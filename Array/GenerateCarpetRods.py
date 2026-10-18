# GenerateCarpetRods.py
"""Generate a family of rod definition files with varying magnetisation
angle alpha. Output files named Rod_<alpha_deg>.csv (alpha in degrees).
"""
import numpy as np
import datetime

# Input parameters
L      = 1e-2     # Length in meters
D      = 1e-3     # Diameter in meters
E      = 1.429e6  # Youngs Modulus in Pa
Mr     = 52e3     # Remanent magnetisation in A/m
N_SAMPLES = 101   # s samples per rod file (simulator uses N_SAMPLES-1 nodes)

# Magnetisation angles: degrees in the filename, radians in the file
alphas_deg = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180,\
              200, 220, 240, 260, 280, 300, 320, 340, 360]
alphas_rad = [np.deg2rad(a) for a in alphas_deg]

s = np.linspace(0, L, N_SAMPLES)

now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

for a_deg, a_rad in zip(alphas_deg, alphas_rad):
    filename = f"Rod_{a_deg:02d}.csv"
    header_text = f"""\
# Rod definition
# description : straight rod, magnetisation at {a_deg} deg to rod axis
# created     : {now} by GenerateCarpetRods.py
# program     : GenerateCarpetRods.py
# units       : s [m], D [m], E [Pa], Mr [A/m], alpha [rad]
s, D, E, Mr, alpha
"""
    np.savetxt(filename,
               np.column_stack([s, D*np.ones_like(s),
                                E*np.ones_like(s), Mr*np.ones_like(s),
                                a_rad*np.ones_like(s)]),
               delimiter=",", fmt="%.6e",
               header=header_text, comments="")
    print(f"Wrote {filename} (alpha = {a_deg} deg)")
