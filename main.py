import os
import time
from typing import Union, Tuple, Optional

import pygammon
from pygammon import GameState, OutputType, InvalidMoveCode, Side, InputType

from ai.basic_ai import BasicAi
from ai.greedy_best_first_ai import GreedyBestFirstAi
from ai.human_input_ai import HumanInputAI
from ai.human_input_ai import print_move
from ai.monte_carlo_ai import MonteCarloAi
from ai.strategic_ai import StrategicAi
from renderer import BackgammonRenderer


class Game:

    def __init__(self, first_ai_name: str = "montecarlo", second_ai_name: str = "basic",
                 render: bool = True, verbose: bool = True):
        self.renderer = BackgammonRenderer() if render else None
        self.render = render
        self.verbose = verbose
        self.turn_counter = 0
        self.firstAi = create_ai(first_ai_name, Side.FIRST)
        self.secondAi = create_ai(second_ai_name, Side.SECOND)
        self.current_game_state: GameState
        self.next_player = None

    def do_move_handler(self, side: Side) -> Tuple[InputType, Optional[Tuple[int, Optional[int]]]]:
        move = self.firstAi.move() if side == Side.FIRST else self.secondAi.move()
        if self.verbose:
            print(f"{self.turn_counter}. move by player: {Side(side).name}")
            print_move(move)

        return move

    def current_game_state_handler(self, output_type: OutputType,
                                   data: Union[GameState, Tuple[int, int], InvalidMoveCode, Side],
                                   side: Optional[Side] = None):
        if output_type == OutputType.GAME_STATE:
            self.current_game_state = data
            if self.render and self.renderer is not None:
                self.renderer.render(data)
            self.turn_counter += 1

        elif output_type == OutputType.TURN_ROLLS:
            self.next_player = Side.FIRST if data[0] > data[1] else Side.SECOND
            if self.verbose:
                print("Turn rolls:", data, "Next player:", self.next_player)


        elif output_type == OutputType.MOVE_ROLLS:
            if self.verbose:
                print(f"\nMOVE ROLLS for player: {self.next_player}", data)
            if self.next_player == Side.FIRST:
                self.firstAi.update_game_state(self.current_game_state)
                self.firstAi.update_available_moves(data)
                self.next_player = Side.SECOND
            elif self.next_player == Side.SECOND:
                self.secondAi.update_game_state(self.current_game_state)
                self.secondAi.update_available_moves(data)
                self.next_player = Side.FIRST

        elif output_type == OutputType.INVALID_MOVE:
            if self.verbose:
                print("Invalid move:", data)

        elif output_type == OutputType.GAME_WON:
            # pygammon signals end of game; data is the Side that won
            winner = data
            print(f"Game finished! Winner: {winner.name}")
            try:
                if self.render and self.renderer is not None:
                    self.renderer.show_winner(winner)
            except Exception:
                pass
            if self.render:
                # keep the winner screen up for a couple of seconds before exit
                time.sleep(3)


def create_ai(ai_name: str, side: Side):
    normalized = ai_name.strip().lower()
    ai_map = {
        "basic": BasicAi,
        "greedy": GreedyBestFirstAi,
        "montecarlo": MonteCarloAi,
        "human": HumanInputAI,
        "strategic": StrategicAi,
        "my": StrategicAi,
    }
    ai_class = ai_map.get(normalized)
    if ai_class is None:
        available = ", ".join(sorted(ai_map.keys()))
        raise ValueError(f"Unknown AI '{ai_name}'. Available: {available}")
    return ai_class(side)


# Check https://pygammon.readthedocs.io/en/latest/protocol.html
first_ai_name = os.getenv("FIRST_AI", "montecarlo")
second_ai_name = os.getenv("SECOND_AI", "basic")
render = os.getenv("RENDER", "1") != "0"
verbose = os.getenv("VERBOSE", "1") != "0"

game = Game(
    first_ai_name=first_ai_name,
    second_ai_name=second_ai_name,
    render=render,
    verbose=verbose,
)
pygammon.run(game.do_move_handler, game.current_game_state_handler)
