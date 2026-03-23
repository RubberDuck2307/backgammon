import os
import time
from typing import Union, Tuple, Optional, Type

from ai.random_ai import RandomAi
from engine.engine_types import GameState, OutputType, InvalidMoveCode, Side, InputType

from ai.ai_abstract import AiAbstractClass
from ai.expectiminimax_ai import ExpectiminimaxAi
from ai.greedy_best_first_ai import GreedyBestFirstAi
from ai.human_input_ai import HumanInputAI, print_move
from ai.monte_carlo_ai import MonteCarloAi
from ai.strategic_ai import StrategicAi
from engine.engine import run_game
from renderer import BackgammonRenderer


class Game:

    def __init__(
        self,
        first_ai_cls,
        second_ai_cls,
        render: bool = True,
        verbose: bool = True,
    ):
        self.firstAi = first_ai_cls(Side.FIRST)
        self.secondAi = second_ai_cls(Side.SECOND)
        self.renderer = BackgammonRenderer() if render else None
        self.verbose = verbose
        self.turn_counter = 0
        self.current_game_state: GameState
        self.next_player = None
        self.winner: Optional[Side] = None

    def do_move_handler(self, side: Side) -> Tuple[InputType, Optional[Tuple[int, Optional[int]]]]:
        move = self.firstAi.move() if side == Side.FIRST else self.secondAi.move()
        if self.verbose:
            print(f"{self.turn_counter}. move by player: {Side(side).name}")
            print_move(move)

        time.sleep(1)
        return move

    def current_game_state_handler(self, output_type: OutputType,
                                   data: Union[GameState, Tuple[int, int], InvalidMoveCode, Side],
                                   side: Optional[Side] = None):
        if output_type == OutputType.GAME_STATE:
            self.current_game_state = data
            if self.renderer is not None:
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
                self.secondAi.update_enemy_dice_rolls(data)
                self.next_player = Side.SECOND
            elif self.next_player == Side.SECOND:
                self.secondAi.update_game_state(self.current_game_state)
                self.secondAi.update_available_moves(data)
                self.firstAi.update_enemy_dice_rolls(data)
                self.next_player = Side.FIRST
        elif output_type == OutputType.INVALID_MOVE:
            print("Invalid move:", data)

        elif output_type == OutputType.GAME_WON:
            winner = data
            print(f"Game finished! Winner: {winner.name}")
            if self.renderer is not None:
                try:
                    self.renderer.show_winner(winner)
                except Exception:
                    pass
                time.sleep(3)



game = Game(
    first_ai_cls=RandomAi,
    second_ai_cls=HumanInputAI
)
run_game(game.do_move_handler, game.current_game_state_handler)
