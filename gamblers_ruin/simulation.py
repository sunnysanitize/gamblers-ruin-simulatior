from __future__ import annotations

import numpy as np

from .models import SimulationResult


def run_gamblers_ruin(
    start_money: int,
    goal: int,
    win_probability: float,
    trials: int,
    num_paths_to_capture: int,
) -> SimulationResult:
    success = np.zeros(trials, dtype=bool)
    steps = np.zeros(trials, dtype=int)
    sample_paths: list[np.ndarray] = []

    for trial in range(trials):
        money = start_money
        trajectory = [money]
        count = 0

        while 0 < money < goal:
            money += 1 if np.random.random() < win_probability else -1
            count += 1
            if trial < num_paths_to_capture:
                trajectory.append(money)

        success[trial] = money == goal
        steps[trial] = count

        if trial < num_paths_to_capture:
            sample_paths.append(np.array(trajectory))

    return SimulationResult(success=success, steps=steps, sample_paths=sample_paths)
