import os

from ai.ai_abstract import AiAbstractClass
from ai.human_input_ai import print_move
from game_state_dict import UniqueGameStates, Move, game_state_key
from game_state_generator import get_all_possible_moves
from generators.stochastic_generator import generate_next_turn_distribution_with_states
from pygammon import GameState, Side


class StrategicAi(AiAbstractClass):
    """
    Strategic AI with selective lookahead.

    How it works:
    - Generate all legal end states for this turn
    - Score all candidates with a fast static evaluation
    - Apply slower lookahead only to top static candidates
    - Pick the candidate with the lowest score
    """

    LOOKAHEAD_TOP_K = 3
    LOOKAHEAD_MAX_BRANCH = 14
    LOOKAHEAD_MARGIN = 18.0
    LOOKAHEAD_REPLY_WEIGHT = 0.15

    def move(self) -> Move:
        if self._chosen_move_ is None:
            lookahead_top_k = self._env_int("MYAI_LOOKAHEAD_TOP_K", self.LOOKAHEAD_TOP_K)
            lookahead_max_branch = self._env_int("MYAI_LOOKAHEAD_MAX_BRANCH", self.LOOKAHEAD_MAX_BRANCH)
            lookahead_margin = self._env_float("MYAI_LOOKAHEAD_MARGIN", self.LOOKAHEAD_MARGIN)
            reply_weight = self._env_float("MYAI_LOOKAHEAD_REPLY_WEIGHT", self.LOOKAHEAD_REPLY_WEIGHT)
            reply_weight = min(max(reply_weight, 0.0), 1.0)

            available_moves: UniqueGameStates = get_all_possible_moves(
                self.game_state,
                self.available_moves,
                self.side,
            )

            if len(available_moves.values()) == 0 or available_moves.max_moves == 0:
                raise Exception("No possible moves to make, the code is not ready for this")

            candidates = available_moves.values()
            scored_candidates = []
            for candidate in candidates:
                candidate_state = candidate["possible_game_state"]
                immediate_score = self._evaluate_for_side(candidate_state, self.side)
                scored_candidates.append((candidate, immediate_score))

            scored_candidates.sort(key=lambda item: item[1])

            best_value = scored_candidates[0][1]
            best_moves = scored_candidates[0][0]["moves_to_reach_it"]
            expected_reply_cache: dict[tuple, float] = {}

            should_use_lookahead = len(scored_candidates) <= lookahead_max_branch
            top_candidates = []
            if should_use_lookahead:
                lookahead_count = min(lookahead_top_k, len(scored_candidates))
                top_candidates = scored_candidates[:lookahead_count]
                # Include additional near-tied candidates; these are often tactically best.
                margin_cutoff = scored_candidates[0][1] + lookahead_margin
                for candidate, immediate_score in scored_candidates[lookahead_count:]:
                    if immediate_score > margin_cutoff:
                        break
                    top_candidates.append((candidate, immediate_score))

            for candidate, immediate_score in top_candidates:
                candidate_state = candidate["possible_game_state"]
                candidate_value = self._evaluate_candidate_with_lookahead(
                    candidate_state,
                    immediate_score,
                    expected_reply_cache,
                    reply_weight,
                )
                if candidate_value < best_value:
                    best_value = candidate_value
                    best_moves = candidate["moves_to_reach_it"]

            self.chose_move(best_moves)

            print(f"player : {self.side} choosing moves with StrategicAi:")
            print(f"chosen heuristic value: {best_value}")
            for move in best_moves:
                print_move(move)

        return self.proceed_with_move()

    def evaluate_state(self, game_state: GameState) -> int:
        return self._evaluate_for_side(game_state, self.side)

    def _evaluate_candidate_with_lookahead(
        self,
        candidate_state: GameState,
        immediate_score: float,
        expected_reply_cache: dict[tuple, float],
        reply_weight: float,
    ) -> float:
        state_key = game_state_key(candidate_state)
        if state_key in expected_reply_cache:
            expected_reply_score = expected_reply_cache[state_key]
        else:
            opponent = self._other_side(self.side)
            distribution = generate_next_turn_distribution_with_states(
                candidate_state,
                opponent,
                move_policy="best",
                state_evaluator=lambda state, side: self._evaluate_for_side(state, side),
            )
            expected_reply_score = 0.0
            for info in distribution.values():
                probability = info["probability"]
                reply_state = info["possible_game_state"]
                expected_reply_score += probability * self._evaluate_for_side(reply_state, self.side)
            expected_reply_cache[state_key] = expected_reply_score

        immediate_weight = 1.0 - reply_weight
        return immediate_weight * immediate_score + reply_weight * expected_reply_score

    def _env_int(self, key: str, default: int) -> int:
        raw = os.getenv(key)
        if raw is None:
            return default
        try:
            return int(raw)
        except ValueError:
            return default

    def _env_float(self, key: str, default: float) -> float:
        raw = os.getenv(key)
        if raw is None:
            return default
        try:
            return float(raw)
        except ValueError:
            return default

    def _evaluate_for_side(self, game_state: GameState, perspective: Side) -> int:
        return self._greedy_baseline_for_side(game_state, perspective)

    def _greedy_baseline_for_side(self, game_state: GameState, side: Side) -> int:
        value = 0
        opponent = self._other_side(side)

        my_bar = game_state.first_hit if side == Side.FIRST else game_state.second_hit
        opp_bar = game_state.second_hit if side == Side.FIRST else game_state.first_hit
        my_borne = game_state.first_borne if side == Side.FIRST else game_state.second_borne

        for i, point in enumerate(game_state.board):
            if point.side == side:
                distance_to_home = (24 - i) if side == Side.FIRST else (i + 1)
                value += 7 * point.count * distance_to_home

                if point.count == 1:
                    value += 22

                if point.count >= 2:
                    value -= 9

                    in_home_board = (
                        (side == Side.FIRST and 0 <= i <= 5)
                        or (side == Side.SECOND and 18 <= i <= 23)
                    )
                    if in_home_board:
                        value -= 14

                    in_opponent_home = (
                        (side == Side.FIRST and 18 <= i <= 23)
                        or (side == Side.SECOND and 0 <= i <= 5)
                    )
                    if in_opponent_home:
                        value -= 8

                    if i > 0:
                        left = game_state.board[i - 1]
                        if left.side == side and left.count >= 2:
                            value -= 8
                    if i < 23:
                        right = game_state.board[i + 1]
                        if right.side == side and right.count >= 2:
                            value -= 8

            elif point.side == opponent and point.count >= 2:
                value += 4

        value += 40 * my_bar
        value -= 22 * opp_bar
        value -= 12 * my_borne
        return int(value)

    def _other_side(self, side: Side) -> Side:
        return Side.SECOND if side == Side.FIRST else Side.FIRST
