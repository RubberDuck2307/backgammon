from pygammon import GameState, Side

from ai.ai_abstract import AiAbstractClass
from ai.heuristics import heuristic_new
from game_state_dict import Move
from game_state_generator import get_all_possible_moves_for_side, is_game_over
from generators.stochastic_generator import all_dice_outcomes_with_probabilities, other_side


class ExpectiminimaxAi(AiAbstractClass):
    # number of full turns to look ahead (chance+decision) after the current move
    search_depth: int = 2

    def __init__(self, side: Side):
        super().__init__(side)
        self._cache = {}

    def move(self):
        if self._chosen_move_ is None:
            possible_moves = get_all_possible_moves_for_side(
                self.game_state, self.available_moves, self.side
            ).values()
            best_move = self.find_best_move(possible_moves)
            if best_move is None:
                raise Exception("No possible moves to make, the code is not ready for this")
            self.chose_move(best_move["moves_to_reach_it"])
        return self.proceed_with_move()

    def find_best_move(self, game_states):
        if not game_states:
            return None

        best_value = float("-inf")
        best_move = None

        for move in game_states:
            value = expectiminimax_value(
                move["possible_game_state"],
                other_side(self.side),
                self.side,
                self.search_depth,
                self._cache,
            )
            if value > best_value:
                best_value = value
                best_move = move

        return best_move


def expectiminimax_value(
    game_state: GameState,
    side_to_move: Side,
    perspective: Side,
    depth: int,
    cache,
) -> float:
    result = is_game_over(game_state)
    if result is not None:
        return 1e9 if result == perspective else -1e9

    if depth <= 0:
        return float(min_max_score(game_state, perspective))

    key = (
        side_to_move,
        depth,
        perspective,
        tuple((p.side, p.count) for p in game_state.board),
        game_state.first_hit,
        game_state.first_borne,
        game_state.second_hit,
        game_state.second_borne,
    )
    if key in cache:
        return cache[key]

    expected_value = 0.0
    for dice, prob in all_dice_outcomes_with_probabilities():
        possible_moves = get_all_possible_moves_for_side(game_state, dice, side_to_move).values()

        if not possible_moves:
            expected_value += prob * expectiminimax_value(
                game_state, other_side(side_to_move), perspective, depth - 1, cache
            )
            continue

        if side_to_move == perspective:
            best = float("-inf")
            for mv in possible_moves:
                best = max(
                    best,
                    expectiminimax_value(
                        mv["possible_game_state"],
                        other_side(side_to_move),
                        perspective,
                        depth - 1,
                        cache,
                    ),
                )
            expected_value += prob * best
        else:
            best = float("inf")
            for mv in possible_moves:
                best = min(
                    best,
                    expectiminimax_value(
                        mv["possible_game_state"],
                        other_side(side_to_move),
                        perspective,
                        depth - 1,
                        cache,
                    ),
                )
            expected_value += prob * best

    cache[key] = expected_value
    return expected_value


def min_max_score(game_state: GameState, side: Side) -> float:
    return heuristic_new(game_state, other_side(side)) - heuristic_new(game_state, side)

