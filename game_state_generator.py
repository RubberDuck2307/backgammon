from typing import TypedDict, TypeAlias, Tuple, Optional, List
from pygammon import Side, GameState, InputType
import copy

Move: TypeAlias = Tuple[InputType, Optional[Tuple[int, Optional[int]]]]


class NotPossibleMoveException(Exception):
    def __init__(self, message):
        super().__init__(message)


class PossibleGameState(TypedDict):
    possible_game_state: GameState
    moves_to_reach_it: List[Move]


def restore_token(game_state, side: Side, dice: int, dice_index: int,
                  previous_moves: List[Move] = None) -> PossibleGameState:
    if side == Side.FIRST:
        hit_tokens = game_state.first_hit
    else:
        hit_tokens = game_state.second_hit

    if hit_tokens == 0:
        raise NotPossibleMoveException("No hit tokens to restore")

    point_to_restore = 24 - dice if side == Side.FIRST else dice - 1

    new_game_state = _token_movement_(game_state, side, None, point_to_restore)

    moves_to_reach_it = [(InputType.MOVE, (dice_index, None))]
    if previous_moves is not None:
        moves_to_reach_it = previous_moves + moves_to_reach_it

    return PossibleGameState(possible_game_state=new_game_state, moves_to_reach_it=moves_to_reach_it)


def _token_movement_(game_state: GameState, current_side: Side, from_point: Optional[int], to_point: int):
    """
    from_point can be None if the token is being moved from the bar (hit tokens).
    """
    new_game_state = copy.deepcopy(game_state)

    if new_game_state.board[to_point].side != current_side and new_game_state.board[to_point].count >= 2:
        raise NotPossibleMoveException("Cannot move token to point occupied by opponent")

    elif new_game_state.board[to_point].side != current_side and new_game_state.board[to_point].count == 1:
        if current_side == Side.FIRST:
            new_game_state = new_game_state._replace(second_hit=new_game_state.second_hit + 1)
        else:
            new_game_state = new_game_state._replace(first_hit=new_game_state.first_hit + 1)
        new_game_state.board[to_point].side = None
        new_game_state.board[to_point].count = 0

    new_game_state.board[to_point].side = current_side
    new_game_state.board[to_point].count += 1

    if from_point is None:
        if current_side == Side.FIRST:
            if new_game_state.first_hit <= 0:
                raise NotPossibleMoveException("No hit tokens to move from bar")
            new_game_state = new_game_state._replace(first_hit=new_game_state.first_hit - 1)
        else:
            if new_game_state.second_hit <= 0:
                raise NotPossibleMoveException("No hit tokens to move from bar")
            new_game_state = new_game_state._replace(second_hit=new_game_state.second_hit - 1)
        return new_game_state

    new_game_state.board[from_point].count -= 1
    if new_game_state.board[from_point].count == 0:
        new_game_state.board[from_point].side = None

    return new_game_state


def borne_off_token(game_state: GameState, side: Side, from_point: int, dice_index: int,
                    previous_moves: List[Move] = None) -> PossibleGameState:
    # check if the move is possible
    new_game_state = copy.deepcopy(game_state)
    if new_game_state.board[from_point].side != side or new_game_state.board[from_point].count <= 0:
        raise NotPossibleMoveException("No token to move from the specified point")

    new_game_state.board[from_point].count = new_game_state.board[from_point].count - 1
    if new_game_state.board[from_point].count == 0:
        new_game_state.board[from_point].side = None

    if side == Side.FIRST:
        new_game_state = new_game_state._replace(first_borne=new_game_state.first_borne + 1)
    else:
        new_game_state = new_game_state._replace(second_borne=new_game_state.second_borne + 1)

    moves_to_reach_it = [(InputType.MOVE, (dice_index, from_point))]

    if previous_moves is not None:
        moves_to_reach_it = previous_moves + moves_to_reach_it

    return PossibleGameState(possible_game_state=new_game_state, moves_to_reach_it=moves_to_reach_it)


def is_borne_off_possible(game_state: GameState, side: Side, die) -> bool:
    if side == Side.SECOND:
        for i in range(18):
            if game_state.board[i].side == Side.SECOND and game_state.board[i].count > 0:
                return False
        return game_state.board[24 - die].side == Side.SECOND and game_state.board[24 - die].count > 0
    else:
        for i in range(6, 24):
            if game_state.board[i].side == Side.FIRST and game_state.board[i].count > 0:
                return False
        return game_state.board[die - 1].side == Side.FIRST and game_state.board[die - 1].count > 0


def get_all_tokens_ready_to_borne_off(game_state: GameState, side: Side, die: int) -> List[int]:
    tokens_ready_to_borne_off = []
    if side == Side.SECOND:
        if game_state.board[24 - die].side == Side.SECOND and game_state.board[24 - die].count > 0:
            tokens_ready_to_borne_off.append(24 - die)
    else:
        if game_state.board[die - 1].side == Side.FIRST and game_state.board[die - 1].count > 0:
            tokens_ready_to_borne_off.append(die - 1)
    return tokens_ready_to_borne_off


def move(game_state: GameState, side: Side, from_point: int, dice: int, dice_index: int,
         previous_moves: List[Move] = None) -> PossibleGameState:
    if side == Side.FIRST:
        to_point = from_point - dice
    else:
        to_point = from_point + dice

    if to_point < 0 or to_point > 23:
        raise NotPossibleMoveException("Move goes off the board")

    new_game_state = _token_movement_(game_state, side, from_point, to_point)
    moves_to_reach_it = [(InputType.MOVE, (dice_index, from_point))]
    if previous_moves is not None:
        moves_to_reach_it = previous_moves + moves_to_reach_it
    return PossibleGameState(possible_game_state=new_game_state, moves_to_reach_it=moves_to_reach_it)
