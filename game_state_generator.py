from typing import TypedDict, TypeAlias, Tuple, Optional, List
from pygammon import Side, GameState, InputType
import copy

from game_state_dict import UniqueGameStates, Move, PossibleGameState


class NotPossibleMoveException(Exception):
    def __init__(self, message):
        super().__init__(message)


def get_hit_tokens(game_state: GameState, side: Side) -> int:
    return game_state.first_hit if side == Side.FIRST else game_state.second_hit

def get_all_possible_moves( game_state: GameState, dice: Tuple[int, ...], side:Side) -> UniqueGameStates:
    return get_all_possible_moves_for_side(game_state, dice, side)

def get_all_possible_moves_for_side(game_state: GameState, dice: Tuple[int, ...], side: Side) -> UniqueGameStates:
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
                states_after_die = get_all_possible_moves_one_die_for_side(
                    state_game,
                    get_hit_tokens(state_game, side),
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

def _get_all_possible_moves_one_die(game_state: GameState, hit_tokens, die: int, dice_index: int,  side: Side,
                                    previous_moves=None,):
    return get_all_possible_moves_one_die_for_side(
        game_state, hit_tokens, die, dice_index, side, previous_moves
    )

def get_all_possible_moves_one_die_for_side(game_state: GameState, hit_tokens, die: int, dice_index: int,
                                            side: Side, previous_moves=None):
    possible_game_states = UniqueGameStates()
    if hit_tokens > 0:
        try:
            possible_game_states.append(
                restore_token(game_state, side, die, dice_index, previous_moves)
            )
        except NotPossibleMoveException:
            pass
            # if the move is not possible, we just skip it
        return possible_game_states

    for point_index in get_all_movable_tokens_for_side(game_state, side):
        try:
            # Normal move on the board
            possible_game_states.append(
                move(game_state, side, point_index, die, dice_index, previous_moves)
            )
        except NotPossibleMoveException:
            pass
            # if the move is not possible, we just skip it
        # Additionally, try to bear off from this point, if rules allow it.
        try:
            possible_game_states.append(
                borne_token(game_state, side, point_index, die, dice_index, previous_moves)
            )
        except NotPossibleMoveException:
            pass

    return possible_game_states

def get_all_movable_tokens(game_state: GameState, side: Side):
    return get_all_movable_tokens_for_side(game_state, side)

def get_all_movable_tokens_for_side(game_state: GameState, side: Side):
    movable_tokens = []
    for i, point in enumerate(game_state.board):
        if point.side == side and point.count > 0:
            movable_tokens.append(i)
    return movable_tokens



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


def _all_tokens_in_home(game_state: GameState, side: Side) -> bool:
    """Return True if all of the given side's tokens are either borne off or
    located in the home quarter.

    Note: board indexing runs from bottom right (0) counterclockwise to top
    right (23).  The *first* player's home quarter is points 0--5, while the
    *second* player's home quarter is opposite, points 18--23.
    """
    # no tokens on the bar
    if side == Side.FIRST and game_state.first_hit > 0:
        return False
    if side == Side.SECOND and game_state.second_hit > 0:
        return False

    for idx, point in enumerate(game_state.board):
        if point.side == side and point.count > 0:
            if side == Side.FIRST and idx > 5:
                return False
            if side == Side.SECOND and not (18 <= idx <= 23):
                return False
    return True

def is_game_over(game_state: GameState) -> Optional[Side]:
    if game_state.first_borne >= 15:
        return Side.FIRST
    if game_state.second_borne >= 15:
        return Side.SECOND
    return None

def borne_token(
    game_state: GameState,
    side: Side,
    from_point: int,
    dice: int,
    dice_index: int,
    previous_moves: List[Move] | None = None,
) -> PossibleGameState:
    """
    Bear off a single checker from the board for the given side using `dice`.

    This assumes standard backgammon rules:
    - All checkers for `side` must already be in the home board.
    - A checker on point n (1-indexed) can be borne off with die n.
    - A higher die can be used to bear off from the highest occupied point
      lower than the die, if there are no checkers on higher home points.
    """
    if not _all_tokens_in_home(game_state, side):
        raise NotPossibleMoveException("Not all tokens are in home")

    if game_state.board[from_point].side != side or game_state.board[from_point].count <= 0:
        raise NotPossibleMoveException("No checker of this side on from_point")

    # Point numbers are 1-based for the rules, but our indices are 0-based.
    if side == Side.FIRST:
        if not (0 <= from_point <= 5):
            raise NotPossibleMoveException("From point not in home board for FIRST")
        distance = from_point + 1  # points 0..5 -> distances 1..6

        if dice < distance:
            raise NotPossibleMoveException("Die too small to bear off from this point")

        if dice > distance:
            # Only allowed if there are no checkers on higher home points (further away).
            for idx in range(from_point + 1, 6):
                point = game_state.board[idx]
                if point.side == side and point.count > 0 and can_point_move(game_state, side, from_point, dice):
                    raise NotPossibleMoveException("Cannot bear off with higher die; checker behind")

    else:  # Side.SECOND
        if not (18 <= from_point <= 23):
            raise NotPossibleMoveException("From point not in home board for SECOND")
        distance = 24 - from_point  # indices 18..23 -> distances 6..1

        if dice < distance:
            raise NotPossibleMoveException("Die too small to bear off from this point")

        if dice > distance:
            # Only allowed if there are no checkers on lower home points (further away).
            for idx in range(18, from_point):
                point = game_state.board[idx]
                if point.side == side and point.count > 0 and can_point_move(game_state, side, from_point, dice):
                    raise NotPossibleMoveException("Cannot bear off with higher die; checker behind")

    new_game_state = copy.deepcopy(game_state)

    # Remove the checker from the board
    new_game_state.board[from_point].count -= 1
    if new_game_state.board[from_point].count == 0:
        new_game_state.board[from_point].side = None

    # Increment borne-off counter
    if side == Side.FIRST:
        new_game_state = new_game_state._replace(first_borne=new_game_state.first_borne + 1)
    else:
        new_game_state = new_game_state._replace(second_borne=new_game_state.second_borne + 1)

    moves_to_reach_it: List[Move] = [(InputType.MOVE, (dice_index, from_point))]
    if previous_moves is not None:
        moves_to_reach_it = previous_moves + moves_to_reach_it

    return PossibleGameState(possible_game_state=new_game_state, moves_to_reach_it=moves_to_reach_it)

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


def can_point_move(game_state: GameState, side: Side, from_point: int, dice: int) -> bool:
    try:
        move(game_state, side, from_point, dice, 0)
        return True
    except NotPossibleMoveException:
        return False