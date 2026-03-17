import random
from multiprocessing import Pool, cpu_count
from typing import Optional, List, Tuple

from pygammon import GameState, Side
from tqdm import tqdm

from ai.ai_abstract import AiAbstractClass
from game_state_generator import Move, is_game_over, get_all_possible_moves_for_side
from generators.monter_carlo_generator import get_possible_moves_sequence_for_side
from generators.stochastic_generator import select_random_dice_outcome, other_side
from mc_structure import GameNode, DiceNode, SearchStep


class MonteCarloAi(AiAbstractClass):
    parent_node: Optional[GameNode] = None
    search_limit: int = 200
    search_depth: int = 30

    def __init__(self, side: Side):
        super().__init__(side)
        self.parent_node = None

    def update_game_state(self, game_state: GameState):
        if self.parent_node is None:
            self.parent_node = GameNode({"possible_game_state": game_state, "moves_to_reach_it": []}, side=self.side)
            return

        played_dice_node = self.parent_node.find_child(self.previous_player_dice_rolls)
        if played_dice_node is None:
            self.parent_node = GameNode({"possible_game_state": game_state, "moves_to_reach_it": []}, side=self.side)
            return

        played_move_node = played_dice_node.find_child(game_state)
        if played_move_node is None:
            self.parent_node = GameNode({"possible_game_state": game_state, "moves_to_reach_it": []}, side=self.side)
            return

        self.parent_node = played_move_node

    def search(self):
        for _ in tqdm(range(self.search_limit), total=self.search_limit):
            sequence: List[SearchStep]
            selected_dice_node: DiceNode
            sequence, selected_dice_node = selection(self.parent_node, self.available_moves)

            node_to_perform_rollout = expansion(selected_dice_node)
            sequence.append(SearchStep(node_to_perform_rollout.game_state, None))

            winner = rollout(node_to_perform_rollout.game_state["possible_game_state"], node_to_perform_rollout.side,
                             self.search_depth)

            self.parent_node.back_propagate(sequence, winner)

    def multiprocess_search(self):
        num_workers = cpu_count()
        searches_per_worker = self.search_limit // num_workers

        args = [
            (self.side,
             self.parent_node.game_state["possible_game_state"],
             self.available_moves,
             self.search_depth,
             searches_per_worker)
            for _ in range(num_workers)
        ]

        with Pool(processes=num_workers) as pool:
            results = []
            for result in pool.imap_unordered(simulation_worker, args):
                results.append(result)

        for result in results:
            if self.parent_node is None:
                self.parent_node = result
            else:
                self.parent_node.merge(result)

    def move(self) -> Move:
        if self._chosen_move_ is None:
            self.multiprocess_search()
            self.chose_move(self.parent_node.find_child(self.available_moves).best_child(self.side)["moves_to_reach_it"])
        return self.proceed_with_move()


def backpropagation(node: GameNode, sequence: List[SearchStep], winner: Side):
    node.back_propagate(sequence, winner)


def selection(parent_node: GameNode, dices: Tuple[int, int]) -> Tuple[
    List[SearchStep], DiceNode]:
    sequence: List[SearchStep] = []
    current_dices = dices
    current_game_node: GameNode = parent_node

    while True:
        following_dice_node: Optional[DiceNode] = current_game_node.find_or_add_child(current_dices)
        sequence.append(SearchStep(current_game_node.game_state, following_dice_node.dice_outcome))
        if following_dice_node.visits == 0:
            break
        current_game_node = following_dice_node.select_ucb_child()
        current_dices = select_random_dice_outcome()
    return sequence, following_dice_node


def expansion(node: DiceNode) -> GameNode:
    if node.expanded:
        raise Exception("Should never happen")
    possible_states = get_all_possible_moves_for_side(node.parent.game_state["possible_game_state"], node.dice_outcome,
                                                      node.deciding_side)
    return random.choice(node.expand(possible_states.values()))


def rollout(game_state: GameState, side: Side, max_depth: int) -> Side:
    current_state :GameState = game_state
    current_side = side
    current_dices = select_random_dice_outcome()
    for _ in range(max_depth):
        current_state = get_possible_moves_sequence_for_side(current_state, current_dices, side)["possible_game_state"]
        result = is_game_over(current_state)
        if result is not None:
            return result
        current_side = other_side(current_side)
        current_dices = select_random_dice_outcome()
        side = other_side(side)
    return get_winner_based_on_score(current_state)


def get_winner_based_on_score(game_state: GameState) -> Side:
    if heuristic(game_state, Side.FIRST) < heuristic(game_state, Side.SECOND):
        return Side.FIRST
    else:
        return Side.SECOND


def heuristic(game_state: GameState, side: Side) -> int:
    value = 0
    home = 0 if side == Side.FIRST else 23
    for i, point in enumerate(game_state.board):
        if point.side == side:
            value += point.count * (abs(home - i) + 1)

    value += (game_state.first_hit if side == Side.FIRST else game_state.second_hit) * 25
    return value


def simulation_worker(args):
    side, game_state, dices, search_depth, searches_per_worker = args

    parent_node = GameNode({"possible_game_state": game_state, "moves_to_reach_it": []}, side=side)

    for _ in range(searches_per_worker):
        sequence: List[SearchStep]
        selected_dice_node: DiceNode
        sequence, selected_dice_node = selection(parent_node, dices)

        node_to_perform_rollout = expansion(selected_dice_node)
        sequence.append(SearchStep(node_to_perform_rollout.game_state, None))

        winner = rollout(node_to_perform_rollout.game_state["possible_game_state"], node_to_perform_rollout.side,
                         search_depth)

        backpropagation(parent_node, sequence, winner)

    return parent_node
