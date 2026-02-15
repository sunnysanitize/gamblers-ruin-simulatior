from __future__ import annotations

import numpy as np

from .analytics import (
    absolute_convergence_error,
    average_steps,
    estimated_goal_probability,
    estimator_variance_decay,
    probability_convergence,
    ruin_count,
    success_count,
    theoretical_goal_probability,
)
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
    target_config_results: list[dict[str, float | int]] | None = None,
):
    convergence = probability_convergence(result)
    theoretical_probability = theoretical_goal_probability(start_money, goal, win_probability)
    absolute_error = absolute_convergence_error(result, theoretical_probability)
    variance_decay = estimator_variance_decay(result)
    success_steps = result.steps[result.success]
    fail_steps = result.steps[~result.success]

    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            "Sample Bankroll Paths",
            "Estimated Probability Convergence",
            "Absolute Error to Closed Form",
            "Variance Decay of Estimator",
            "Duration Distribution",
            "Outcome Breakdown",
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "histogram"}, {"type": "pie"}],
        ],
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

    fig.add_trace(
        go.Scatter(
            x=np.arange(1, len(convergence) + 1),
            y=convergence,
            mode="lines",
            name="Estimated P(reach goal)",
            line=dict(color="royalblue", width=3),
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=np.arange(1, len(convergence) + 1),
            y=np.full(len(convergence), theoretical_probability),
            mode="lines",
            name="Closed-form P(reach goal)",
            line=dict(color="darkorange", width=2, dash="dash"),
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Scatter(
            x=np.arange(1, len(absolute_error) + 1),
            y=absolute_error,
            mode="lines",
            name="|Empirical - Closed-form|",
            line=dict(color="firebrick", width=2),
        ),
        row=2,
        col=1,
    )
    fig.add_hline(y=0.01, row=2, col=1, line_dash="dot", line_color="gray")
    fig.add_hline(y=0.02, row=2, col=1, line_dash="dot", line_color="lightgray")

    fig.add_trace(
        go.Scatter(
            x=np.arange(1, len(variance_decay) + 1),
            y=variance_decay,
            mode="lines",
            name="Estimated Var(p-hat)",
            line=dict(color="purple", width=2),
        ),
        row=2,
        col=2,
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
        row=3,
        col=2,
    )

    if len(success_steps) > 0:
        fig.add_trace(
            go.Histogram(
                x=success_steps,
                name="Reached Goal",
                opacity=0.6,
                marker_color="seagreen",
                nbinsx=40,
            ),
            row=3,
            col=1,
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
            row=3,
            col=1,
        )

    est_prob = estimated_goal_probability(result)
    avg_steps = average_steps(result)
    final_error = abs(est_prob - theoretical_probability)

    extra_title = ""
    if target_config_results:
        labels = ", ".join(
            f"goal={int(item['goal'])}: emp={item['empirical']:.3f}, th={item['theoretical']:.3f}"
            for item in target_config_results
        )
        extra_title = f"<br><sup>Target configurations: {labels}</sup>"

    fig.update_layout(
        title=(
            "Gambler's Ruin Monte Carlo Dashboard"
            f"<br><sup>start={start_money}, goal={goal}, p(win)={win_probability:.3f}, "
            f"trials={len(result.success):,}, empirical={est_prob:.4f}, closed-form={theoretical_probability:.4f}, "
            f"error={final_error:.4f}, avg steps={avg_steps:.1f}</sup>"
            f"{extra_title}"
        ),
        template="plotly_white",
        height=1100,
        bargap=0.05,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )

    fig.update_xaxes(title_text="Step", row=1, col=1)
    fig.update_yaxes(title_text="Money", row=1, col=1)
    fig.update_xaxes(title_text="Trial Number", row=1, col=2)
    fig.update_yaxes(title_text="Probability", range=[0, 1], row=1, col=2)
    fig.update_xaxes(title_text="Trial Number", row=2, col=1)
    fig.update_yaxes(title_text="Absolute Error", row=2, col=1)
    fig.update_xaxes(title_text="Sample Size", row=2, col=2)
    fig.update_yaxes(title_text="Variance", row=2, col=2)
    fig.update_xaxes(title_text="Number of Steps", row=3, col=1)
    fig.update_yaxes(title_text="Frequency", row=3, col=1)

    return fig
