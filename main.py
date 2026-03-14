import time
from typing import Union, Tuple, Optional

import pygammon
from pygammon import GameState, OutputType, InvalidMoveCode, Side, InputType

from ai.basic_ai import BasicAi
from ai.human_input_ai import print_move
from ai.monte_carlo_ai import MonteCarloAi
from renderer import BackgammonRenderer


class Game:

    def __init__(self):
        self.renderer = BackgammonRenderer()
        self.turn_counter = 0
        self.firstAi = MonteCarloAi(Side.FIRST)
        self.secondAi = BasicAi(Side.SECOND)
        self.current_game_state : GameState
        self.next_player = None

    def do_move_handler(self, side: Side) -> Tuple[InputType, Optional[Tuple[int, Optional[int]]]]:
        move = self.firstAi.move() if side == Side.FIRST else self.secondAi.move()
        print(f"{self.turn_counter}. move by player: {Side(side).name}")
        print_move(move)

        return move

    def current_game_state_handler(self, output_type: OutputType,
                                   data: Union[GameState, Tuple[int, int], InvalidMoveCode, Side],
                                   side: Optional[Side] = None):
        if output_type == OutputType.GAME_STATE:
            self.current_game_state = data
            self.renderer.render(data)
            self.turn_counter += 1

        elif output_type == OutputType.TURN_ROLLS:
            self.next_player = Side.FIRST if data[0] > data[1] else Side.SECOND
            print("Turn rolls:", data, "Next player:", self.next_player)


        elif output_type == OutputType.MOVE_ROLLS:
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
            print("Invalid move:", data)
        
    
    
        elif output_type == OutputType.GAME_WON:
            # pygammon signals end of game; data is the Side that won
            winner = data
            print(f"Game finished! Winner: {winner.name}")
            try:
                pass
                self.renderer.show_winner(winner)
            except Exception:
                pass
            # keep the winner screen up for a couple of seconds before exit
            time.sleep(3)



# Check https://pygammon.readthedocs.io/en/latest/protocol.html
game = Game()
pygammon.run(game.do_move_handler, game.current_game_state_handler)
