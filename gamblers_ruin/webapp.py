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
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 1.5rem; color: #121212; background: #f8fafc; }
    h1 { margin: 0 0 0.25rem 0; }
    .sub { margin: 0 0 1rem 0; color: #425466; }
    form { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.75rem; margin-bottom: 1rem; background: #fff; padding: 1rem; border-radius: 10px; }
    label { display: flex; flex-direction: column; font-size: 0.85rem; color: #3a4451; }
    input { margin-top: 0.25rem; padding: 0.45rem; border: 1px solid #d9dee5; border-radius: 8px; }
    button { grid-column: 1 / -1; padding: 0.6rem; border-radius: 8px; border: 0; background: #0f6bff; color: #fff; font-weight: 600; cursor: pointer; }
    .error { background: #ffe3e3; color: #7d1a1a; padding: 0.65rem; border-radius: 8px; margin-bottom: 1rem; }
    .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); gap: 0.75rem; margin-bottom: 1rem; }
    .card { background: #fff; padding: 0.75rem; border-radius: 10px; border: 1px solid #e7ebf0; }
    .card b { display: block; font-size: 1.2rem; margin-top: 0.2rem; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; background: #fff; border-radius: 10px; overflow: hidden; }
    th, td { padding: 0.6rem; border-bottom: 1px solid #ecf0f4; text-align: left; }
    th { background: #f2f6fc; font-weight: 600; }
  </style>
</head>
<body>
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
    {{ figure_html|safe }}
  {% endif %}
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
            figure_html = figure.to_html(include_plotlyjs="cdn", full_html=False)
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
