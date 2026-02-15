from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive Gambler's Ruin simulator")
    parser.add_argument("--start", type=int, default=25, help="Starting bankroll")
    parser.add_argument("--goal", type=int, default=50, help="Goal bankroll")
    parser.add_argument("--p", type=float, default=0.5, help="Probability of winning each round")
    parser.add_argument("--trials", type=int, default=20000, help="Number of Monte Carlo trials (max 100000)")
    parser.add_argument(
        "--paths",
        type=int,
        default=20,
        help="How many full bankroll paths to draw in the dashboard",
    )
    parser.add_argument(
        "--target-goals",
        type=str,
        default="",
        help="Comma-separated goals for configuration comparison in Flask dashboard (e.g., 40,50,60)",
    )
    parser.add_argument(
        "--no-open-browser",
        action="store_true",
        help="Do not open the dashboard in your default browser after generation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("gamblers_ruin_dashboard.html"),
        help="Output HTML dashboard path",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host for the Flask dashboard server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port for the Flask dashboard server",
    )
    parser.add_argument(
        "--no-serve",
        action="store_true",
        help="Do not start the Flask dashboard server",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.start <= 0:
        raise SystemExit("--start must be > 0")
    if args.goal <= args.start:
        raise SystemExit("--goal must be greater than --start")
    if not (0.0 <= args.p <= 1.0):
        raise SystemExit("--p must be between 0 and 1")
    if args.trials <= 0:
        raise SystemExit("--trials must be > 0")
    if args.trials > 100000:
        raise SystemExit("--trials must be <= 100000")
    if args.paths < 0:
        raise SystemExit("--paths cannot be negative")
    if args.port <= 0 or args.port > 65535:
        raise SystemExit("--port must be between 1 and 65535")
