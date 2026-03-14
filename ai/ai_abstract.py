from abc import ABC, abstractmethod
from typing import Tuple, Optional, List

from pygammon import GameState, Side
from pygammon.structures import DieRolls

from game_state_dict import Move


class AiAbstractClass(ABC):
    _chosen_move_: Optional[List[Move]] = None
    game_state: GameState = None
    available_moves: Tuple[int, int] | Tuple[int, int, int, int] = None
    side: Side = None
    move_counter: int = 0

    def __init__(self, side: Side):
        self.side = side

    @abstractmethod
    def move(self) -> Move:
        # see https://pygammon.readthedocs.io/en/latest/protocol.html#moving
        pass

    def proceed_with_move(self):
        move_to_make = self._chosen_move_[len(self._chosen_move_) - self.move_counter]
        self.move_counter -= 1
        if self.move_counter == 0:
            self._chosen_move_ = None
        return move_to_make

    def chose_move(self, move: List[Move]):
        self._chosen_move_ = move
        self.move_counter = len(move)

    def update_game_state(self, game_state: GameState):
        self.game_state = game_state

    def update_available_moves(self, available_moves: DieRolls):
        if available_moves[0] == available_moves[1]:
            # if the dice are the same, we have to play them twice
            self.available_moves = (available_moves.first, available_moves.second, available_moves.first,
                                    available_moves.second)
            self.move_counter = 4
        else:
            self.available_moves = (available_moves.first, available_moves.second)
            self.move_counter = 2
