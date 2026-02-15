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


def theoretical_goal_probability(start_money: int, goal: int, win_probability: float) -> float:
    if start_money <= 0 or goal <= start_money:
        raise ValueError("Require 0 < start_money < goal")
    if not (0.0 <= win_probability <= 1.0):
        raise ValueError("win_probability must be in [0, 1]")

    if win_probability == 0.0:
        return 0.0
    if win_probability == 1.0:
        return 1.0

    if np.isclose(win_probability, 0.5):
        return start_money / goal

    loss_probability = 1.0 - win_probability
    ratio = loss_probability / win_probability
    numerator = 1.0 - ratio**start_money
    denominator = 1.0 - ratio**goal
    return numerator / denominator


def absolute_convergence_error(result: SimulationResult, theoretical_probability: float) -> np.ndarray:
    return np.abs(probability_convergence(result) - theoretical_probability)


def estimator_variance_decay(result: SimulationResult) -> np.ndarray:
    running_p = probability_convergence(result)
    sample_sizes = np.arange(1, len(result.success) + 1)
    return running_p * (1.0 - running_p) / sample_sizes
