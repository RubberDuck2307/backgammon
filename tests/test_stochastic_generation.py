from __future__ import annotations

import pytest
from pygammon import GameState, InputType, Side
from pygammon.structures import Point

from ai.ai_abstract import AiAbstractClass
from game_state_generator import Move


class DummyAi(AiAbstractClass):
    def move(self) -> Move:
        return InputType.UNDO, None


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


def assert_distribution_is_valid(distribution: dict[tuple, float]) -> None:
    assert distribution, "Distribution should not be empty"
    total_probability = sum(distribution.values())
    assert abs(total_probability - 1.0) < 1e-9, f"Expected sum 1.0, got {total_probability}"
    assert all(probability >= 0 for probability in distribution.values())


@pytest.fixture
def starting_state() -> GameState:
    return build_starting_game_state()


@pytest.fixture
def ai() -> DummyAi:
    return DummyAi(Side.FIRST)


def test_dice_outcomes_cover_full_probability_mass(ai: DummyAi) -> None:
    outcomes = ai._all_dice_outcomes_with_probabilities()
    assert len(outcomes) == 21
    assert abs(sum(probability for _, probability in outcomes) - 1.0) < 1e-12


def test_next_turn_distribution_sums_to_one(ai: DummyAi, starting_state: GameState) -> None:
    distribution = ai.generate_next_turn_state_distribution(starting_state, Side.FIRST, move_policy="uniform")
    assert_distribution_is_valid(distribution)


def test_next_turn_distribution_is_deterministic(ai: DummyAi, starting_state: GameState) -> None:
    distribution_first = ai.generate_next_turn_state_distribution(starting_state, Side.FIRST, move_policy="uniform")
    distribution_second = ai.generate_next_turn_state_distribution(starting_state, Side.FIRST, move_policy="uniform")
    assert distribution_first == distribution_second


def test_depth_zero_returns_same_state_with_probability_one(ai: DummyAi, starting_state: GameState) -> None:
    distribution = ai.generate_state_distribution_n_ply(starting_state, Side.FIRST, depth=0)
    assert list(distribution.values()) == [1.0]


def test_depth_one_matches_next_turn_distribution(ai: DummyAi, starting_state: GameState) -> None:
    one_ply = ai.generate_state_distribution_n_ply(starting_state, Side.FIRST, depth=1, move_policy="uniform")
    next_turn = ai.generate_next_turn_state_distribution(starting_state, Side.FIRST, move_policy="uniform")
    assert one_ply == next_turn


def test_depth_two_still_forms_probability_distribution(ai: DummyAi, starting_state: GameState) -> None:
    distribution = ai.generate_state_distribution_n_ply(starting_state, Side.FIRST, depth=2, move_policy="uniform")
    assert_distribution_is_valid(distribution)


def test_best_policy_requires_evaluator(ai: DummyAi, starting_state: GameState) -> None:
    with pytest.raises(ValueError):
        ai.generate_next_turn_state_distribution(starting_state, Side.FIRST, move_policy="best")


def test_best_policy_with_evaluator_sums_to_one(ai: DummyAi, starting_state: GameState) -> None:
    distribution = ai.generate_next_turn_state_distribution(
        starting_state,
        Side.FIRST,
        move_policy="best",
        state_evaluator=lambda state, side: 0.0,
    )
    assert_distribution_is_valid(distribution)

