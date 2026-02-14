from __future__ import annotations

from pathlib import Path

from .models import SimulationResult
from .visualization import build_figure


def build_dashboard(
    result: SimulationResult,
    start_money: int,
    goal: int,
    win_probability: float,
    output_file: Path,
) -> None:
    figure = build_figure(
        result=result,
        start_money=start_money,
        goal=goal,
        win_probability=win_probability,
    )
    figure.write_html(str(output_file), include_plotlyjs="cdn", full_html=True)
