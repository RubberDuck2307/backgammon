from engine.engine_types import GameState, Side


def heuristic_new(game_state: GameState, side: Side, maximalize_hits: bool = False) -> int:
   #straight up stolen from vita's greedy_best_first_ai just made it more agressive to use for expectminimax
    value = 0
    opponent = Side.SECOND if side == Side.FIRST else Side.FIRST

    my_bar = game_state.first_hit if side == Side.FIRST else game_state.second_hit
    opp_bar = game_state.second_hit if side == Side.FIRST else game_state.first_hit
    my_borne = game_state.first_borne if side == Side.FIRST else game_state.second_borne

    for i, point in enumerate(game_state.board):
        if point.side == side:
            distance_to_home = (24 - i) if side == Side.FIRST else (i + 1)
            value += 6 * point.count * distance_to_home  # was 7

            if point.count == 1:
                value += 15  # was 22

            if point.count >= 2:
                value -= 8  # was 9

                in_home_board = (
                    (side == Side.FIRST and 0 <= i <= 5)
                    or (side == Side.SECOND and 18 <= i <= 23)
                )
                if in_home_board:
                    value -= 14  # was 14

                in_opponent_home = (
                    (side == Side.FIRST and 18 <= i <= 23)
                    or (side == Side.SECOND and 0 <= i <= 5)
                )
                if in_opponent_home:
                    value -= 4  # was 8

                if i > 0:
                    left = game_state.board[i - 1]
                    if left.side == side and left.count >= 2:
                        value -= 10  # was 8
                if i < 23:
                    right = game_state.board[i + 1]
                    if right.side == side and right.count >= 2:
                        value -= 10  # was 8

        elif point.side == opponent and point.count >= 2:
            value += 2  # was 4

    value += 30 * my_bar    # was 40
    value -= 30 * opp_bar   # was 22
    value -= 20 * my_borne  # was 12

    if maximalize_hits:
        value -= 25 * opp_bar  # was 15

    return int(value)

