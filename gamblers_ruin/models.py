from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class SimulationResult:
    success: np.ndarray
    steps: np.ndarray
    sample_paths: list[np.ndarray]
