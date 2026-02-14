from __future__ import annotations

import numpy as np

from .analytics import average_steps, estimated_goal_probability, probability_convergence, ruin_count, success_count
from .models import SimulationResult

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError as exc:
    raise SystemExit("Missing dependency: plotly. Install it with: pip install plotly") from exc


def build_figure(
    result: SimulationResult,
    start_money: int,
    goal: int,
    win_probability: float,
):
    convergence = probability_convergence(result)
    success_steps = result.steps[result.success]
    fail_steps = result.steps[~result.success]

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Sample Bankroll Paths",
            "Duration Distribution",
            "Estimated Probability Convergence",
            "Outcome Breakdown",
        ),
        specs=[[{"type": "scatter"}, {"type": "histogram"}], [{"type": "scatter"}, {"type": "pie"}]],
    )

    for i, path in enumerate(result.sample_paths, start=1):
        fig.add_trace(
            go.Scatter(
                x=np.arange(len(path)),
                y=path,
                mode="lines",
                name=f"Path {i}",
                opacity=0.85,
                line=dict(width=2),
            ),
            row=1,
            col=1,
        )

    fig.add_hline(y=0, row=1, col=1, line_dash="dot", line_color="crimson")
    fig.add_hline(y=goal, row=1, col=1, line_dash="dot", line_color="seagreen")

    if len(success_steps) > 0:
        fig.add_trace(
            go.Histogram(
                x=success_steps,
                name="Reached Goal",
                opacity=0.6,
                marker_color="seagreen",
                nbinsx=40,
            ),
            row=1,
            col=2,
        )
    if len(fail_steps) > 0:
        fig.add_trace(
            go.Histogram(
                x=fail_steps,
                name="Ruined",
                opacity=0.6,
                marker_color="crimson",
                nbinsx=40,
            ),
            row=1,
            col=2,
        )

    fig.add_trace(
        go.Scatter(
            x=np.arange(1, len(convergence) + 1),
            y=convergence,
            mode="lines",
            name="Estimated P(reach goal)",
            line=dict(color="royalblue", width=3),
        ),
        row=2,
        col=1,
    )

    wins = success_count(result)
    losses = ruin_count(result)
    fig.add_trace(
        go.Pie(
            labels=["Reached Goal", "Ruined"],
            values=[wins, losses],
            marker=dict(colors=["seagreen", "crimson"]),
            textinfo="label+percent",
            hole=0.35,
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    est_prob = estimated_goal_probability(result)
    avg_steps = average_steps(result)

    fig.update_layout(
        title=(
            "Gambler's Ruin Monte Carlo Dashboard"
            f"<br><sup>start={start_money}, goal={goal}, p(win)={win_probability:.3f}, "
            f"trials={len(result.success):,}, estimated P(goal)={est_prob:.4f}, avg steps={avg_steps:.1f}</sup>"
        ),
        template="plotly_white",
        height=900,
        bargap=0.05,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )

    fig.update_xaxes(title_text="Step", row=1, col=1)
    fig.update_yaxes(title_text="Money", row=1, col=1)
    fig.update_xaxes(title_text="Number of Steps", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=1, col=2)
    fig.update_xaxes(title_text="Trial Number", row=2, col=1)
    fig.update_yaxes(title_text="Estimated Probability", range=[0, 1], row=2, col=1)

    return fig
