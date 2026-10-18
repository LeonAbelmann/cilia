####################################################################
# MagneticTorque.py
#
# Computes the quasi-static equilibrium shape of a hard-magnetic
# elastic rod in a single, fixed uniform
# magnetic field (magnitude B, angle phi), and compares the
# numerical result with the analytical small-deflection solution.
#
# Physics:
#   A thin elastic rod is clamped vertically at its base. Its
#   remanent magnetisation Mr gives a magnetic torque per unit
#   length  w = Mr * A * B * sin(theta - phi)  that tries to align
#   the rod with the applied field. At equilibrium the bending
#   moment balances the magnetic torque:
#
#       EI * theta'' = w * sin(theta - phi)
#       theta(0) = 0      (clamped base)
#       M(L) = 0          (moment-free tip)
#
#   solved as a first-order system in (theta, M):
#       theta' = -M / EI
#       M'     = -w * sin(theta - phi)
#
#   The initial guess is the straight rod (theta = 0, M = 0),
#   so the solution found is the branch connected to the unloaded
#   state. Valid for fields where this branch is stable: at high
#   fields (w*L^2/EI >> 1) the physical solution may snap to a
#   different state that this script cannot find.
#
#   Analytical benchmark (small deflections, sin(theta - phi)
#   approximated by theta - phi and arc length s ~ y):
#       theta(s) = (w/EI) * (L*s - s^2/2)
#       x(s)    = (w/EI) * (L*s^2/2 - s^3/6)
#   Agreement with the numerical solution validates the BVP.
#
# Output:
#   - Plot of the numerical rod shape (x, y) in mm, together with
#     the analytical small-deflection shape.
#   - Saved to MagneticTorque.pdf.
#
# Units: SI throughout (m, Pa, T, A/m).
####################################################################
import numpy as np
from numpy import pi as pi
from scipy.integrate import solve_bvp
from scipy.integrate import cumulative_trapezoid as cumtrapz
import matplotlib.pyplot as plt


# Input parameters
L   = 1e-2     # Length in meters
D   = 1e-3     # Diameter in meters
E   = 1.429e6  # Youngs Modulus in Pa
Mr  = 52e3     # Remanent magnetisation in A/m
B   = 0.02      # Applied magnetic field in T
phi = pi/2     # Angle of applied field in rad, phi = 0 is vertical

EI = E*(pi*D**4)/64      # Flexural rigidity for a long thin cylinder
w  = (Mr*pi*(D/2)**2)*B  # Maximum torque per unit length (N/m)

# ODE system
def ode(s, y):
    theta, M = y
    dtheta_ds = -M / EI
    dM_ds = -w * np.sin(theta - phi)
    return np.array([dtheta_ds, dM_ds])

# Boundary conditions
def bc(ya, yb):
    return np.array([ya[0], yb[1]])  # theta(0) = 0, M(L) = 0

# Initial guess
s = np.linspace(0, L, 100)
theta_guess = np.zeros_like(s)
M_guess = np.zeros_like(s)
y_guess = np.array([theta_guess, M_guess])

# Solve the ODE system
sol = solve_bvp(ode, bc, s, y_guess, tol=1e-6, max_nodes=1000)

# Extract theta(s) and M(s)
s_plot = np.linspace(0, L, 100)
theta_s = sol.sol(s_plot)[0]
M_s = sol.sol(s_plot)[1]

# Compute x(s) and y(s) by integration
x_s = cumtrapz(np.sin(theta_s), s_plot, initial=0)
y_s = cumtrapz(np.cos(theta_s), s_plot, initial=0)

# Analytical solution for small deflections
theta_analytical = (w / EI) * (L * s_plot - s_plot**2 / 2)
x_analytical = (w / EI) * (L * s_plot**2 / 2 - s_plot**3 / 6)
y_analytical = s_plot  # y(s) = s for small deflections

# Plot both solutions
plt.figure(figsize=(8, 6))
plt.plot(1000 * x_s, 1000 * y_s, label='Numerical', linewidth=2)
plt.plot(1000 * x_analytical, 1000 * y_analytical, '--', label='Analytical (small deflection)', linewidth=2)
plt.xlabel('x [mm]')
plt.ylabel('y [mm]')
plt.title('Shape of Cylinder under Magnetic Torque')
plt.axis('equal')
plt.grid(True)
plt.legend()
plt.savefig('MagneticTorque.pdf', format='pdf', dpi=200, bbox_inches='tight')
#plt.show()

