# settings.py
"""Simulation settings, shared by all runners."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationSettings:
    gamma_ratio: float = 1e-4
    rtol: float = 1e-6
    atol: float = 1e-8

    # Check values
    def __post_init__(self):
        if self.gamma_ratio <= 0:
            raise ValueError(f"gamma_ratio must be > 0, got {self.gamma_ratio}")
        if self.rtol <= 0 or self.atol <= 0:
            raise ValueError(f"tolerances must be > 0, got rtol={self.rtol}, atol={self.atol}")

# Default settings
DEFAULT = SimulationSettings()
