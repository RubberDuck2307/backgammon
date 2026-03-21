import random
from typing import Optional, Tuple, Callable, Union


from engine.engine_types import Point, BOARD_SIZE, InputType, InvalidMoveCode, DieRolls, StartingCount, OutputType, \
    GameState, Side

import game_state_generator as gsg
from generators.stochastic_generator import other_side


"""
This class is inspired by pygammon library, which was the original implementation. 
To make sure to comply with the requirements of the project, we reimplement it from scratch, but the general structure and flow of the game is very similar to pygammon's implementation.
Also the types are the same.
"""


def run_game(move_handler: Callable[[Side], Tuple[InputType, Optional[Tuple[int, Optional[int]]]]],
             game_state_handler: Callable[
                 [OutputType, Union[GameState, Tuple[int, int], InvalidMoveCode, Side], Optional[Side]],
                 None
             ]):
    current_game_state = make_start_game_state()
    game_state_handler(OutputType.GAME_STATE, current_game_state, None)

    turn_rolls = (random.randint(1, 6), random.randint(1, 6))
    current_side = Side.SECOND if turn_rolls[0] > turn_rolls[1] else Side.FIRST  # this is flipped in the loop
    game_state_handler(OutputType.TURN_ROLLS, turn_rolls, None)
    while True:
        current_side = other_side(current_side)
        if _is_game_over(current_game_state) is not None:
            game_state_handler(OutputType.GAME_WON, _is_game_over(current_game_state), None)
            break

        current_dice_rolls = (random.randint(1, 6), random.randint(1, 6))
        current_dice_rolls = (current_dice_rolls[0], current_dice_rolls[1], current_dice_rolls[0],
                              current_dice_rolls[1]) if current_dice_rolls[0] == current_dice_rolls[
            1] else current_dice_rolls
        game_state_handler(OutputType.MOVE_ROLLS, DieRolls(first=current_dice_rolls[0], second=current_dice_rolls[1]),
                           None)

        not_yet_played_moves = [0, 1, 2, 3] if current_dice_rolls[0] == current_dice_rolls[1] else [0, 1]
        all_possible_moves = gsg.get_all_possible_moves_for_side(current_game_state, current_dice_rolls, current_side)

        played_moves = 0
        while played_moves < all_possible_moves.max_moves:
            move = move_handler(current_side)
            if move[1][0] not in not_yet_played_moves:
                game_state_handler(OutputType.INVALID_MOVE, InvalidMoveCode.INVALID_INPUT_TYPE, current_side)
                continue

            if move[1][1] is None:
                try:
                    current_game_state = \
                        gsg.restore_token(current_game_state, current_side, current_dice_rolls[move[1][0]], move[1][0])[
                            'possible_game_state']
                    played_moves += 1
                    not_yet_played_moves = [not_yet_played for not_yet_played in not_yet_played_moves if
                                            not_yet_played != move[1][0]]
                    game_state_handler(OutputType.GAME_STATE, current_game_state, None)
                    continue
                except gsg.NotPossibleMoveException:
                    game_state_handler(OutputType.INVALID_MOVE, InvalidMoveCode.INVALID_INPUT_TYPE, current_side)
                    continue

            move_length = current_dice_rolls[move[1][0]]
            move_length = -move_length if current_side == Side.FIRST else move_length

            current_pos = move[1][1]
            new_pos = current_pos + move_length

            if ((current_side == Side.FIRST and new_pos < 0) or
                    (current_side == Side.SECOND and new_pos >= BOARD_SIZE)):
                try:
                    current_game_state = gsg.borne_token(
                        current_game_state,
                        current_side,
                        current_pos,
                        abs(move_length),
                        move[1][0]
                    )['possible_game_state']

                    played_moves += 1
                    not_yet_played_moves = [m for m in not_yet_played_moves if m != move[1][0]]
                    game_state_handler(OutputType.GAME_STATE, current_game_state, None)
                    continue

                except gsg.NotPossibleMoveException:
                    game_state_handler(
                        OutputType.INVALID_MOVE,
                        InvalidMoveCode.INVALID_INPUT_TYPE,
                        current_side
                    )

            try:
                current_game_state = \
                    gsg.move(current_game_state, current_side, move[1][1], abs(move_length), move[1][0])[
                        'possible_game_state']
                played_moves += 1
                not_yet_played_moves = [not_yet_played for not_yet_played in not_yet_played_moves if
                                        not_yet_played != move[1][0]]
                game_state_handler(OutputType.GAME_STATE, current_game_state, None)
            except gsg.NotPossibleMoveException:
                game_state_handler(OutputType.INVALID_MOVE, InvalidMoveCode.INVALID_INPUT_TYPE, current_side)
                continue


def make_start_game_state():
    board = [Point() for _ in range(BOARD_SIZE)]

    board[0] = Point(Side.SECOND, StartingCount.LOW)
    board[5] = Point(Side.FIRST, StartingCount.HIGH)
    board[7] = Point(Side.FIRST, StartingCount.MEDIUM)
    board[11] = Point(Side.SECOND, StartingCount.HIGH)
    board[12] = Point(Side.FIRST, StartingCount.HIGH)
    board[16] = Point(Side.SECOND, StartingCount.MEDIUM)
    board[18] = Point(Side.SECOND, StartingCount.HIGH)
    board[23] = Point(Side.FIRST, StartingCount.LOW)

    return GameState(
        board=board,
        first_hit=0,
        first_borne=0,
        second_hit=0,
        second_borne=0
    )


def _get_current_hit_tokens(game_state: GameState, side: Side) -> int:
    return game_state.first_hit if side == Side.FIRST else game_state.second_hit


def _is_game_over(game_state: GameState) -> Optional[Side]:
    if game_state.first_borne == 15:
        return Side.FIRST
    elif game_state.second_borne >= 15:
        return Side.SECOND
    else:
        return None
