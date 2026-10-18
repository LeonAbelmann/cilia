# run_simulation.py
"""Run one simulation: field file + rod file -> simulation_NNN.csv

Output format:
  - '#' metadata lines (provenance: input files, parameters, versions)
  - column row: t, theta_1, ..., theta_n   (theta at nodes s = ds..L)
  - one row per output time; theta = 0 at the clamp is implied (not stored)
Usage:
  python run_simulation.py
"""

import os
import glob
import datetime
import numpy as np
from fields import FieldSequence
from rods import RodDescription
from simulator import simulate
from settings import DEFAULT as settings
from output import write_output


# Input files
FIELD_FILE = 'Constant_50mT.csv'
ROD_FILE   = 'Rod_90.csv'

# Output file
def next_simulation_filename(directory='.'):
    """simulation_NNN.csv with NNN one above the highest existing number."""
    numbers = []
    for path in glob.glob(os.path.join(directory, 'simulation_*.csv')):
        stem = os.path.splitext(os.path.basename(path))[0]
        try:
            numbers.append(int(stem.split('_')[1]))
        except (IndexError, ValueError):
            continue          # not our naming scheme; ignore
    next_number = max(numbers, default=-1) + 1
    return os.path.join(directory, f'simulation_{next_number:03d}.csv')


def main():
    # --- Load inputs ---
    field = FieldSequence(FIELD_FILE)
    rod   = RodDescription(ROD_FILE)

    # --- Run ---
    result = simulate(field, rod, settings)

    # --- Write output to file ----
    write_output(result, field, rod, settings,
                 program='run_simulation.py') # This file
    
if __name__ == '__main__':
    main()
