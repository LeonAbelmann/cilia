import numpy as np
from numpy import pi as pi
from scipy.integrate import solve_bvp, cumtrapz
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

# Plot the shape
# plt.plot(1000*x_s, 1000*y_s, label='Numerical')
# plt.xlabel('x [mm]')
# plt.ylabel('y [mm]')
# plt.axis('equal')
# plt.grid(True)
# plt.legend()
# # Save the plot
# plt.savefig('MagneticTorque.pdf', format='pdf')
# # plt.show()
