from __future__ import annotations

from gamblers_ruin.analytics import theoretical_goal_probability
from gamblers_ruin.cli import parse_args, validate_args
from gamblers_ruin.dashboard import build_dashboard
from gamblers_ruin.simulation import run_gamblers_ruin
from gamblers_ruin.webapp import serve_dashboard


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
    theoretical_prob = theoretical_goal_probability(args.start, args.goal, args.p)
    abs_error = abs(estimated_prob - theoretical_prob)

    print(f"Estimated probability of reaching goal: {estimated_prob:.6f}")
    print(f"Closed-form probability of reaching goal: {theoretical_prob:.6f}")
    print(f"Absolute error: {abs_error:.6f}")
    print(f"Dashboard written to: {args.output.resolve()}")

    if args.no_serve:
        return

    serve_dashboard(
        host=args.host,
        port=args.port,
        open_browser=not args.no_open_browser,
        default_start=args.start,
        default_goal=args.goal,
        default_p=args.p,
        default_trials=args.trials,
        default_paths=args.paths,
        default_target_goals=args.target_goals,
    )


if __name__ == "__main__":
    main()
