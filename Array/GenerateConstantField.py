import numpy as np
T = 60   # s duration of field sequence (one rotation)
B = 0.05 # T, field strenght (constant)
N = 100  # Number of timesteps

filename = "Constant_50mT.csv"
header_text ="""\
# Magnetic field sequence
# description : Uniform rotating field, constant 50 mT, one revolution in 60 s
# created     : 2026-10-16 by Leon Abelmann
# program     : GenerateConstantField.py
# units       : t [s], B [T], phi [rad] (phi = 0 is vertical, unwrapped)
# note        : phi is UNWRAPPED (monotonic); do not wrap before interpolation
t, B, phi
"""

t = np.linspace(0, T, N)

np.savetxt(filename,
           np.column_stack([t, B*np.ones_like(t), 2*np.pi*t/T]),
           delimiter=",", fmt="%.6f",
           header=header_text, comments="")
