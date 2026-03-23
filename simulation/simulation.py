import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from typing import Union, Tuple, Optional

from ai.basic_ai import BasicAi
from ai.expectiminimax_ai import ExpectiminimaxAi
from ai.greedy_best_first_ai import GreedyBestFirstAi
from ai.human_input_ai import print_move
from ai.random_ai import RandomAi
from ai.strategic_ai import StrategicAi
from engine.engine import run_game
from engine.engine_types import GameState, OutputType, InvalidMoveCode, Side, InputType
from renderer import BackgammonRenderer
from tqdm import tqdm

RENDERER = BackgammonRenderer()


class SimulationGame:

    def __init__(self, first_ai_cls, second_ai_cls, log=False):
        self.firstAi = first_ai_cls(Side.FIRST)
        self.secondAi = second_ai_cls(Side.SECOND)

        self.current_game_state: GameState | None = None
        self.next_player: Optional[Side] = None
        self.winner: Optional[Side] = None
        self.previous_game_state: Optional[GameState] = None
        self.log = log

    def do_move_handler(self, side: Side) -> Tuple[InputType, Optional[Tuple[int, Optional[int]]]]:
        move = self.firstAi.move() if side == Side.FIRST else self.secondAi.move()
        if self.log:
            print(f"Player {Side(side).name} move:")
            print_move(move)
        return move

    def current_game_state_handler(
            self,
            output_type: OutputType,
            data: Union[GameState, Tuple[int, int], InvalidMoveCode, Side],
            side: Optional[Side] = None
    ):

        if output_type == OutputType.GAME_STATE:
            if self.log:
                print("move performed, new game state:")
            self.previous_game_state = self.current_game_state
            self.current_game_state = data

        elif output_type == OutputType.TURN_ROLLS:
            self.next_player = Side.FIRST if data[0] > data[1] else Side.SECOND

        elif output_type == OutputType.MOVE_ROLLS:
            if self.log:
                print(f"Move rolls: for player{self.next_player}", data)

            if self.next_player == Side.FIRST:
                self.firstAi.update_game_state(self.current_game_state)
                self.firstAi.update_available_moves(data)
                self.secondAi.update_enemy_dice_rolls(data)
                self.next_player = Side.SECOND

            else:
                self.secondAi.update_game_state(self.current_game_state)
                self.secondAi.update_available_moves(data)
                self.firstAi.update_enemy_dice_rolls(data)
                self.next_player = Side.FIRST

        elif output_type == OutputType.INVALID_MOVE:
            RENDERER.render(self.current_game_state)
            if self.next_player == Side.FIRST:
                self.secondAi.update_game_state(self.current_game_state)
            else:
                self.firstAi.update_game_state(self.current_game_state)
            print("Invalid move:", data)

        elif output_type == OutputType.GAME_WON:
            self.winner = data


def run_match(first_ai, second_ai, games=100):
    first_wins = 0
    second_wins = 0

    pbar = tqdm(range(games), desc="Running games")

    for _ in pbar:
        game = SimulationGame(first_ai, second_ai)

        run_game(game.do_move_handler, game.current_game_state_handler)

        winner = game.winner

        if winner == Side.FIRST:
            first_wins += 1
        else:
            second_wins += 1

        pbar.set_postfix({
            "FIRST": first_wins,
            "SECOND": second_wins
        })

    print("\nRESULTS")
    print("FIRST wins :", first_wins)
    print("SECOND wins:", second_wins)
    print("FIRST winrate :", first_wins / games)
    print("SECOND winrate:", second_wins / games)


def run_round_robin(ai_classes: dict[str, type], games_per_side: int = 1):
    """
    Side-balanced round robin.

    For each unordered pair (A,B), run:
    - `games_per_side` games with A as FIRST and B as SECOND
    - `games_per_side` games with B as FIRST and A as SECOND
    """
    names = list(ai_classes.keys())
    wins: dict[str, int] = {name: 0 for name in names}
    games_played: dict[str, int] = {name: 0 for name in names}

    pbar_total = 0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            # two legs (A first, B first) times games_per_side
            pbar_total += 2 * games_per_side

    pbar = tqdm(total=pbar_total, desc="Running tournament")

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = names[i]
            b = names[j]
            a_cls = ai_classes[a]
            b_cls = ai_classes[b]

            # A as FIRST
            for _ in range(games_per_side):
                game = SimulationGame(a_cls, b_cls)
                run_game(game.do_move_handler, game.current_game_state_handler)
                if game.winner == Side.FIRST:
                    wins[a] += 1
                else:
                    wins[b] += 1
                games_played[a] += 1
                games_played[b] += 1
                pbar.update(1)

            # B as FIRST
            for _ in range(games_per_side):
                game = SimulationGame(b_cls, a_cls)
                run_game(game.do_move_handler, game.current_game_state_handler)
                if game.winner == Side.FIRST:
                    wins[b] += 1
                else:
                    wins[a] += 1
                games_played[a] += 1
                games_played[b] += 1
                pbar.update(1)

    pbar.close()

    print("\nTOURNAMENT RESULTS (side-balanced)")
    for name in sorted(names):
        t = games_played[name]
        w = wins[name]
        winrate = (w / t) if t else 0.0
        print(f"{name:>14}  wins={w:>3}  games={t:>3}  winrate={winrate:.2%}")


if __name__ == "__main__":
    ai_classes = {
        "strategic": StrategicAi,
        "greedy": GreedyBestFirstAi,
        "basic": BasicAi,
        "random": RandomAi,
        "expectiminimax": ExpectiminimaxAi,
    }
    run_round_robin(ai_classes, games_per_side=1)
