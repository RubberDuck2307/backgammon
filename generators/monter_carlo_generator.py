from typing import Optional, Tuple

from engine.engine_types import GameState, Side

from game_state_dict import PossibleGameState
from game_state_generator import restore_token, NotPossibleMoveException, move, borne_token, get_hit_tokens, \
    _all_tokens_in_home


def get_possible_moves_sequence_for_side(game_state: GameState, dice: Tuple[int, ...], side: Side) -> PossibleGameState:
    if dice[0] == dice[1]:
        dice = (dice[0], dice[1], dice[0], dice[1])
    max_possible_moves = 4 if len(dice) == 4 else 2
    if len(dice) == 4:
        dice_orders = [(0, 1, 2, 3)]
    else:
        dice_orders = [(0, 1), (1, 0)]
    all_found_game_states = []

    for order in dice_orders:
        current_state: PossibleGameState = {'possible_game_state': game_state, 'moves_to_reach_it': []}
        for i, dice_index in enumerate(order):
            found_move = get_one_possible_move_one_die_for_side(
                current_state["possible_game_state"],
                get_hit_tokens(current_state["possible_game_state"], side),
                dice[dice_index],
                dice_index,
                side,
                current_state["moves_to_reach_it"],
            )
            if found_move is None:
                break
            current_state = found_move
        if current_state != game_state:
            if current_state['moves_to_reach_it'] == max_possible_moves:
                return current_state
            all_found_game_states.append(current_state)

    if len(all_found_game_states) == 0:
        return {'possible_game_state': game_state, 'moves_to_reach_it': []}
    return max(all_found_game_states, key=lambda s: len(s['moves_to_reach_it']))


def get_one_possible_move_one_die_for_side(game_state: GameState, hit_tokens, die: int, dice_index: int,
                                           side: Side, previous_moves=None) -> Optional[PossibleGameState]:
    if hit_tokens > 0:
        try:
            return restore_token(game_state, side, die, dice_index, previous_moves)
        except NotPossibleMoveException:
            pass
            # if the move is not possible, we just skip it

    tokens = get_all_movable_tokens_for_side(game_state, side)
    if _all_tokens_in_home(game_state, side):
        for point_index in tokens:
            try:
                return borne_token(game_state, side, point_index, die, dice_index, previous_moves)
            except NotPossibleMoveException:
                pass

    for point_index in tokens:
        try:
            return move(game_state, side, point_index, die, dice_index, previous_moves)
        except NotPossibleMoveException:
            pass
    return None


def get_all_movable_tokens_for_side(game_state: GameState, side: Side):
    movable_tokens = []

    if side == Side.FIRST:
        indices = range(len(game_state.board) - 1, -1, -1)  # 23 -> 0
    else:
        indices = range(len(game_state.board))  # 0 -> 23

    for i in indices:
        point = game_state.board[i]
        if point.side == side and point.count > 0:
            movable_tokens.append(i)

    return movable_tokens
