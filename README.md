# Magnetic Cilia Simulation

Simulates the bending of a hard-magnetic elastic rod (an artificial
cilium) under a uniform magnetic field. The rod is clamped at its
base; its remanent magnetisation experiences a torque that tries to
align it with the applied field, working against the rod's flexural
rigidity. The equilibrium (or dynamic) shapes are computed by solving
the elastica equation numerically.

## The Programs
   Notebook | Description |
 |---|---|
 | `MagneticTorque.ipynb` | Equilibrium shape in a single fixed field, compared against the analytical small-deflection solution. |
 | `MagneticTorqueSeries.ipynb` | Quasi-static shapes under a rotating field, tracked by continuation. **Low fields only**  - beyond the fold instability the quasi-static branch becomes unstable. |
 | `MagneticTorqueDampingSeries.ipynb` | Time simulation of the overdamped rod under a rotating field. Handles the snap-through (fold) instabilities at high fields naturally; valid at all field strengths. |

Typical progression: use `MagneticTorque` to validate against the
analytical benchmark, `MagneticTorqueSeries` for low-field rotating
fields, and `MagneticTorqueDampingSeries` when the field is strong
enough that the rod snaps between states.

## How to Run
You can run the notebooks directly in your browser:

### Using Binder

- [MagneticTorque](https://mybinder.org/v2/gh/LeonAbelmann/cilia/main?filepath=MagneticTorque.ipynb) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/LeonAbelmann/cilia/main?filepath=MagneticTorque.ipynb)
- [MagneticTorqueSeries](https://mybinder.org/v2/gh/LeonAbelmann/cilia/main?filepath=MagneticTorqueSeries.ipynb) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/LeonAbelmann/cilia/main?filepath=MagneticTorqueSeries.ipynb)
- [MagneticTorqueDampingSeries](https://mybinder.org/v2/gh/LeonAbelmann/cilia/main?filepath=MagneticTorqueDampingSeries.ipynb) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/LeonAbelmann/cilia/main?filepath=MagneticTorqueDampingSeries.ipynb)

### Using Google Colab

- [MagneticTorque](https://colab.research.google.com/github/LeonAbelmann/cilia/blob/main/MagneticTorque.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/LeonAbelmann/cilia/blob/main/MagneticTorque.ipynb)
- [MagneticTorqueSeries](https://colab.research.google.com/github/LeonAbelmann/cilia/blob/main/MagneticTorqueSeries.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/LeonAbelmann/cilia/blob/main/MagneticTorqueSeries.ipynb)
- [MagneticTorqueDampingSeries](https://colab.research.google.com/github/LeonAbelmann/cilia/blob/main/MagneticTorqueDampingSeries.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/LeonAbelmann/cilia/blob/main/MagneticTorqueDampingSeries.ipynb)

## Requirements
- Python 3.x
- Libraries: `numpy`, `scipy`, `matplotlib` (automatically installed in Binder/Colab)

## Notes
- All units are SI (m, Pa, T, A/m, s).
- The animation notebooks save an MP4; this requires `ffmpeg`,
  which is available in Binder and Colab by default.
