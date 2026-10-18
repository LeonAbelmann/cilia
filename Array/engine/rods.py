# rods.py
"""RodDescription: loads a hard-magnetic cilium description from a
self-describing CSV file and provides the simulator with the
quantities it needs on its internal node grid.

File format:
  - '#' lines at the top: metadata (description, created, program, units)
  - one column-name row:  s, D, E, Mr, alpha
  - data rows: s [m], D [m], E [Pa], Mr [A/m], alpha [rad]
    (s from 0 (clamp) to L (tip), strictly increasing)

Physics derived here (per unit length):
  EI(s)  = E * pi * D^4 / 64          flexural rigidity
  w(s,t) = Mr * pi*(D/2)^2 * B(t)     magnetic torque prefactor
  alpha(s)                              moment angle wrt rod axis
"""

import numpy as np
from scipy.interpolate import CubicSpline
import os


class RodDescription:

    def __init__(self, filename):
        self.filename = filename
        self.file = os.path.basename(filename)
        self.metadata = {}
        s, D, E, Mr, alpha = [], [], [], [], []
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    self._parse_metadata(line)
                    continue
                if line.replace(' ', '').lower().startswith('s,d'):
                    continue                      # column-name row
                parts = line.split(',')
                s.append(float(parts[0]))
                D.append(float(parts[1]))
                E.append(float(parts[2]))
                Mr.append(float(parts[3]))
                alpha.append(float(parts[4]))
        self._s = np.array(s)
        self._D = np.array(D)
        self._E = np.array(E)
        self._Mr = np.array(Mr)
        self._alpha = np.array(alpha)
        self._validate()

        # Interpolants in s (cubic: same smoothness argument as the field)
        self._D_spline     = CubicSpline(self._s, self._D)
        self._E_spline    = CubicSpline(self._s, self._E)
        self._Mr_spline   = CubicSpline(self._s, self._Mr)
        self._alpha_spline = CubicSpline(self._s, self._alpha)

    def _parse_metadata(self, line):
        text = line.lstrip('#').strip()
        if ':' in text:
            key, value = text.split(':', 1)
            self.metadata[key.strip()] = value.strip()
        else:
            self.metadata.setdefault('title', text)

    def _validate(self):
        if len(self._s) < 4:
            raise ValueError("Need at least 4 sample points")
        if self._s[0] != 0.0:
            raise ValueError("s must start at 0 (clamped base)")
        if np.any(np.diff(self._s) <= 0):
            raise ValueError("s must be strictly increasing")
        if np.any(self._D <= 0):
            raise ValueError("D must be > 0 everywhere")
        if np.any(self._E <= 0):
            raise ValueError("E must be > 0 everywhere")
        # Sanity check on the grid
        ds_file = np.diff(self._s)
        mean_ds = ds_file.mean()
        if np.any(np.abs(ds_file - mean_ds) > 0.01 * mean_ds):
            raise ValueError(
                "rod s samples must be (approximately) equidistant; "
                "this file's spacings vary by more than 1%")
        # exact uniform grid, immune to rounding in the file:
        self.n_nodes = len(self._s) - 1
        self.L = self._s[-1]
        self.ds = self.L / self.n_nodes
        self.s_nodes = self.ds * np.arange(1, self.n_nodes + 1)


    def samples(self):
        """Raw sample arrays: (s, D, E, Mr, alpha)."""
        return (self._s, self._D, self._E, self._Mr, self._alpha)

    # --- quantities on an arbitrary s grid (the simulator's nodes) ---
    def EI(self, s):
        """Flexural rigidity EI(s) [N.m^2]."""
        return self._E_spline(s) * np.pi * self._D_spline(s)**4 / 64

    def w_prefactor(self, s):
        """Magnetic torque prefactor Mr*A [A/m * m^2]; multiply by B(t)."""
        return (self._Mr_spline(s)
                * np.pi * (self._D_spline(s)/2)**2)

    def alpha(self, s):
        """Magnetisation angle alpha(s) [rad]."""
        return self._alpha_spline(s)

    @property
    def description(self):
        """Human-readable description from
        the file's '# description :' line."""
        return self.metadata.get('description', '')
