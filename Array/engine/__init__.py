# engine/__init__.py
"""Simulation engine for hard-magnetic rod carpets.

Users normally don't import this directly -- use the tools/ scripts.
"""
from .fields import FieldSequence
from .rods import RodDescription
from .simulator import simulate, relax_to_equilibrium
from .settings import SimulationSettings, DEFAULT
from .output import write_output
