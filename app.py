from __future__ import annotations

from pathlib import Path

import streamlit as st

from gamblers_ruin.analytics import average_steps, estimated_goal_probability, ruin_count, success_count
from gamblers_ruin.dashboard import build_dashboard
from gamblers_ruin.simulation import run_gamblers_ruin
from gamblers_ruin.visualization import build_figure


st.set_page_config(page_title="Gambler's Ruin Simulator", layout="wide")

st.title("Gambler's Ruin Simulator")
st.caption("Interactive Monte Carlo simulation with live plots and downloadable HTML dashboard.")

with st.sidebar:
    st.header("Parameters")
    start_money = st.number_input("Starting bankroll", min_value=1, value=500, step=1)
    goal = st.number_input("Goal bankroll", min_value=int(start_money + 1), value=max(1000, int(start_money + 1)), step=1)
    win_probability = st.slider("Win probability", min_value=0.0, max_value=1.0, value=0.5, step=0.001)
    trials = st.number_input("Trials", min_value=1, value=10000, step=100)
    paths = st.number_input("Sample paths", min_value=0, max_value=int(trials), value=min(30, int(trials)), step=1)
    output_name = st.text_input("Export HTML filename", value="gamblers_ruin_dashboard.html")

run = st.button("Run Simulation", type="primary", use_container_width=True)

if run:
    result = run_gamblers_ruin(
        start_money=int(start_money),
        goal=int(goal),
        win_probability=float(win_probability),
        trials=int(trials),
        num_paths_to_capture=int(paths),
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Estimated P(reach goal)", f"{estimated_goal_probability(result):.4f}")
    metric_cols[1].metric("Average steps", f"{average_steps(result):,.1f}")
    metric_cols[2].metric("Reached goal", f"{success_count(result):,}")
    metric_cols[3].metric("Ruined", f"{ruin_count(result):,}")

    fig = build_figure(
        result=result,
        start_money=int(start_money),
        goal=int(goal),
        win_probability=float(win_probability),
    )
    st.plotly_chart(fig, use_container_width=True)

    output_path = Path(output_name)
    build_dashboard(
        result=result,
        start_money=int(start_money),
        goal=int(goal),
        win_probability=float(win_probability),
        output_file=output_path,
    )

    with output_path.open("rb") as f:
        st.download_button(
            label="Download HTML dashboard",
            data=f.read(),
            file_name=output_path.name,
            mime="text/html",
            use_container_width=True,
        )

    st.success(f"Saved dashboard to {output_path.resolve()}")
else:
    st.info("Set parameters in the sidebar and click Run Simulation.")
