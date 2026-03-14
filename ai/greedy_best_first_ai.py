from ai.ai_abstract import AiAbstractClass
from ai.human_input_ai import print_move
from game_state_dict import UniqueGameStates
from game_state_generator import Move
from pygammon import GameState, Side


class GreedyBestFirstAi(AiAbstractClass):
    """
    Greedy Best-First Search AI.

    The engine already provides all legal successor states for the current turn.
    This AI evaluates each successor with a heuristic h(s) and chooses the move
    sequence leading to the state with the lowest heuristic value.

    Lower score = better state for this player.
    """

    def move(self) -> Move:
        if self._chosen_move_ is None:
            available_moves: UniqueGameStates = self.get_all_possible_moves(
                self.game_state, self.available_moves
            )

            if len(available_moves.values()) == 0 or available_moves.max_moves == 0:
                raise Exception("No possible moves to make, the code is not ready for this")

            best_value = float("inf")
            best_moves = None

            for candidate in available_moves.values():
                candidate_state = candidate["possible_game_state"]
                candidate_value = self.evaluate_state(candidate_state)

                if candidate_value < best_value:
                    best_value = candidate_value
                    best_moves = candidate["moves_to_reach_it"]

            self.chose_move(best_moves)

            print(f"player : {self.side} choosing moves with Greedy Best-First Search:")
            print(f"chosen heuristic value: {best_value}")
            for move in best_moves:
                print_move(move)

        return self.proceed_with_move()
#play around with weights!
    def heuristic_new(self, game_state: GameState, maximalize_hits: bool = False) -> int:
        value = 0
        opponent = Side.SECOND if self.side == Side.FIRST else Side.FIRST

        my_bar = game_state.first_hit if self.side == Side.FIRST else game_state.second_hit
        opp_bar = game_state.second_hit if self.side == Side.FIRST else game_state.first_hit
        my_borne = game_state.first_borne if self.side == Side.FIRST else game_state.second_borne

        for i, point in enumerate(game_state.board):
            if point.side == self.side:
                distance_to_home = (24 - i) if self.side == Side.FIRST else (i + 1)
                value += 7 * point.count * distance_to_home

                # blot penalty
                if point.count == 1:
                    value += 22

                # made point reward
                if point.count >= 2:
                    value -= 9

                    # home-board point reward
                    in_home_board = (
                        (self.side == Side.FIRST and 0 <= i <= 5)
                        or (self.side == Side.SECOND and 18 <= i <= 23)
                    )
                    if in_home_board:
                        value -= 14

                    # anchor reward
                    in_opponent_home = (
                        (self.side == Side.FIRST and 18 <= i <= 23)
                        or (self.side == Side.SECOND and 0 <= i <= 5)
                    )
                    if in_opponent_home:
                        value -= 8

                    # local prime / blockade reward
                    if i > 0:
                        left = game_state.board[i - 1]
                        if left.side == self.side and left.count >= 2:
                            value -= 8
                    if i < 23:
                        right = game_state.board[i + 1]
                        if right.side == self.side and right.count >= 2:
                            value -= 8

            elif point.side == opponent and point.count >= 2:
                value += 4

        # bar pressure
        value += 40 * my_bar
        value -= 22 * opp_bar

        # progress toward winning
        value -= 12 * my_borne

        if maximalize_hits:
            value -= 15 * opp_bar

        return int(value)
    
    def evaluate_state(self, game_state: GameState) -> int:
        return self.heuristic_new(game_state, maximalize_hits=False)
    

    