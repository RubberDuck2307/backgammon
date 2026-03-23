import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from typing import Union, Tuple, Optional

from ai.expectiminimax_ai import ExpectiminimaxAi
from ai.greedy_best_first_ai import GreedyBestFirstAi
from ai.human_input_ai import print_move
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


if __name__ == "__main__":
    n = 20
    print("Strategic (FIRST) vs Expectiminimax (SECOND)")
    run_match(StrategicAi, ExpectiminimaxAi, games=n)
    print("\nStrategic (FIRST) vs Greedy best-first (SECOND)")
    run_match(StrategicAi, GreedyBestFirstAi, games=n)
