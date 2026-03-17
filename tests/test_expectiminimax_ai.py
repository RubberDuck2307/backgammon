from __future__ import annotations

from pygammon import GameState, InputType, Side
from pygammon.structures import Point

from ai.expectiminimax_ai import ExpectiminimaxAi


def build_starting_game_state() -> GameState:
    board = [Point() for _ in range(24)]
    board[0] = Point(Side.SECOND, 2)
    board[5] = Point(Side.FIRST, 5)
    board[7] = Point(Side.FIRST, 3)
    board[11] = Point(Side.SECOND, 5)
    board[12] = Point(Side.FIRST, 5)
    board[16] = Point(Side.SECOND, 3)
    board[18] = Point(Side.SECOND, 5)
    board[23] = Point(Side.FIRST, 2)
    return GameState(board=board, first_hit=0, first_borne=0, second_hit=0, second_borne=0)


def test_expectiminimax_returns_a_legal_move_step() -> None:
    state = build_starting_game_state()
    ai = ExpectiminimaxAi(Side.FIRST)
    ai.search_depth = 1
    ai.update_game_state(state)

    # Dice are already rolled in the engine before move() is called.
    ai.available_moves = (1, 2)

    move = ai.move()
    assert move[0] == InputType.MOVE
    assert move[1] is not None
    dice_index, from_point = move[1]
    assert dice_index in (0, 1)
    # from_point may be None if restoring from bar; starting state has no hits.
    assert from_point is None or 0 <= from_point <= 23

