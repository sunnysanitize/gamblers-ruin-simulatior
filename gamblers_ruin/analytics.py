from __future__ import annotations

import numpy as np

from .models import SimulationResult


def estimated_goal_probability(result: SimulationResult) -> float:
    return float(result.success.mean())


def average_steps(result: SimulationResult) -> float:
    return float(result.steps.mean())


def success_count(result: SimulationResult) -> int:
    return int(result.success.sum())


def ruin_count(result: SimulationResult) -> int:
    return int((~result.success).sum())


def probability_convergence(result: SimulationResult) -> np.ndarray:
    return np.cumsum(result.success) / np.arange(1, len(result.success) + 1)
