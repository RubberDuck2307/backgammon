from abc import ABC, abstractmethod
from typing import Tuple, Optional, List

from pygammon import GameState, Side
from pygammon.structures import DieRolls

import game_state_generator as generator
from game_state_dict import UniqueGameStates
from game_state_generator import Move


class AiAbstractClass(ABC):
    chosen_move: Optional[List[Move]] = None
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
        move_to_make = self.chosen_move[len(self.chosen_move) - self.move_counter]
        self.move_counter -= 1
        if self.move_counter == 0:
            self.chosen_move = None
        return move_to_make

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

    def get_my_hit_tokens(self):
        if self.side == Side.FIRST:
            return self.game_state.first_hit
        else:
            return self.game_state.second_hit

    def get_all_possible_moves(self, game_state: GameState, dice: Tuple[int, int]) -> UniqueGameStates:
        states_first_dice = UniqueGameStates()

        #  first scenario we apply the first dice, then the second dice
        states_first_dice.extend(
            self._get_all_possible_moves_one_die(game_state,
                                                 self.get_my_hit_tokens(),
                                                 dice[0],
                                                 0))

        states_first_then_second_dice = UniqueGameStates()
        for state in states_first_dice.values():
            states_first_then_second_dice.extend(
                self._get_all_possible_moves_one_die(state["possible_game_state"],
                                                     max(self.get_my_hit_tokens() - 1, 0), # if we had hit tokens 1 was already used
                                                     dice[1],
                                                     1,
                                                     state["moves_to_reach_it"]))

        # second scenario we apply the second dice, then the first dice
        states_second_dice = UniqueGameStates()
        states_second_dice.extend(
            self._get_all_possible_moves_one_die(game_state,
                                                 self.get_my_hit_tokens(),
                                                 dice[1],
                                                 1))

        states_second_then_first_dice = UniqueGameStates()
        for state in states_second_dice.values():
            states_second_then_first_dice.extend(
                self._get_all_possible_moves_one_die(state["possible_game_state"],
                                                     max(self.get_my_hit_tokens() - 1, 0),
                                                     # if we had hit tokens 1 was already used
                                                     dice[0],
                                                     0,
                                                     state["moves_to_reach_it"]))

        possible_game_states = UniqueGameStates()
        #if states_first_then_second_dice and states_second_then_first_dice is empty we should add the moves from states_first_dice, states_second_dice.
        possible_game_states.extend(states_first_then_second_dice)
        possible_game_states.extend(states_second_then_first_dice)

        if len(dice) == 4:
            states_first_dice_3_times = UniqueGameStates()
            for state in states_first_then_second_dice.values():
                states_first_dice_3_times.extend(
                    self._get_all_possible_moves_one_die(state["possible_game_state"],
                                                         max(self.get_my_hit_tokens() - 2, 0),
                                                         # if we had hit tokens 2 was already used
                                                         dice[2],
                                                         2,
                                                         state["moves_to_reach_it"]))
            states_first_dice_4_times = UniqueGameStates()
            for state in states_first_dice_3_times.values():
                states_first_dice_4_times.extend(
                    self._get_all_possible_moves_one_die(state["possible_game_state"],
                                                         max(self.get_my_hit_tokens() - 3, 0),
                                                         # if we had hit tokens 3 was already used
                                                         dice[3],
                                                         3,
                                                         state["moves_to_reach_it"]))
            #need to handle the scenario when only 1,2,3 moves are possible
            possible_game_states = states_first_dice_4_times
        return possible_game_states

    def _get_all_possible_moves_one_die(self, game_state: GameState, hit_tokens, die: int, dice_index: int,
                                        previous_moves=None):
        possible_game_states = UniqueGameStates()
        if hit_tokens > 0:
            try:
                possible_game_states.append(
                    generator.restore_token(game_state, self.side, die, dice_index, previous_moves))
            except generator.NotPossibleMoveException:
                pass
                # if the move is not possible, we just skip it
            return possible_game_states

        for point_index in self._get_all_movable_tokens(game_state):
            try:
                possible_game_states.append(
                    generator.move(game_state, self.side, point_index, die, dice_index, previous_moves))
            except generator.NotPossibleMoveException:
                pass
                # if the move is not possible, we just skip it
        return possible_game_states

    def _get_all_movable_tokens(self, game_state: GameState):
        movable_tokens = []
        for i, point in enumerate(game_state.board):
            if point.side == self.side and point.count > 0:
                movable_tokens.append(i)
        return movable_tokens
