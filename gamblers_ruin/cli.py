from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive Gambler's Ruin simulator")
    parser.add_argument("--start", type=int, default=500, help="Starting bankroll")
    parser.add_argument("--goal", type=int, default=1000, help="Goal bankroll")
    parser.add_argument("--p", type=float, default=0.5, help="Probability of winning each round")
    parser.add_argument("--trials", type=int, default=10000, help="Number of Monte Carlo trials")
    parser.add_argument(
        "--paths",
        type=int,
        default=30,
        help="How many full bankroll paths to draw in the dashboard",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the dashboard in your default browser after generation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("gamblers_ruin_dashboard.html"),
        help="Output HTML dashboard path",
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
    if args.paths < 0:
        raise SystemExit("--paths cannot be negative")
