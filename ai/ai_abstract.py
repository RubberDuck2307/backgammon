from abc import ABC, abstractmethod
from typing import Tuple, Optional, List, Dict, Callable

from pygammon import GameState, Side
from pygammon.structures import DieRolls

import game_state_generator as generator
from game_state_dict import UniqueGameStates, game_state_key
from game_state_generator import Move


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

    def get_my_hit_tokens(self):
        return self._get_hit_tokens(self.game_state, self.side)

    def _get_hit_tokens(self, game_state: GameState, side: Side) -> int:
        return game_state.first_hit if side == Side.FIRST else game_state.second_hit

    def get_all_possible_moves(self, game_state: GameState, dice: Tuple[int, ...]) -> UniqueGameStates:
        return self.get_all_possible_moves_for_side(game_state, dice, self.side)

    def get_all_possible_moves_for_side(self, game_state: GameState, dice: Tuple[int, ...], side: Side) -> UniqueGameStates:
        if len(dice) == 4:
            dice_orders = [(0, 1, 2, 3)]
        else:
            dice_orders = [(0, 1), (1, 0)]

        all_order_states = []

        for order in dice_orders:
            frontier = UniqueGameStates()
            frontier.append({"possible_game_state": game_state, "moves_to_reach_it": []})

            for dice_index in order:
                next_frontier = UniqueGameStates()
                for state in frontier.values():
                    state_game = state["possible_game_state"]
                    states_after_die = self._get_all_possible_moves_one_die_for_side(
                        state_game,
                        self._get_hit_tokens(state_game, side),
                        dice[dice_index],
                        dice_index,
                        side,
                        state["moves_to_reach_it"],
                    )
                    # If this die cannot be played for this path, keep the state and continue with next die.
                    if len(states_after_die) == 0:
                        next_frontier.append(state)
                    else:
                        next_frontier.extend(states_after_die)
                frontier = next_frontier

            # Keep track of how many moves were actually used in this order
            if len(frontier) > 0:
                all_order_states.append((frontier.max_moves, frontier))

        # Only keep orders that achieved the maximum number of moves
        if all_order_states:
            max_moves_overall = max(moves for moves, _ in all_order_states)
            possible_game_states = UniqueGameStates()
            for moves, states in all_order_states:
                if moves == max_moves_overall:
                    possible_game_states.extend(states)
            return possible_game_states
        else:
            return UniqueGameStates()

    def _get_all_possible_moves_one_die(self, game_state: GameState, hit_tokens, die: int, dice_index: int,
                                        previous_moves=None):
        return self._get_all_possible_moves_one_die_for_side(
            game_state, hit_tokens, die, dice_index, self.side, previous_moves
        )

    def _get_all_possible_moves_one_die_for_side(self, game_state: GameState, hit_tokens, die: int, dice_index: int,
                                                 side: Side, previous_moves=None):
        possible_game_states = UniqueGameStates()
        if hit_tokens > 0:
            try:
                possible_game_states.append(
                    generator.restore_token(game_state, side, die, dice_index, previous_moves))
            except generator.NotPossibleMoveException:
                pass
                # if the move is not possible, we just skip it
            return possible_game_states

        for point_index in self._get_all_movable_tokens_for_side(game_state, side):
            try:
                possible_game_states.append(
                    generator.move(game_state, side, point_index, die, dice_index, previous_moves))
            except generator.NotPossibleMoveException:
                pass
                # if the move is not possible, we just skip it
        return possible_game_states

    def _get_all_movable_tokens(self, game_state: GameState):
        return self._get_all_movable_tokens_for_side(game_state, self.side)

    def _get_all_movable_tokens_for_side(self, game_state: GameState, side: Side):
        movable_tokens = []
        for i, point in enumerate(game_state.board):
            if point.side == side and point.count > 0:
                movable_tokens.append(i)
        return movable_tokens

    @staticmethod
    def _all_dice_outcomes_with_probabilities() -> List[Tuple[Tuple[int, int], float]]:
        outcomes: List[Tuple[Tuple[int, int], float]] = []
        for first in range(1, 7):
            for second in range(first, 7):
                probability = 1 / 36 if first == second else 2 / 36
                outcomes.append(((first, second), probability))
        return outcomes

    def _generate_next_turn_distribution_with_states(
        self,
        game_state: GameState,
        side: Side,
        move_policy: str = "uniform",
        state_evaluator: Optional[Callable[[GameState, Side], float]] = None,
    ) -> Dict[tuple, dict]:
        distribution: Dict[tuple, dict] = {}
        for dice, dice_probability in self._all_dice_outcomes_with_probabilities():
            possible_states = self.get_all_possible_moves_for_side(game_state, dice, side)
            states = possible_states.values()

            if len(states) == 0:
                key = game_state_key(game_state)
                entry = distribution.get(key, {"possible_game_state": game_state, "probability": 0.0})
                entry["probability"] += dice_probability
                distribution[key] = entry
                continue

            if move_policy == "uniform":
                share = dice_probability / len(states)
                for state in states:
                    key = game_state_key(state["possible_game_state"])
                    entry = distribution.get(key, {"possible_game_state": state["possible_game_state"], "probability": 0.0})
                    entry["probability"] += share
                    distribution[key] = entry
                continue

            if move_policy == "best":
                if state_evaluator is None:
                    raise ValueError("state_evaluator is required when move_policy='best'")
                best_state = min(states, key=lambda state: state_evaluator(state["possible_game_state"], side))
                key = game_state_key(best_state["possible_game_state"])
                entry = distribution.get(key, {"possible_game_state": best_state["possible_game_state"], "probability": 0.0})
                entry["probability"] += dice_probability
                distribution[key] = entry
                continue

            raise ValueError(f"Unknown move_policy '{move_policy}'")

        return distribution

    def generate_next_turn_state_distribution(
        self,
        game_state: GameState,
        side: Side,
        move_policy: str = "uniform",
        state_evaluator: Optional[Callable[[GameState, Side], float]] = None,
    ) -> Dict[tuple, float]:
        distribution_with_states = self._generate_next_turn_distribution_with_states(
            game_state,
            side,
            move_policy,
            state_evaluator,
        )
        return {key: state["probability"] for key, state in distribution_with_states.items()}

    @staticmethod
    def _other_side(side: Side) -> Side:
        return Side.SECOND if side == Side.FIRST else Side.FIRST

    def generate_state_distribution_n_ply(
        self,
        game_state: GameState,
        side_to_move: Side,
        depth: int,
        move_policy: str = "uniform",
        state_evaluator: Optional[Callable[[GameState, Side], float]] = None,
    ) -> Dict[tuple, float]:
        if depth <= 0:
            return {game_state_key(game_state): 1.0}

        current_distribution: Dict[tuple, dict] = {
            game_state_key(game_state): {"possible_game_state": game_state, "probability": 1.0}
        }
        current_side = side_to_move

        for _ in range(depth):
            next_distribution: Dict[tuple, dict] = {}
            for state in current_distribution.values():
                child_distribution = self._generate_next_turn_distribution_with_states(
                    state["possible_game_state"],
                    current_side,
                    move_policy,
                    state_evaluator,
                )

                for key, child_state in child_distribution.items():
                    entry = next_distribution.get(
                        key,
                        {"possible_game_state": child_state["possible_game_state"], "probability": 0.0},
                    )
                    entry["probability"] += state["probability"] * child_state["probability"]
                    next_distribution[key] = entry

            current_distribution = next_distribution
            current_side = self._other_side(current_side)

        return {key: state["probability"] for key, state in current_distribution.items()}
