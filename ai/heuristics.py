from engine.engine_types import GameState, Side


def heuristic_new(game_state: GameState, side: Side, maximalize_hits: bool = False) -> int:
   #straight up stolen from vita's greedy_best_first_ai to test for expectiminimax
    value = 0
    opponent = Side.SECOND if side == Side.FIRST else Side.FIRST

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

    if maximalize_hits:
        value -= 15 * opp_bar  

    return int(value)

