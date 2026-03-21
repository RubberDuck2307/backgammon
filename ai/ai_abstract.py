from abc import ABC, abstractmethod
from typing import Tuple, Optional, List

from engine.engine_types import GameState, Side, DieRolls

from game_state_dict import Move


class AiAbstractClass(ABC):
    _chosen_move_: Optional[List[Move]] = None
    game_state: GameState = None
    available_moves: Tuple[int, int] | Tuple[int, int, int, int] = None
    previous_player_dice_rolls: Tuple[int, int] | Tuple[int, int, int, int]  = None
    side: Side = None
    opponent: Side = None
    move_counter: int = 0

    def __init__(self, side: Side, log: bool = False):
        self.log = log
        self.side = side
        self.opponent = self.other_side(side)

    @staticmethod
    def other_side(side: Side) -> Side:
        return Side.SECOND if side == Side.FIRST else Side.FIRST

    @abstractmethod
    def move(self) -> Move:
        pass

    def proceed_with_move(self):
        if self.log:
            print("Continuing with move, for player:", self.side)
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
        self.move_counter = 0
        self._chosen_move_ = None
        if available_moves[0] == available_moves[1]:
            # if the dice are the same, we have to play them twice
            self.available_moves = (available_moves.first, available_moves.second, available_moves.first,
                                    available_moves.second)
            self.move_counter = 4
        else:
            self.available_moves = (available_moves.first, available_moves.second)
            self.move_counter = 2

    def update_enemy_dice_rolls(self, dice_rolls: DieRolls):
        if dice_rolls[0] == dice_rolls[1]:
            self.previous_player_dice_rolls = (dice_rolls.first, dice_rolls.second, dice_rolls.first,
                                              dice_rolls.second)
        else:
            self.previous_player_dice_rolls = (dice_rolls.first, dice_rolls.second)