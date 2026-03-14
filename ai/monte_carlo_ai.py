import random
from multiprocessing import Pool, cpu_count
from typing import Optional, List

from pygammon import GameState, Side
from tqdm import tqdm

from ai.ai_abstract import AiAbstractClass
from game_state_generator import Move, is_game_over, PossibleGameState, get_all_possible_moves_for_side
from generators.stochastic_generator import select_random_dice_outcome
from mc_structure import GameNode


def simulation_worker(searcher):
    return searcher.single_sequence_search()


class MonteCarloAi(AiAbstractClass):
    parent_node: Optional[GameNode] = None
    search_limit: int = 1500
    search_depth: int = 20

    def __init__(self, side: Side):
        super().__init__(side)
        self.parent_node = None

    def update_game_state(self, game_state: GameState):
        if self.parent_node is None:
            self.parent_node = GameNode({"possible_game_state": game_state, "moves_to_reach_it": []})
            return
        node = self.parent_node.find_child(game_state)
        if node is None:
            node = GameNode({"possible_game_state": game_state, "moves_to_reach_it": []})
        self.parent_node = node

    def all_sequence_search(self):
        workers = cpu_count()
        with Pool(workers) as pool:
            results = list(
                tqdm(
                    pool.imap(simulation_worker, [self] * self.search_limit),
                    total=self.search_limit
                )
            )

        for sequence, win in results:
            self.parent_node.update_sequence(sequence, win)

    def single_sequence_search(self):
        turn_search_count = 0
        current_state = self.parent_node.game_state
        dices = self.available_moves
        side = self.side
        winner = None
        search_sequence: List[PossibleGameState] = []
        while turn_search_count < self.search_depth:
            possible_moves = get_all_possible_moves_for_side(current_state["possible_game_state"], dices,
                                                             side).values()
            current_state = self.find_smallest_score_move(possible_moves)
            search_sequence.append(current_state)
            dices = select_random_dice_outcome()
            side = Side.SECOND if side == Side.FIRST else Side.FIRST
            turn_search_count += 1
            result = is_game_over(current_state["possible_game_state"])
            score = min_max_score(current_state["possible_game_state"], self.side)
            if result is not None:
                winner = result
                break
        if winner is None:
            if min_max_score(current_state["possible_game_state"], self.side) < 0:
                winner = Side.SECOND if self.side == Side.SECOND else Side.FIRST
        return search_sequence, winner == self.side

    def find_smallest_score_move(self, game_states: List[PossibleGameState]) -> PossibleGameState:
        if not game_states:
            return None

        min_score = float('inf')
        best_move = None
        total_score = 0

        for move in game_states:
            score = ucb_score(move["possible_game_state"], self.side)
            total_score += score
            if score < min_score:
                min_score = score
                best_move = move

        average_score = total_score / len(game_states)
        print(f"Average score of possible moves: {average_score:.2f}")

        return best_move
    def move(self) -> Move:
        if self._chosen_move_ is None:
            self.all_sequence_search()
            self.chose_move(self.parent_node.best_child()["moves_to_reach_it"])
        return self.proceed_with_move()


def ucb_score(game_state: GameState, side: Side) -> float:
    if random.random() < 0.3:
        return 0
    return heuristic_new(game_state, side)


def min_max_score(game_state: GameState, side: Side) -> float:
    return ucb_score(game_state, side) - ucb_score(game_state,
                                                   Side.SECOND if side == Side.FIRST else Side.FIRST)

def heuristic_new(game_state: GameState, side: Side, maximalize_hits: bool = False) -> int:
    value = 0
    home = 0 if side == Side.FIRST else 23
    for i, point in enumerate(game_state.board):
        if point.side == side:
            value += point.count * abs(home - i)
    return value
