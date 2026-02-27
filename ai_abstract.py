from abc import ABC, abstractmethod
from typing import Tuple, Optional

from pygammon import GameState, InputType, Side


class AiAbstractClass(ABC):
    game_state: GameState = None
    available_moves: Tuple[int, int] = None

    def __init__(self, side: Side):
        self.side = side

    @abstractmethod
    def move(self) -> Tuple[InputType, Optional[Tuple[int, Optional[int]]]]:
        # see https://pygammon.readthedocs.io/en/latest/protocol.html#moving
        pass

    def update_game_state(self, gameState: GameState):
        self.game_state = gameState

    def update_available_moves(self, available_moves):
        self.available_moves = available_moves

    def get_my_hits(self):
        if self.side == Side.FIRST:
            return self.game_state.first_hit
        else:
            return self.game_state.second_hit

    # dice - the dice move that will be used for returning the token
    def return_hit_token(dice:int):
        return (dice, None)
