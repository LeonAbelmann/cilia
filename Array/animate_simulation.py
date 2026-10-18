# animate_simulation.py
"""Animate a simulation_NNN.csv result file.

Reconstructs the rod shape from theta(s,t) and animates it, with the
external field direction drawn as an arrow. The field CSV is re-loaded
(its filename is recorded in the result file header) purely to draw the
field; the physics data all comes from the result file.

Usage:
  python animate_simulation.py [simulation_000.csv]
"""

import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from fields import FieldSequence

import imageio_ffmpeg


SIM_FILE = 'simulation_000.csv'

def load_simulation(filename):
    """Parse a simulation_NNN.csv into a dict with metadata + arrays."""
    meta = {}
    t, theta = [], []
    s_nodes = None
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                text = line.lstrip('#').strip()
                if ':' in text:
                    key, value = text.split(':', 1)
                    key, value = key.strip(), value.strip()
                    if key.startswith('s_nodes'):
                        s_nodes = np.array(
                            [float(v) for v in value.split(',')])
                    else:
                        meta[key] = value
                continue
            if line.startswith('t,'):
                continue          # column-name row
            parts = [float(v) for v in line.split(',')]
            t.append(parts[0])
            theta.append(parts[1:])

    if s_nodes is None:
        raise ValueError(f"No '# s_nodes' line found in {filename} "
                         "-- cannot reconstruct shapes")
    if len(t) == 0:
        raise ValueError(f"No data rows found in {filename}")

    return {'meta': meta,
            't': np.array(t),
            'theta': np.array(theta),      # (n_frames, n_nodes)
            's_nodes': s_nodes}

def reconstruct_shape(theta_frame, s_nodes):
    """theta at nodes -> x(s), y(s) by cumulative trapezoid integration.

    Clamp at origin, rod initially along +y (theta = angle from y axis).
    """
    # include the clamp: theta=0 at s=0
    th = np.concatenate(([0.0], np.asarray(theta_frame)))
    s = np.concatenate(([0.0], s_nodes))
    dxds = np.sin(th)
    dyds = np.cos(th)
    x = np.concatenate(([0.0], np.cumsum(0.5*(dxds[1:] + dxds[:-1])
                                         * np.diff(s))))
    y = np.concatenate(([0.0], np.cumsum(0.5*(dyds[1:] + dyds[:-1])
                                         * np.diff(s))))
    return x, y


def main():
    sim = load_simulation(SIM_FILE)
    t = sim['t']
    theta = sim['theta']
    s_nodes = sim['s_nodes']
    meta = sim['meta']

    print("Metadata:")
    for key in ('created', 'field file', 'field desc', 'rod file',
                'rod desc', 'gamma', 'solver'):
        if key in meta:
            print(f"  {key:12s}: {meta[key]}")

    # --- Field for the direction arrow ---
    field = None
    field_file = meta.get('field file')
    try:
        field = FieldSequence(field_file)
    except Exception as e:
        print(f"(field file '{field_file}' not loadable: {e} -- "
              f"arrow disabled)")

    # --- Figure setup ---
    L = float(meta.get('rod L [m]', '0.01'))
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-L, L)
    ax.set_ylim(-0.2*L, 1.4*L)
    ax.set_aspect('equal')
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.grid(True)
    title = f"{meta.get('rod file', '?')} in {meta.get('field file', '?')}"
    ax.set_title(title, fontsize=10)
    ax.set_title(title)

    rod_line, = ax.plot([], [], 'b-', lw=3)
    field_arrow = ax.annotate('', xy=(0, 0), xytext=(0, 0),
                              arrowprops=dict(color='red', width=2,
                                              headwidth=8))
    time_text = ax.text(0.02, 0.97, '', transform=ax.transAxes)

    # --- Precompute all shapes: (n_frames, n_nodes+1) arrays ---
    n_frames = len(t)
    x_s = np.empty((n_frames, len(s_nodes) + 1))
    y_s = np.empty((n_frames, len(s_nodes) + 1))
    for k in range(n_frames):
        x_s[k], y_s[k] = reconstruct_shape(theta[k], s_nodes)
    
    # Calculate and show the tip positions
    tips = np.column_stack([x_s[:, -1], y_s[:, -1]]) #(n_frames, 2)
    tip_line, = ax.plot([], [], 'r.', markersize=2, alpha=0.6,
                    label='Tip trajectory')

    def update(k):
        #x, y = reconstruct_shape(theta[k], s_nodes)
        rod_line.set_data(x_s[k], y_s[k])
        time_text.set_text(f"t = {t[k]:.2f} s")
        if field is not None:
            phi = field.phi(t[k])
            # arrow anchored at the clamp, length ~ half the rod
            r = 0.2*L
            field_arrow.set_position((0, 0.8*L))
            field_arrow.xy = (r*np.sin(phi), 0.8*L + r*np.cos(phi))
        # Show entire tip trajectory
        tip_line.set_data(tips[:, 0], tips[:, 1])

        return rod_line, time_text, tip_line

    ani = animation.FuncAnimation(fig, update, frames=len(t),
                                  interval=30, blit=False)
    plt.show()
    
    # Save as MP4 
    ani.save('animation.mp4', writer='ffmpeg', fps=int(N/2))
    
    return ani   # keep a reference so the animation isn't garbage-collected


if __name__ == '__main__':
    ani = main()
