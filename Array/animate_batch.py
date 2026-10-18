# animate_batch.py
"""Animate a carpet of rods from a carpet layout CSV.

Usage: python animate_batch.py carpet.csv
   or: from animate_batch import animate_batch; animate_batch('carpet.csv')

Layout: '# key : value' header, then rows 'x [mm], y [mm], result_file'.
The same result file may appear on multiple rows (drawn at each position).
All listed results must share the same time grid (validated at load).
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from animate_simulation import reconstruct_shape   
from animate_simulation import load_simulation     

from fields import FieldSequence

import imageio_ffmpeg

    

def load_layout(filename):
    """Parse carpet layout: meta dict + list of (x_mm, y_mm, result_file)."""
    meta, rows = {}, []
    with open(filename) as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith('#'):
                text = line.lstrip('#').strip()
                if ':' in text:
                    key, value = text.split(':', 1)
                    meta[key.strip()] = value.strip()
                continue
            if s.replace(' ', '').startswith('x,y,'):
                continue                       # column header row
            parts = [p.strip() for p in s.split(',')]
            if len(parts) != 3:
                raise ValueError(f"layout row needs 3 fields (x, y, file): {s!r}")
            rows.append((float(parts[0]), float(parts[1]), parts[2]))
    if not rows:
        raise ValueError(f"layout {filename} contains no rods")
    return meta, rows


def animate_batch(layout_file='carpet.csv', interval_ms=75):
    """Animate all rods declared in the layout, side by side."""
    meta, rows = load_layout(layout_file)

    # --- Load each unique result file once, cache by filename ---
    cache = {}
    t_ref = None
    for x_mm, y_mm, result_file in rows:
        if result_file not in cache:
            sim = load_simulation(result_file)
            if t_ref is None:
                t_ref = sim['t']
            elif not np.allclose(sim['t'], t_ref):
                raise ValueError(
                    f"{result_file} has a different time grid than the "
                    "other results; carpet frames must share times")
            cache[result_file] = sim

    # --- Precompute all shapes (per result file): (n_frames, n_nodes+1) ---
    shapes = {}
    for fname, sim in cache.items():
        s_nodes = sim['s_nodes']
        n_frames = len(sim['t'])
        sx = np.empty((n_frames, len(s_nodes) + 1))
        sy = np.empty((n_frames, len(s_nodes) + 1))
        for k in range(n_frames):
            sx[k], sy[k] = reconstruct_shape(sim['theta'][k], s_nodes)
        shapes[fname] = (sx, sy)

    # --- Field: taken from the result files' own provenance ---
    first_sim = next(iter(cache.values()))
    field_file = first_sim['meta'].get('field file')
    if not field_file:
        raise ValueError("result files carry no '# field file :' header; "
                         "cannot draw the field arrow")
    field = FieldSequence(field_file)

    # cross-check: all results must share the same field file
    for fname, sim in cache.items():
        if sim['meta'].get('field file') != field_file:
            raise ValueError(f"{fname} used a different field than "
                             f"{field_file}; carpet must share one field")


    # --- Figure ---
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True)
    ax.set_title(f"{layout_file} - {meta.get('description', '')}",
                 fontsize=9)

    # one line object per layout row (so repeats get their own line)
    lines = []
    for x_mm, y_mm, fname in rows:
        line, = ax.plot([], [], 'b-', lw=2)
        lines.append((line, x_mm, y_mm, fname))

    # --- Axis limits: from all shapes at all positions, with margin ---
    all_x, all_y = [], []
    for x_mm, y_mm, fname in rows:
        sx, sy = shapes[fname]
        all_x.append(1000 * sx.min() + x_mm)
        all_x.append(1000 * sx.max() + x_mm)
        all_y.append(1000 * sy.min() + y_mm)
        all_y.append(1000 * sy.max() + y_mm)
    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)
    margin = 5.0                                     # mm
    ax.set_xlim(x_min - margin, x_max + margin)
    ax.set_ylim(min(y_min, -1) - margin, max(y_max, 1) + margin)

    time_text = ax.text(0.02, 0.02, '', transform=ax.transAxes)

    n_frames = len(t_ref)

    # arrow to indicate field direction and strength
    arrow_mm = 20.0
    # Arrow position, color etc.
    arrow = ax.annotate('', xy=(0, 0), xytext=(0, 0), xycoords='data',
                        arrowprops=dict(arrowstyle='-|>', color='red', lw=2))
    
    def update(k):
        artists = [time_text]
        for line, x_mm, y_mm, fname in lines:
            sx, sy = shapes[fname]
            line.set_data(x_mm + 1000 * sx[k], y_mm + 1000 * sy[k])
            artists.append(line)
        time_text.set_text(f"t = {t_ref[k]:.2f} s")

        # Field arrow
        x0 = (ax.get_xlim()[1] + ax.get_xlim()[0])/2
        y0 = (ax.get_ylim()[1] + ax.get_ylim()[0])/2
        B_k   = field.B(t_ref[k])
        phi_k = field.phi(t_ref[k])
        dx = (B_k/0.1) * arrow_mm * np.sin(phi_k)
        dy = (B_k/0.1) * arrow_mm * np.cos(phi_k)
        arrow.xyann = (x0, y0)
        arrow.xy = (x0 + dx, y0 + dy)
        artists.append(arrow)
        return artists

    ani = animation.FuncAnimation(fig, update, frames=n_frames,
                                  interval=interval_ms, blit=True)
    plt.show()

    # Save as MP4 
    ani.save('batch.mp4', writer='ffmpeg', fps=10)

    return ani


def main():
    layout = sys.argv[1] if len(sys.argv) > 1 else 'carpet.csv'
    animate_batch(layout)


if __name__ == '__main__':
    main()
