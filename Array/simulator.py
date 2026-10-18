# simulator.py
"""Simulates the overdamped dynamics of a hard-magnetic elastic rod
(an artificial cilium) under an external field sequence.

    gamma * dtheta/dt = d/ds( EI(s) * theta' )
                        - Mr(s)*A(s)*B(t) * sin(theta + alpha(s) - phi(t))

BCs: theta(0) = 0 (clamped base), theta'(L) = 0 (free tip, ghost node).
Time integration: implicit BDF (stiff solver), since gamma makes the
problem stiff by design (relaxation << field variation).

Outputs theta(s_i, t_k) on the node grid at the requested frames;
shape reconstruction (x, y) is a cheap deterministic post-step that
lives in the animator, not here.
"""

import numpy as np
from scipy.integrate import solve_ivp


def elastic_operator(EI_nodes):
    """Build the conservative discrete operator d/ds(EI * theta').

    Returns a function theta -> d/ds(EI theta') on the n interior
    nodes (s = ds..L), using midpoint EI values. For constant EI this
    reduces EXACTLY to the classic (1, -2, 1)/ds^2 stencil.
    """
    EI = np.asarray(EI_nodes)
    n = len(EI)
    ds_store = None  # set at first call together with ds

    def operator(theta, ds):
        d2 = np.empty_like(theta)
        # EI at midpoints between neighbouring nodes
        EI_mid = 0.5*(EI[:-1] + EI[1:])           # length n-1

        # clamp node (s=ds): ghost theta(0)=0 is the clamp itself
        d2[0] = (EI_mid[0]*(theta[1] - theta[0])
                 - EI_mid[0]*theta[0]) / ds**2

        # interior nodes i = 1..n-2:
        #   [EI_{i+1/2}(th_{i+1}-th_i) - EI_{i-1/2}(th_i-th_{i-1})]/ds^2
        d2[1:-1] = (EI_mid[1:]*(theta[2:] - theta[1:-1])
                    - EI_mid[:-1]*(theta[1:-1] - theta[:-2])) / ds**2

        # tip node (s=L): ghost theta(L+ds) = theta(L-ds) => theta'(L)=0
        d2[-1] =   (EI_mid[-1]*(theta[-2] - theta[-1]) * 2.0) / ds**2

        return d2

    return operator

def relax_to_equilibrium(field, s_nodes, ds, EI_nodes, w_nodes,
                          alpha_nodes, gamma, settings, t_freeze=0.0):
    """Integrate the dynamics under the field frozen at t_freeze
    until the rod reaches its stable equilibrium (quasi-static attractor).
    """
    dds_elastic = elastic_operator(EI_nodes)

    def rhs_frozen(t, theta):
        B = field.B(t_freeze)
        phi = field.phi(t_freeze)
        elastic = dds_elastic(theta, ds)
        torque = w_nodes * B * np.sin(theta + alpha_nodes - phi)
        return (elastic - torque) / gamma

    # Relaxation time of the rod: gamma*ds^2/EI (per your design rule).
    # Integrate for ~20 relaxation times, then check the residual rate.
    EI_mean = np.mean(EI_nodes)
    tau = gamma * ds**2 / EI_mean
    theta = np.zeros_like(s_nodes)

    for _ in range(50):                      # max 10 retries if not settled
        sol = solve_ivp(rhs_frozen, (0.0, 20*tau), theta, method='BDF',
                        rtol=settings.rtol, atol=settings.atol)
        theta = sol.y[:, -1]
        rate = np.max(np.abs(rhs_frozen(0.0, theta)))
        print(rate, rate*tau, sol.y[-1][-1])
        if rate * tau < 1e-3:                # settled: |dtheta/dt| << 1/tau
            return theta
    raise RuntimeError(
        "pre-relaxation did not converge to a stable equilibrium "
        f"(residual rate {rate:.3e}); check field/rod parameters")


def simulate(field, rod, settings):
    """Integrate one rod under one field sequence.

    Parameters
    ----------
    field   : FieldSequence
    rod     : RodDescription
    settings: SimulationSettings
    
    Returns
    -------
    dict with 't', 'theta' (n_nodes x n_frames), 's_nodes', 'rod', 'field'
    """
    # --- node grid: s = ds..L (n unknowns); clamp at s=0 not a state ---
    L = rod.L
    s_nodes = rod.s_nodes      # interior nodes
    ds = rod.ds

    # --- rod quantities on the node grid ---
    EI_nodes = rod.EI(s_nodes)
    w_nodes  = rod.w_prefactor(s_nodes)               # Mr*A per node
    alpha_nodes = rod.alpha(s_nodes)

    # --- damping: same design rule as the original code ---
    EI_mean = np.mean(EI_nodes)
    frame_time = (field.t[-1] - field.t[0]) / max(len(field.t) - 1, 1)
    characteristic = frame_time / (ds**2 / EI_mean)
    gamma = settings.gamma_ratio * characteristic

    # --- RHS of the overdamped dynamics ---
    dds_elastic = elastic_operator(EI_nodes)

    def rhs(t, theta):
        B = field.B(t)
        phi = field.phi(t)
        elastic = dds_elastic(theta, ds)
        torque = w_nodes * B * np.sin(theta + alpha_nodes - phi)
        return (elastic - torque) / gamma

    # --- time grid ---
    # output times are the field file's sample times
    t_span = (field.t_start, field.t_end)
    t_eval = field.t

    #theta0 = np.zeros_like(s_nodes)        # straight rod
    theta0 = relax_to_equilibrium(field, s_nodes, ds, EI_nodes, w_nodes,
                                 alpha_nodes, gamma, settings,
                                t_freeze=t_span[0])
    sol = solve_ivp(rhs, t_span, theta0, method='BDF',
                    t_eval=t_eval, rtol=settings.rtol, atol=settings.atol)

    if not sol.success:
        raise RuntimeError(f"Integration failed: {sol.message}")

    return {'t': sol.t,
            'theta': sol.y,           # (n_nodes, n_frames)
            's_nodes': s_nodes,
            's_full': np.concatenate(([0.0], s_nodes)),
            'gamma': gamma,
            'rod': rod, 'field': field}
