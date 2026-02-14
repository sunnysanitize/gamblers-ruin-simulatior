from __future__ import annotations

import platform
import subprocess
from pathlib import Path

from gamblers_ruin.cli import parse_args, validate_args
from gamblers_ruin.dashboard import build_dashboard
from gamblers_ruin.simulation import run_gamblers_ruin


def open_in_browser(path: Path) -> bool:
    resolved = path.resolve()

    system = platform.system()
    if system == "Darwin":
        command = ["open", str(resolved)]
    elif system == "Windows":
        command = ["cmd", "/c", "start", "", str(resolved)]
    else:
        command = ["xdg-open", str(resolved)]

    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return completed.returncode == 0
    except Exception:
        return False


def main() -> None:
    args = parse_args()
    validate_args(args)

    result = run_gamblers_ruin(
        start_money=args.start,
        goal=args.goal,
        win_probability=args.p,
        trials=args.trials,
        num_paths_to_capture=min(args.paths, args.trials),
    )

    build_dashboard(
        result=result,
        start_money=args.start,
        goal=args.goal,
        win_probability=args.p,
        output_file=args.output,
    )

    estimated_prob = float(result.success.mean())
    print(f"Estimated probability of reaching goal: {estimated_prob:.6f}")
    print(f"Dashboard written to: {args.output.resolve()}")

    if args.open_browser:
        if open_in_browser(args.output):
            print("Opened dashboard in your default browser.")
        else:
            print("Could not auto-open browser. Open the HTML file manually.")


if __name__ == "__main__":
    main()
