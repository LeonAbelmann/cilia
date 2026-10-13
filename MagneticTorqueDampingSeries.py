####################################################################
# MagneticTorqueDampingSeries.py
#
# Simulates the dynamic response of a hard-magnetic elastic rod to a
# rotating uniform magnetic field, and renders the result as an animation.
#
# Physics:
#   A thin elastic rod is clamped vertically at its base. Its
#   remanent magnetisation Mr gives a magnetic torque per unit
#   length  w = Mr * A * B * sin(theta - phi)  that tries to align
#   the rod with the applied field (magnitude Bval, angle phi(t),
#   rotating once around in T seconds). The rod bends against its
#   flexural rigidity EI.
#
#   The angle of the magnetic moment with respect to the rod axis is
#   defined by alpha, and can vary along the rod
#
#   Instead of solving the quasi-static elastica BVP (which has
#   fold instabilities where the solver must "jump branches"),
#   we simulate the overdamped dynamics
#
#     gamma * dtheta/dt = EI * theta'' - w*sin(theta - phi(t) + alpha)
#
#   This is gradient descent on the rod's energy: between folds
#   the rod relaxes to the (quasi-)static equilibria, and at the
#   instability the transition emerges naturally as a fast but
#   continuous motion. 
#
#   gamma (rotational drag per unit length) is chosen ~1e-4 of
#   the frame spacing time so that the rod is quasi-static between
#   snapshots; it is a numerical/visual choice, not a measured
#   drag coefficient.
#
# Numerics:
#   - theta(s) discretised on n finite-difference nodes; clamp
#     theta(0)=0 built into the stencil, free end theta'(L)=0
#     via a ghost node.
#   - angle_nodes(s) angle of moment at the discretized points
#   - Time integration with scipy's implicit BDF (stiff solver).
#
# Output:
#   - Prints the relaxation time vs. frame spacing (sanity check).
#   - Shapes (x(s), y(s)) per frame; tip trajectory.
#   - Animation of the rod, field arrow, and tip trajectory,
#     saved to MagneticTorqueAnimation.mp4.
#
# Units: SI throughout (m, Pa, T, A/m, s).
####################################################################
import numpy as np
from numpy import pi as pi
from scipy.integrate import solve_ivp
from scipy.integrate import cumulative_trapezoid as cumtrapz
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import imageio_ffmpeg
import matplotlib
matplotlib.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()

# Input parameters
L      = 1e-2     # Length in meters
D      = 1e-3     # Diameter in meters
E      = 1.429e6  # Youngs Modulus in Pa
Mr     = 52e3     # Remanent magnetisation in A/m

# Applied Field:
# constant magnitude Bval, angle rotating 0 to 2*pi in N steps
# in time T
Bval = 0.1 # T
N    = 400
T    = 60  # s, time for one rotation of the field

# Field angle as a function of time: one full revolution in T seconds
def phi_of_t(t):
    return 2*pi * t / T

# Discretisation of rod
# s_grid[0] = clamp (theta = 0, not a state),
# s_grid[1:] = n unknown theta values, last one at s = L (free end).
n      = 100
s_grid = np.linspace(0, L, n+1)
ds = s_grid[1] - s_grid[0]

# Angle of magnetic moment along the rod, s=0 is the base (fixed)
# s=L is the free end.
def angle(s,L):
    angle = 2*pi*(s/L)
    return angle

# calculate alpha(s) at the n unknown nodes (s = ds ... L); 
alpha_nodes = angle(s_grid[1:], L) 


# Help function to calculate second derivative of theta
# Note theta(0) = 0 (clamped end)
#      theta'(L) = 0 (free end)
def theta_double_prime(theta):
    d2 = np.empty_like(theta)
    d2[0]    = (theta[1] - 2*theta[0]) / ds**2
    d2[1:-1] = (theta[2:] - 2*theta[1:-1] + theta[:-2]) / ds**2
    # ghost: theta(L+ds)=theta(L-ds)
    d2[-1]   = 2*(theta[-2] - theta[-1]) / ds**2 
    return d2

# Setup of model with differential equation
# gamma * dtheta/dt = EI * theta'' - w*sin(theta - phi(t))
# parameters
EI = E*(pi*D**4)/64           # Flexural rigidity for a long thin cylinder
w_max = (Mr*pi*(D/2)**2)*Bval # magnetic torque per unit length

# We included damping to gracefully simulate switching of
# the rod at high fields
characteristic_time = (T/N)/(ds**2/EI)
gamma = 1e-4*characteristic_time  # rotational drag per unit length (N.s)

# Sanity check
print('relaxation time:', gamma*ds**2/EI, 's') 
print('frame spacing:', T/N, 's')

# Differential equation itself
def de(t, theta):
    phi = phi_of_t(t)
    elasticterm = EI*theta_double_prime(theta)
    torqueterm  = w_max*np.sin(theta - phi + alpha_nodes)
    dampedterm  = ( elasticterm - torqueterm) / gamma
    return dampedterm


# --- Time integration: one sweep from t=0 to t=T ---
theta0 = np.zeros(n)           # initial state: straight rod
t_eval = np.linspace(0, T, N)  # time sample points

sol = solve_ivp(de, (0, T), theta0, method='BDF',
                t_eval=t_eval, rtol=1e-4, atol=1e-6)

if not sol.success:
    print(f"Warning: time integration failed: {sol.message}")

# --- Build shapes, fields and times for the animation ---
shapes, fields, times = [], [], []
for k, t in enumerate(sol.t):
    theta_full = np.concatenate(([0.0], sol.y[:, k]))
    x_s = cumtrapz(np.sin(theta_full), s_grid, initial=0)
    y_s = cumtrapz(np.cos(theta_full), s_grid, initial=0)
    shapes.append((x_s, y_s))
    fields.append((Bval, phi_of_t(t)))
    times.append(t)

# Calculate the tip positions
tips = np.array([[x_s[-1], y_s[-1]] for x_s, y_s in shapes])

# ----------------------------- Animation --------------------------
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
tip_line, = ax.plot([], [], 'r.', markersize=2, alpha=0.6,
                    label='Tip trajectory')

# Add an arrow indicating the field
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
    t = times[frame]
    line.set_data(1000*x_s, 1000*y_s)
    title.set_text(f't = {t:.2f} s,  B = {B*1000:.0f} mT,  '
                   f'phi = {phi*180/pi:.0f} deg')
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
ani.save('MagneticTorqueAnimation.mp4', writer='ffmpeg', fps=int(N/2))

plt.show()
