import numpy as np
# Input parameters
L      = 1e-2     # Length in meters
D      = 1e-3     # Diameter in meters
E      = 1.429e6  # Youngs Modulus in Pa
Mr     = 52e3     # Remanent magnetisation in A/m
alpha  = 90        # Angle between moment and rod axis
N      = 20       # Number of nodes (= number of segments + 1)

filename = "Rod.csv"
header_text ="""\
# Rod definition
# description : straight rod length 1 cm, magnetisation perpendicular to rod
# created     : 2026-10-16 by Leon Abelmann
# program     : GenerateSimpleRod.py
# units       : s [m], D [m], E [Pa], Mr [A/m], alpha [rad]
s, D, E, Mr, alpha
"""

s = np.linspace(0, L, N)

np.savetxt(filename,
           np.column_stack([s, D*np.ones_like(s),
                            E*np.ones_like(s), Mr*np.ones_like(s),
                            alpha*np.ones_like(s)]),
           delimiter=",", fmt="%.6e",
           header=header_text, comments="")
