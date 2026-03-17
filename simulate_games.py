import os
import re
import subprocess
import sys
import argparse
from typing import Tuple


WINNER_PATTERN = re.compile(r"Game finished!\s*Winner:\s*(\w+)")


def run_single_game(
    first_ai: str = "strategic",
    second_ai: str = "basic",
    render: bool = False,
    verbose: bool = False,
    timeout_seconds: int = 90,
) -> str | None:
    """
    Run main.py once as a subprocess and return the winner name ("FIRST"/"SECOND"),
    or None if it could not be determined.
    """
    script_path = os.path.join(os.path.dirname(__file__), "main.py")
    env = os.environ.copy()
    env["FIRST_AI"] = first_ai
    env["SECOND_AI"] = second_ai
    env["RENDER"] = "1" if render else "0"
    env["VERBOSE"] = "1" if verbose else "0"

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return None

    # Combine stdout and stderr for robustness
    output = (result.stdout or "") + "\n" + (result.stderr or "")

    match = WINNER_PATTERN.search(output)
    if match:
        return match.group(1)
    return None


def simulate_games(
    n_games: int = 10,
    first_ai: str = "strategic",
    second_ai: str = "basic",
    render: bool = False,
    verbose: bool = False,
    timeout_seconds: int = 90,
) -> Tuple[int, int, int]:
    """
    Run main.py n_games times and count wins.

    Returns a tuple: (first_wins, second_wins, unknown_results).
    """
    first_wins = 0
    second_wins = 0
    unknown = 0

    for i in range(1, n_games + 1):
        print(f"Starting game {i}/{n_games}...")
        winner = run_single_game(
            first_ai=first_ai,
            second_ai=second_ai,
            render=render,
            verbose=verbose,
            timeout_seconds=timeout_seconds,
        )
        if winner == "FIRST":
            first_wins += 1
            print(f"Game {i}: FIRST won")
        elif winner == "SECOND":
            second_wins += 1
            print(f"Game {i}: SECOND won")
        else:
            unknown += 1
            print(f"Game {i}: winner could not be determined")

    return first_wins, second_wins, unknown


def main() -> None:
    parser = argparse.ArgumentParser(description="Run repeated AI-vs-AI backgammon matches.")
    parser.add_argument("--games", type=int, default=10, help="Number of games to simulate")
    parser.add_argument(
        "--first-ai",
        type=str,
        default="strategic",
        choices=["basic", "greedy", "montecarlo", "human", "strategic", "my"],
        help="AI used as Side.FIRST",
    )
    parser.add_argument(
        "--second-ai",
        type=str,
        default="basic",
        choices=["basic", "greedy", "montecarlo", "human", "strategic", "my"],
        help="AI used as Side.SECOND",
    )
    parser.add_argument("--render", action="store_true", help="Enable renderer while simulating")
    parser.add_argument("--verbose", action="store_true", help="Show turn-by-turn logs")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=90,
        help="Max seconds allowed per game before marking as unknown",
    )
    args = parser.parse_args()

    n_games = args.games
    first_wins, second_wins, unknown = simulate_games(
        n_games=n_games,
        first_ai=args.first_ai,
        second_ai=args.second_ai,
        render=args.render,
        verbose=args.verbose,
        timeout_seconds=args.timeout_seconds,
    )

    print("\n=== Simulation summary ===")
    print(f"Total games:   {n_games}")
    print(f"FIRST AI:      {args.first_ai}")
    print(f"SECOND AI:     {args.second_ai}")
    print(f"FIRST wins:    {first_wins}")
    print(f"SECOND wins:   {second_wins}")
    print(f"Unknown games: {unknown}")

    if first_wins > second_wins:
        print("Overall winner: FIRST")
    elif second_wins > first_wins:
        print("Overall winner: SECOND")
    else:
        print("Overall result: TIE")


if __name__ == "__main__":
    main()

