from __future__ import annotations

import platform
import subprocess
import threading

try:
    from flask import Flask, render_template_string, request
except ImportError as exc:
    raise SystemExit("Missing dependency: flask. Install it with: pip install flask") from exc

from .analytics import estimated_goal_probability, theoretical_goal_probability
from .simulation import run_gamblers_ruin
from .visualization import build_figure

PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Gambler's Ruin Simulator</title>
  <style>
    :root {
      --bg: #f8fafc;
      --fg: #121212;
      --muted: #425466;
      --panel: #ffffff;
      --line: #e7ebf0;
      --accent: #0f6bff;
      --radius: 12px;
    }
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      color: var(--fg);
      background: var(--bg);
    }
    .shell {
      width: min(1100px, 100%);
      margin: 0 auto;
      padding: 1rem;
    }
    h1 { margin: 0 0 0.25rem 0; font-size: clamp(1.35rem, 3.5vw, 2rem); line-height: 1.2; }
    .sub { margin: 0 0 1rem 0; color: var(--muted); font-size: 0.95rem; }
    form {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 0.75rem;
      margin-bottom: 1rem;
      background: var(--panel);
      padding: 0.9rem;
      border-radius: var(--radius);
      border: 1px solid var(--line);
    }
    label { display: flex; flex-direction: column; font-size: 0.85rem; color: #3a4451; min-width: 0; }
    input {
      width: 100%;
      margin-top: 0.25rem;
      padding: 0.55rem 0.6rem;
      border: 1px solid #d9dee5;
      border-radius: 8px;
      font-size: 0.95rem;
      min-width: 0;
    }
    button {
      grid-column: 1 / -1;
      padding: 0.7rem;
      border-radius: 8px;
      border: 0;
      background: var(--accent);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
      font-size: 0.95rem;
    }
    .error { background: #ffe3e3; color: #7d1a1a; padding: 0.65rem; border-radius: 8px; margin-bottom: 1rem; }
    .metrics {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 0.75rem;
      margin-bottom: 1rem;
    }
    .card {
      background: var(--panel);
      padding: 0.75rem;
      border-radius: var(--radius);
      border: 1px solid var(--line);
      min-width: 0;
    }
    .card b { display: block; font-size: clamp(1rem, 3vw, 1.2rem); margin-top: 0.2rem; word-break: break-word; }
    .table-wrap {
      width: 100%;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      margin-bottom: 1rem;
    }
    table { width: 100%; min-width: 520px; border-collapse: collapse; }
    th, td { padding: 0.6rem; border-bottom: 1px solid #ecf0f4; text-align: left; white-space: nowrap; }
    th { background: #f2f6fc; font-weight: 600; }
    .figure-wrap {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 0.4rem;
      overflow: hidden;
    }
    .figure-wrap .plotly-graph-div {
      width: 100% !important;
      max-width: 100% !important;
    }
    @media (max-width: 700px) {
      .shell { padding: 0.75rem; }
      form { grid-template-columns: 1fr; gap: 0.65rem; }
      .metrics { grid-template-columns: 1fr 1fr; }
      table { min-width: 460px; }
    }
    @media (max-width: 460px) {
      .metrics { grid-template-columns: 1fr; }
      .sub { font-size: 0.9rem; }
    }
  </style>
</head>
<body>
  <div class="shell">
  <h1>Gambler's Ruin Simulation</h1>
  <p class="sub">Monte Carlo vs closed-form theory, convergence diagnostics, and variance decay.</p>

  {% if error %}
    <div class="error">{{ error }}</div>
  {% endif %}

  <form method="get">
    <label>Start bankroll
      <input type="number" min="1" name="start" value="{{ params.start }}" required>
    </label>
    <label>Goal bankroll
      <input type="number" min="2" name="goal" value="{{ params.goal }}" required>
    </label>
    <label>Win probability p
      <input type="number" min="0" max="1" step="0.001" name="p" value="{{ params.p }}" required>
    </label>
    <label>Trials (max 100000)
      <input type="number" min="1" max="100000" name="trials" value="{{ params.trials }}" required>
    </label>
    <label>Sample paths
      <input type="number" min="0" name="paths" value="{{ params.paths }}" required>
    </label>
    <label>Target goals (comma-separated)
      <input type="text" name="target_goals" value="{{ params.target_goals }}">
    </label>
    <button type="submit">Run Simulation</button>
  </form>

  {% if metrics %}
    <div class="metrics">
      <div class="card">Empirical P(reach goal)<b>{{ metrics.empirical }}</b></div>
      <div class="card">Closed-form P(reach goal)<b>{{ metrics.theoretical }}</b></div>
      <div class="card">Absolute error<b>{{ metrics.error }}</b></div>
      <div class="card">Trials<b>{{ metrics.trials }}</b></div>
    </div>
    <div class="table-wrap">
    <table>
      <thead>
        <tr><th>Goal</th><th>Empirical</th><th>Closed-form</th><th>Absolute Error</th></tr>
      </thead>
      <tbody>
        {% for row in target_rows %}
          <tr>
            <td>{{ row.goal }}</td>
            <td>{{ row.empirical }}</td>
            <td>{{ row.theoretical }}</td>
            <td>{{ row.error }}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
    </div>
    <div class="figure-wrap">{{ figure_html|safe }}</div>
  {% endif %}
  </div>
  <script>
    (function () {
      function fitPlotlyHeight() {
        var graph = document.querySelector(".figure-wrap .plotly-graph-div");
        if (!graph || typeof Plotly === "undefined") return;
        var isMobile = window.matchMedia("(max-width: 700px)").matches;
        var targetHeight = isMobile ? 1450 : 1100;
        Plotly.relayout(graph, {height: targetHeight});
      }
      window.addEventListener("resize", fitPlotlyHeight);
      window.addEventListener("load", fitPlotlyHeight);
      setTimeout(fitPlotlyHeight, 250);
    })();
  </script>
</body>
</html>
"""


def _open_target(target: str) -> bool:
    system = platform.system()
    if system == "Darwin":
        commands = [["open", target]]
    elif system == "Windows":
        commands = [
            ["powershell", "-NoProfile", "-Command", f"Start-Process '{target}'"],
            ["cmd", "/c", "start", "", target],
        ]
    else:
        commands = [["xdg-open", target], ["gio", "open", target]]

    for command in commands:
        try:
            completed = subprocess.run(
                command,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if completed.returncode == 0:
                return True
        except Exception:
            continue

    return False


def _open_target_with_notice(target: str) -> None:
    if _open_target(target):
        print(f"Opened browser at: {target}")
    else:
        print(f"Auto-open failed. Open this URL manually: {target}")


def _parse_target_goals(raw: str, start: int, goal: int) -> list[int]:
    if not raw.strip():
        inferred = {max(start + 1, int(round(goal * 0.75))), goal, int(round(goal * 1.25))}
        return sorted(inferred)

    values: list[int] = []
    for part in raw.split(","):
        token = part.strip()
        if not token:
            continue
        val = int(token)
        if val <= start:
            continue
        values.append(val)
    if not values:
        raise ValueError("At least one valid target goal must be greater than start bankroll.")
    return sorted(set(values))


def _run_target_configurations(
    start_money: int,
    goals: list[int],
    win_probability: float,
    trials: int,
) -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    for configured_goal in goals:
        scenario_result = run_gamblers_ruin(
            start_money=start_money,
            goal=configured_goal,
            win_probability=win_probability,
            trials=trials,
            num_paths_to_capture=0,
        )
        empirical = estimated_goal_probability(scenario_result)
        theoretical = theoretical_goal_probability(start_money, configured_goal, win_probability)
        rows.append(
            {
                "goal": configured_goal,
                "empirical": empirical,
                "theoretical": theoretical,
                "error": abs(empirical - theoretical),
            }
        )
    return rows


def serve_dashboard(
    host: str,
    port: int,
    open_browser: bool,
    default_start: int,
    default_goal: int,
    default_p: float,
    default_trials: int,
    default_paths: int,
    default_target_goals: str,
) -> None:
    app = Flask(__name__)

    @app.get("/")
    def index():
        params = {
            "start": request.args.get("start", str(default_start)),
            "goal": request.args.get("goal", str(default_goal)),
            "p": request.args.get("p", str(default_p)),
            "trials": request.args.get("trials", str(default_trials)),
            "paths": request.args.get("paths", str(default_paths)),
            "target_goals": request.args.get("target_goals", default_target_goals),
        }

        error = ""
        metrics: dict[str, str] | None = None
        target_rows: list[dict[str, str]] = []
        figure_html = ""

        try:
            start_money = int(params["start"])
            goal = int(params["goal"])
            win_probability = float(params["p"])
            trials = int(params["trials"])
            paths = int(params["paths"])

            if start_money <= 0:
                raise ValueError("Start bankroll must be > 0.")
            if goal <= start_money:
                raise ValueError("Goal bankroll must be greater than start bankroll.")
            if not (0.0 <= win_probability <= 1.0):
                raise ValueError("Win probability must be between 0 and 1.")
            if trials <= 0 or trials > 100000:
                raise ValueError("Trials must be between 1 and 100000.")
            if paths < 0:
                raise ValueError("Sample paths must be >= 0.")

            target_goals = _parse_target_goals(params["target_goals"], start_money, goal)
            target_config_results = _run_target_configurations(
                start_money=start_money,
                goals=target_goals,
                win_probability=win_probability,
                trials=trials,
            )

            main_result = run_gamblers_ruin(
                start_money=start_money,
                goal=goal,
                win_probability=win_probability,
                trials=trials,
                num_paths_to_capture=min(paths, trials),
            )
            empirical = estimated_goal_probability(main_result)
            theoretical = theoretical_goal_probability(start_money, goal, win_probability)
            abs_error = abs(empirical - theoretical)

            metrics = {
                "empirical": f"{empirical:.4f}",
                "theoretical": f"{theoretical:.4f}",
                "error": f"{abs_error:.4f}",
                "trials": f"{trials:,}",
            }
            target_rows = [
                {
                    "goal": f"{int(item['goal'])}",
                    "empirical": f"{item['empirical']:.4f}",
                    "theoretical": f"{item['theoretical']:.4f}",
                    "error": f"{item['error']:.4f}",
                }
                for item in target_config_results
            ]

            figure = build_figure(
                result=main_result,
                start_money=start_money,
                goal=goal,
                win_probability=win_probability,
                target_config_results=target_config_results,
            )
            figure_html = figure.to_html(
                include_plotlyjs="cdn",
                full_html=False,
                config={"responsive": True, "displaylogo": False},
                default_width="100%",
            )
        except (TypeError, ValueError) as exc:
            error = str(exc)

        return render_template_string(
            PAGE_TEMPLATE,
            params=params,
            error=error,
            metrics=metrics,
            target_rows=target_rows,
            figure_html=figure_html,
        )

    dashboard_url = f"http://{host}:{port}"
    if open_browser:
        threading.Timer(0.8, _open_target_with_notice, args=[dashboard_url]).start()

    print(f"Serving dashboard at: {dashboard_url}")
    print("Press Ctrl+C to stop the server.")
    app.run(host=host, port=port, debug=False, use_reloader=False)
