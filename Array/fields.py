# fields.py
"""FieldSequence: loads a magnetic field sequence from a self-describing
CSV file and provides B(t) and phi(t) to the simulator.

File format:
  - '#' lines at the top: metadata (description, created, program, units)
  - one column-name row:  t, B, phi
  - data rows: t [s], B [T], phi [rad, UNWRAPPED]
"""

import numpy as np
import os
from scipy.interpolate import CubicSpline


class FieldSequence:

    def __init__(self, filename):
        self.filename = filename
        self.file = os.path.basename(filename)
        self.metadata = {}
        t, B, phi = [], [], []
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    self._parse_metadata(line)
                    continue
                if line.replace(' ', '').lower().startswith('t,b'):
                    continue                      # column-name row
                parts = line.split(',')
                t.append(float(parts[0]))
                B.append(float(parts[1]))
                phi.append(float(parts[2]))
        self.t = np.array(t)
        self._B = np.array(B)
        self._phi = np.array(phi)
        self._validate()

        # Interpolants: cubic for smoothness of the torque in time
        self._B_spline   = CubicSpline(self.t, self._B)
        self._phi_spline = CubicSpline(self.t, self._phi)

    def _parse_metadata(self, line):
        text = line.lstrip('#').strip()
        if ':' in text:
            key, value = text.split(':', 1)
            self.metadata[key.strip()] = value.strip()
        else:
            self.metadata.setdefault('title', text)

    def _validate(self):
        if len(self.t) < 4:
            raise ValueError("Need at least 4 sample points for cubic "
                             "interpolation")
        if np.any(np.diff(self.t) <= 0):
            raise ValueError("t must be strictly increasing")
        dphi = np.diff(self._phi)
        if np.any(np.abs(dphi) > np.pi):
            raise ValueError("phi jumps by > pi between samples: is it "
                             "wrapped? Store phi UNWRAPPED (monotonic).")
        if np.any(self._B < 0):
            raise ValueError("B must be >= 0 (direction is in phi)")

    def B(self, t):
        """Field magnitude [T] at time t (scalar or array)."""
        return self._B_spline(t)

    def phi(self, t):
        """Field angle [rad, unwrapped convention] at time t."""
        return self._phi_spline(t)

    @property
    def t_start(self):
        return self.t[0]

    @property
    def t_end(self):
        return self.t[-1]

    @property
    def description(self):
        """Human-readable description
        from the file's '# description :' line."""
        return self.metadata.get('description', '')
