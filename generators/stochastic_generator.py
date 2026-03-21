import random
from typing import Tuple, Optional, List, Callable, Dict

from engine.engine_types import GameState, Side

import game_state_generator as generator
from game_state_dict import game_state_key


def all_dice_outcomes_with_probabilities() -> List[Tuple[Tuple[int, int], float]]:
    outcomes: List[Tuple[Tuple[int, int], float]] = []
    for first in range(1, 7):
        for second in range(first, 7):
            probability = 1 / 36 if first == second else 2 / 36
            outcomes.append(((first, second), probability))
    return outcomes


def select_random_dice_outcome() -> Tuple[int, int]:
    outcomes = all_dice_outcomes_with_probabilities()
    dice, _ = random.choices(outcomes, weights=[prob for _, prob in outcomes], k=1)[0]
    return dice


def generate_next_turn_distribution_with_states(
        game_state: GameState,
        side: Side,
        move_policy: str = "uniform",
        state_evaluator: Optional[Callable[[GameState, Side], float]] = None,
) -> Dict[tuple, dict]:
    distribution: Dict[tuple, dict] = {}
    for dice, dice_probability in all_dice_outcomes_with_probabilities():
        possible_states = generator.get_all_possible_moves_for_side(game_state, dice, side)
        states = possible_states.values()

        if len(states) == 0:
            key = game_state_key(game_state)
            entry = distribution.get(key, {"possible_game_state": game_state, "probability": 0.0})
            entry["probability"] += dice_probability
            distribution[key] = entry
            continue

        if move_policy == "uniform":
            share = dice_probability / len(states)
            for state in states:
                key = game_state_key(state["possible_game_state"])
                entry = distribution.get(key, {"possible_game_state": state["possible_game_state"], "probability": 0.0})
                entry["probability"] += share
                distribution[key] = entry
            continue

        if move_policy == "best":
            if state_evaluator is None:
                raise ValueError("state_evaluator is required when move_policy='best'")
            best_state = min(states, key=lambda state: state_evaluator(state["possible_game_state"], side))
            key = game_state_key(best_state["possible_game_state"])
            entry = distribution.get(key,
                                     {"possible_game_state": best_state["possible_game_state"], "probability": 0.0})
            entry["probability"] += dice_probability
            distribution[key] = entry
            continue

        raise ValueError(f"Unknown move_policy '{move_policy}'")

    return distribution


def generate_next_turn_state_distribution(
        game_state: GameState,
        side: Side,
        move_policy: str = "uniform",
        state_evaluator: Optional[Callable[[GameState, Side], float]] = None,
) -> Dict[tuple, float]:
    distribution_with_states = generate_next_turn_distribution_with_states(
        game_state,
        side,
        move_policy,
        state_evaluator,
    )
    return {key: state["probability"] for key, state in distribution_with_states.items()}


def other_side(side: Side) -> Side:
    return Side.SECOND if side == Side.FIRST else Side.FIRST


def generate_state_distribution_n_ply(
        game_state: GameState,
        side_to_move: Side,
        depth: int,
        move_policy: str = "uniform",
        state_evaluator: Optional[Callable[[GameState, Side], float]] = None,
) -> Dict[tuple, float]:
    if depth <= 0:
        return {game_state_key(game_state): 1.0}

    current_distribution: Dict[tuple, dict] = {
        game_state_key(game_state): {"possible_game_state": game_state, "probability": 1.0}
    }
    current_side = side_to_move

    for _ in range(depth):
        next_distribution: Dict[tuple, dict] = {}
        for state in current_distribution.values():
            child_distribution = generate_next_turn_distribution_with_states(
                state["possible_game_state"],
                current_side,
                move_policy,
                state_evaluator,
            )

            for key, child_state in child_distribution.items():
                entry = next_distribution.get(
                    key,
                    {"possible_game_state": child_state["possible_game_state"], "probability": 0.0},
                )
                entry["probability"] += state["probability"] * child_state["probability"]
                next_distribution[key] = entry

        current_distribution = next_distribution
        current_side = other_side(current_side)

    return {key: state["probability"] for key, state in current_distribution.items()}
