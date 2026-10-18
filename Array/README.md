# Array — magnetic cilia carpets

This part simulates one or many hard-magnetic elastic rods ("artificial
cilia") under a uniform, time-varying magnetic field, and animates the
resulting motion, including carpets of rods acting in concert.

## The physics

A slender elastic rod (length L ~ 10 mm, diameter ~ 1 mm) is clamped
upright at its base. It carries a remanent magnetisation Mr, in a material
with Young's modulus E. An external field **B**(t) = B(t)·(sin φ(t),
cos φ(t)) exerts a torque on the magnetisation, which bends the rod
against its flexural rigidity.

Each rod is described in the overdamped limit

    γ · ∂θ/∂t = ∂/∂s( EI(s) · θ' ) − Mr(s)·A(s)·B(t) · sin(θ + α(s) − φ(t))

where s is arclength, θ(s,t) the angle of the rod axis with the vertical,
EI(s) the flexural rigidity, A(s) the cross-section, and α(s) the angle of
the magnetisation relative to the rod axis. Boundary conditions:
θ(0,t) = 0 (clamped base) and θ'(L,t) = 0 (free tip).

γ is a damping coefficient chosen for numerical stability (γ_ratio × the
relaxation time per node spacing), not a physical viscosity: the rod is
always slower than the field, so it follows the field's stable attractor.

### Why dynamics, not statics

Quasi-static (continuation) solutions of the elastica exist, but beyond a
critical field strength the branch folds and becomes unstable — the rod
snaps through. Simulating the overdamped *dynamics* handles these fold
instabilities naturally: the rod simply follows its stable attractor in
time. (The legacy `Single/` notebooks demonstrate the same physics and
the failure of the quasi-static approach.)

### Initial condition

Each simulation starts from the rod's equilibrium under the field frozen
at t = 0 (found by relaxing the dynamics under the frozen field), so the
animation shows the physically meaningful response to the field sweep.

### Carpets

Many rods are simulated independently (a manifest lists rod files and
result files) and then animated side by side at chosen x-positions
(a layout file lists positions and results). Because all rods feel the
same field, this reproduces metachronal-wave-like behaviour of magnetic
cilia carpets — the collective effect is emergent from the phase relation
between rods, not imposed.

## Architecture
   Directory | Role |
 |-----------|------|
 | `engine/` | The library: loaders (`fields`, `rods`), solver (`simulator`), writer (`output`), settings. Not user-facing. |
 | `tools/`  | Programs: input generators, runners, animators, displays. |
 | `notebook/` | Experiments: one folder per experiment, containing inputs, `Simulate.py`/`Animate.py` wrappers, and results. |

All data files are self-describing CSVs: `# key : value` metadata
headers (units in the key, bare values) followed by a column-name row and
data rows. Every result file records its provenance — rod file, field
file, settings, manifest — so any result can be traced to its inputs.

