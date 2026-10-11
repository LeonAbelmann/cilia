####################################################################
# MagneticTorqueSeries.py
#
# Computes the quasi-static equilibrium shapes of a hard-magnetic
# elastic rod under a rotating uniform
# magnetic field (constant magnitude Bval, angle sweeping from 0
# to 2*pi in N steps), and renders them as an animation.
#
# Physics:
#   A thin elastic rod is clamped vertically at its base. Its
#   remanent magnetisation Mr gives a magnetic torque per unit
#   length  w = Mr * A * B * sin(theta - phi)  that tries to align
#   the rod with the applied field. At each field angle the
#   equilibrium satisfies the elastica BVP
#
#       EI * theta'' = w * sin(theta - phi)
#       theta(0) = 0      (clamped base)
#       M(L) = 0          (moment-free tip)
#
#   solved as a first-order system in (theta, M) with
#   scipy.integrate.solve_bvp.
#
#   Continuation:
#   - Each solve is seeded with the solution of the PREVIOUS
#     field angle. This lets the solver track the smooth branch
#     of solutions as the field rotates, rather than rediscovering
#     an arbitrary equilibrium from a generic guess each time.
#   - The seed from the previous step keeps the rod's bending
#     direction (left/right) consistent, so at low fields the
#     animation shows the rod continuously tracking the field.
#
#   Validity (IMPORTANT):
#   - Strictly quasi-static: no inertia, no damping, no time.
#     The animation is a sequence of equilibrium states, not a
#     dynamics simulation; the field rotation rate has no
#     physical meaning here.
#   - Use at LOW fields only. When a field step crosses a fold
#     instability (a branch turning point), the previous-solution
#     seed can no longer track the physical branch: the solver
#     either fails or silently jumps to the wrong branch, and the
#     animation shows unphysical behaviour. For higher fields use
#     MagneticTorqueDampingSeries.py, which simulates the
#     overdamped dynamics and handles the snap-through correctly.
#
# Output:
#   - Shapes (x(s), y(s)) per field step; tip trajectory.
#   - Animation of the rod, field arrow, and tip trajectory,
#     saved to MagneticTorqueAnimation.mp4.
#
# Units: SI throughout (m, Pa, T, A/m).
####################################################################

import numpy as np
from numpy import pi as pi
from scipy.integrate import solve_bvp
from scipy.integrate import cumulative_trapezoid as cumtrapz
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Input parameters
L   = 1e-2     # Length in meters
D   = 1e-3     # Diameter in meters
E   = 1.429e6  # Young's Modulus in Pa
Mr  = 52e3     # Remanent magnetisation in A/m

EI = E*(pi*D**4)/64      # Flexural rigidity for a long thin cylinder

# List of applied fields: [B, phi], phi in rad, phi = 0 is vertical

# For example manually entered
# B_list = [[0.02, 0], [0.02, pi/12], [0.02, 2*pi/12], [0.02, 3*pi/12],
#           [0.02, 4*pi/12], [0.02, 5*pi/12], [0.02, pi/2]]

# Generated: constant magnitude, angle rotating 0 to 2*pi in N steps
Bval = 0.05
N = 100
B_list = [[Bval, 2*pi*n/N] for n in range(N)]

# ODE system (B and phi passed via closure/default args)
def make_ode(B, phi):
    w = (Mr * pi * (D/2)**2) * B
    def ode(s, y):
        theta, M = y
        dtheta_ds = -M / EI
        dM_ds = -w * np.sin(theta - phi)
        return np.array([dtheta_ds, dM_ds])
    return ode

def bc(ya, yb):
    return np.array([ya[0], yb[1]])  # theta(0) = 0, M(L) = 0

# Common s grid
s_grid = np.linspace(0, L, 200)

# Store shapes and fields for the animation
shapes = []
fields = []

# Initial state: theta(s) = 0 everywhere, M(s) = 0
theta_guess = np.zeros_like(s_grid)
M_guess = np.zeros_like(s_grid)
y_guess = np.array([theta_guess, M_guess])

for B, phi in B_list:
    ode = make_ode(B, phi)
    sol = solve_bvp(ode, bc, s_grid, y_guess, tol=1e-6, max_nodes=5000)

    if not sol.success:
        print(f"Warning: solver did not converge for B={B:.3f} T, phi={phi:.3f} rad")

    theta_s = sol.sol(s_grid)[0]
    x_s = cumtrapz(np.sin(theta_s), s_grid, initial=0)
    y_s = cumtrapz(np.cos(theta_s), s_grid, initial=0)
    shapes.append((x_s, y_s))
    fields.append((B, phi))

    # Use the current solution as initial guess for the next field
    y_guess = sol.sol(s_grid)

# Calculate the tip positions
tips = np.array([[x_s[-1], y_s[-1]] for x_s, y_s in shapes])
    
# --- Animation ---
fig, ax = plt.subplots(figsize=(8, 6))
line, = ax.plot([], [], 'b-', linewidth=2, label='Numerical')
title = ax.set_title('')

ax.set_xlabel('x [mm]')
ax.set_ylabel('y [mm]')
ax.set_aspect('equal', adjustable='box')
ax.grid(True)
# ax.legend(loc='lower left')

# Fixed axis limits based on all shapes
x_max = max(1000*x.max() for x, y in shapes)
x_min = min(1000*x.min() for x, y in shapes)
y_max = max(1000*y.max() for x, y in shapes)
ax.set_xlim(min(x_min, -0.1*x_max) - 1, max(x_max, 1) + 1)
ax.set_ylim(-1, y_max + 1)

# Indicate tip trajectory
tip_line, = ax.plot([], [], 'r--', linewidth=1, alpha=0.6,
                    label='Tip trajectory')

# Add an error indicating the field
# Scale: arrow length in mm per tesla (tune to taste)
arrow_scale = 1.0  # mm per T... adjust below for mT
arrow_mm = 1.0     # base arrow length in mm

# Create the arrow once; it will be updated every frame
arrow = ax.annotate(
    '', xy=(0, 1), xytext=(0, 1),
    xycoords='data',
    arrowprops=dict(arrowstyle='-|>', color='red', lw=2)
)

def update(frame):
    x_s, y_s = shapes[frame]
    B, phi = fields[frame]
    line.set_data(1000*x_s, 1000*y_s)
    title.set_text(f'B = {B*1000:.0f} mT, phi = {phi*180/pi:.0f} deg')

    # Show entire tip trajectory
    tip_line.set_data(1000*tips[:, 0], 1000*tips[:, 1])
    
    # Field arrow in lower-left corner, length proportional to B
    x0 = 0    # corner position
    y0 = (ax.get_ylim()[1] + ax.get_ylim()[0])/2 # ymin + 0.5*(ymax - ymin)
    dx = B/0.02 * arrow_mm * np.sin(phi)   # field direction: phi=0 -> vertical
    dy = B/0.02 * arrow_mm * np.cos(phi)   # phi=pi/2 -> horizontal (+x)
    arrow.xyann = (x0, y0)      # tail of the arrow
    arrow.xy = (x0 + dx, y0 + dy)  # head of the arrow

    return line, title, arrow, tip_line


ani = animation.FuncAnimation(fig, update, frames=len(shapes),
                              interval=2000/N, blit=True)

# Save as MP4 (requires ffmpeg installed in the Binder image)
ani.save('MagneticTorqueAnimation.mp4', writer='ffmpeg', fps=N/2)

plt.show()
