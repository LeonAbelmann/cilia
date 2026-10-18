# Magnetic Cilia Simulation

Simulates hard-magnetic elastic rods (artificial cilia) under uniform
magnetic fields, individually and in arrays ("carpets").

The repository contains two directories:
   Directory | Status | Contents |
 |-----------|--------|----------|
 | `Array/`  | **current** | Simulation of one or many rods from self-describing CSV inputs. Engine + tools + Jupyter-based experiments. Actively developed. |
 | `Single/`  | legacy  | The original single-rod code: equilibrium, quasi-static continuation, and overdamped dynamics notebooks. Superseded by `Array/`, kept for reference. Will be removed. |

**If you are new to the project, go to [`Array/`](Array/README.md).**

`Single/` is retained only because it documents the early exploration and
holds the notebooks from which the current physics was derived. It is not
maintained and will be deleted once `Array/` is fully documented.
