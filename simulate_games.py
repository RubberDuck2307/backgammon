import os
import re
import subprocess
import sys
from typing import Tuple


WINNER_PATTERN = re.compile(r"Game finished!\s*Winner:\s*(\w+)")


def run_single_game() -> str | None:
    """
    Run main.py once as a subprocess and return the winner name ("FIRST"/"SECOND"),
    or None if it could not be determined.
    """
    script_path = os.path.join(os.path.dirname(__file__), "main.py")

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
    )

    # Combine stdout and stderr for robustness
    output = (result.stdout or "") + "\n" + (result.stderr or "")

    match = WINNER_PATTERN.search(output)
    if match:
        return match.group(1)
    return None


def simulate_games(n_games: int = 10) -> Tuple[int, int, int]:
    """
    Run main.py n_games times and count wins.

    Returns a tuple: (first_wins, second_wins, unknown_results).
    """
    first_wins = 0
    second_wins = 0
    unknown = 0

    for i in range(1, n_games + 1):
        print(f"Starting game {i}/{n_games}...")
        winner = run_single_game()
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
    n_games = 10
    first_wins, second_wins, unknown = simulate_games(n_games)

    print("\n=== Simulation summary ===")
    print(f"Total games:   {n_games}")
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

