# output.py
"""Write simulation results to CSV in the project's standard format.

Format contract (shared with the readers, e.g. animate_simulation.py):
  - '#' lines: 'key : value' metadata; units in the key, bare
    machine-parsable values.
  - one column-name row: t,theta_1,...,theta_n
  - one data row per output time; theta(s=0)=0 (clamp) implied.
"""
import os
import glob
import datetime
import numpy as np

def next_simulation_filename(directory='.'):
    """simulation_NNN.csv, NNN one above the highest existing number."""
    numbers = []
    for path in glob.glob(os.path.join(directory, 'simulation_*.csv')):
        stem = os.path.splitext(os.path.basename(path))[0]
        try:
            numbers.append(int(stem.split('_')[1]))
        except (IndexError, ValueError):
            continue          # not our naming scheme; ignore
    return os.path.join(directory,
                        f'simulation_{max(numbers, default=-1)+1:03d}.csv')


def write_output(result, field, rod, settings,
                 outfile=None, program='run_simulation.py', manifest=None):
    """Write a result dict from simulate() to a CSV file.

    If outfile is None, the next free simulation_NNN.csv is chosen
    (single-run mode). Batch runners pass an explicit filename.
    Returns the path written.
    """
    # --- Assemble the table: rows = times, columns = nodes ---
    t = result['t']
    theta = result['theta']                    # (n_nodes, n_frames)
    s_nodes = result['s_nodes']
    data = np.column_stack([t, theta.T])       # (n_frames, 1 + n_nodes)

    # --- Provenance header ---
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    col_row = 't,' + ','.join(f'theta_{i+1}' for i in range(len(s_nodes)))
    header_lines = [
        "# Simulation result",
        f"# created     : {now}",
        f"# program     : {program}",
    ]
    if manifest:
        header_lines.append(f"# manifest    : {manifest}")
    header_lines += [
        f"# field file  : {field.file}",
        f"# field desc  : {field.description}",
        f"# rod file    : {rod.file}",
        f"# rod desc    : {rod.description}",
        f"# rod L [m]   : {rod.L:.6e}",
        f"# n_nodes     : {rod.n_nodes} (from {rod.file}; "
        "theta(0)=0 clamp, theta'(L)=0)",
        f"# s_nodes [m] : " + ",".join(f"{s:.6e}" for s in s_nodes),
        f"# gamma [N.s] : {result['gamma']:.6e}",
        f"# gamma_ratio : {settings.gamma_ratio}",
        f"# solver      : BDF, rtol={settings.rtol}, atol={settings.atol}",
        f"# units       : t [s], theta [rad]",
        "# note        : theta(s=0)=0 (clamped) not stored; s values above",
    ]
    header_text = "\n".join(header_lines) + "\n"

    # --- Choose the output filename ---
    if outfile is None:
        outfile = next_simulation_filename()

    # --- Write ---
    np.savetxt(outfile, data, delimiter=",", fmt="%.8e",
               header=header_text, comments="")
    print(f"Wrote {outfile}: {data.shape[0]} frames x {data.shape[1]} columns")

    # Echo the provenance so the console shows what was recorded
    print("\n".join(header_lines))
    return outfile
