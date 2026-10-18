import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_bvp

# Parameters
L = 1.0  # Length in meters
d = 0.005  # Thickness in meters
E = 130e9  # Young's modulus in Pa
rho = 9000  # Density in kg/m3

# Moment of inertia for unit width
I = (1 * d**3) / 12
EI = E * I

# Small deflection analytical solution
def y_small(x, g, L):
    w = rho * g * d
    C = -w / (2 * EI)
    return (C/12) * ((L-x)**4 +4*x*L**3 - L**4)

# Derivative of small deflection solution
def dy_small(x, g, L):
    w = rho * g * d
    C = -w / (2 * EI)
    return (C/12) * (-4*(L-x)**3 +4*L**3)

# ODE for large deflections
def large_deflection_ode(x, y, g):
    y0, y1 = y  # y and dy/dx
    w = rho * g * d
    C = -w / (2 * EI)
    d2y_dx2 = C * (L - x)**2 * (1 + y1**2)**1.5
    return np.array([y1, d2y_dx2])

# Boundary conditions: y(0) = 0, dy/dx(0) = 0
def bc(ya, yb):
    return np.array([ya[0], ya[1]])

# Initial guess using small deflection solution
def initial_guess(x, g, L):
    y_small_vals = y_small(x, g, L)
    dy_small_dx = dy_small(x, g, L)
    return np.array([y_small_vals, dy_small_dx])

# Solve for a given g
def solve_for_g(g_val):
    x = np.linspace(0, L, 100)
    y_guess = initial_guess(x, g_val, L)

    def ode(x, y):
        return large_deflection_ode(x, y, g_val)

    sol = solve_bvp(ode, bc, x, y_guess, tol=1e-6, max_nodes=1000)
    return sol

# Plot for different g values
g_values = [10, 100]  # m/s2

plt.figure(figsize=(10, 6))
for g_val in g_values:
    sol = solve_for_g(g_val)
    x_plot = np.linspace(0, L, 100)
    y_large = sol.sol(x_plot)[0]
    y_small_vals = y_small(x_plot, g_val, L)
    plt.plot(x_plot, y_large, label=f'Large def., g={g_val} m/s^2')
    plt.plot(x_plot, y_small_vals, '--', label=f'Small def., g={g_val} m/s^2')

plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('Deflection of Plate under Gravity')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()
