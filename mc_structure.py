import math
from typing import List, Tuple

from pygammon import Side, GameState

from game_state_dict import game_state_key
from game_state_generator import PossibleGameState
from generators.stochastic_generator import other_side


class SearchStep:
    chosen_game_state: PossibleGameState
    dice_outcome: Tuple[int, int]

    def __init__(self, chosen_game_state: PossibleGameState, dice_outcome: Tuple[int, int]):
        self.chosen_game_state = chosen_game_state
        self.dice_outcome = dice_outcome


class DiceNode:
    parent: "GameNode"
    dice_outcome: tuple[int, int]
    next_game_states: dict[tuple, "GameNode"]
    unvisited_children: List["GameNode"]
    deciding_side: Side
    visits: int
    wins: int
    expanded: bool = False

    def add_child(self, child_state: PossibleGameState):
        key = game_state_key(child_state["possible_game_state"])
        if key in self.next_game_states:
            return self.next_game_states[key]
        child_node = GameNode(child_state, other_side(self.deciding_side), parent=self)
        self.next_game_states[key] = child_node
        self.unvisited_children.append(child_node)
        return child_node

    def expand(self, child_states: List[PossibleGameState]) -> List["GameNode"]:
        expanded_nodes = []
        self.expanded = True
        for child_state in child_states:
            expanded_nodes.append(self.add_child(child_state))
        return expanded_nodes

    def __init__(self, dice_outcome: tuple[int, int], deciding_side: Side, parent: "GameNode" = None):
        self.parent = parent
        self.dice_outcome = dice_outcome
        self.deciding_side = deciding_side
        self.visits = 0
        self.wins = 0
        self.next_game_states = {}
        self.unvisited_children = []

    def select_ucb_child(self, exploration: float = 1.4):
        if len(self.unvisited_children) > 0:
            return self.unvisited_children.pop()

        best_score = float("-inf")
        best_child = None

        for child in self.next_game_states.values():

            opponent_winrate =  child.wins / child.visits
            my_winrate = 1 - opponent_winrate
            exploration_term = exploration * math.sqrt(
                math.log(self.visits) / child.visits
            )

            score = my_winrate + exploration_term

            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def back_propagate(self, search_sequence: List[SearchStep], winner: Side):
        self.visits += 1
        if winner == self.deciding_side:
            self.wins += 1
        child = self.next_game_states.get(game_state_key(search_sequence[0].chosen_game_state["possible_game_state"]))
        if child is not None:
            child.back_propagate(search_sequence, winner)

    def find_child(self, game_state: GameState):
        return self.next_game_states.get(game_state_key(game_state))

    def best_child(self, side, n: int = 3) -> PossibleGameState:
        if self.deciding_side != side:
            raise ValueError("Can only find best child for the side that made the decision at this node")
        children = list(self.next_game_states.values())

        top_children = sorted(children, key=lambda c: c.visits, reverse=True)[:n]

        best_child = None
        best_score = -1

        for child in top_children:
            if child.visits == 0:
                score = 0
            else:
                score = 1 - (child.wins / child.visits)

            if score > best_score:
                best_score = score
                best_child = child

        if best_child is None:
            raise ValueError("No best child found, this should not happen if there are children")

        # print(f"Best child visits: {best_child.visits}, wins: {best_child.visits - best_child.wins}, win rate: { 1 - (best_child.wins / best_child.visits)}")
        return best_child.game_state

    # def best_child(self, by_winrate: bool = True) -> PossibleGameState:
    #     best_score = -1
    #     best_child = None
    #     for child in self.next_game_states.values():
    #         if by_winrate:
    #             if child.visits == 0:
    #                 score = 0  # avoid division by zero
    #             else:
    #                 score = child.wins / child.visits
    #         else:
    #             score = child.visits
    #
    #         if score > best_score:
    #             best_score = score
    #             best_child = child
    #
    #     return best_child.game_state

    def merge(self, other: "DiceNode"):
        if self.dice_outcome != other.dice_outcome:
            raise ValueError("Can only merge nodes with the same dice outcome")

        self.visits += other.visits
        self.wins += other.wins

        for game_state_key, other_child in other.next_game_states.items():
            if game_state_key in self.next_game_states:
                self.next_game_states[game_state_key].merge(other_child)
            else:
                self.next_game_states[game_state_key] = other_child



class GameNode:
    game_state: PossibleGameState
    next_dice_nodes: dict[tuple, DiceNode]
    visits: int
    side: Side
    wins: int

    def __init__(self, state: PossibleGameState, side: Side, parent=None):
        self.parent = parent
        self.game_state = state
        self.visits = 0
        self.wins = 0
        self.next_dice_nodes = {}
        self.side = side

    def find_or_add_child(self, dice_outcome: tuple[int, int]):
        if dice_outcome in self.next_dice_nodes:
            return self.next_dice_nodes[dice_outcome]
        child_node = DiceNode(dice_outcome, self.side, parent=self)
        self.next_dice_nodes[dice_outcome] = child_node
        return child_node

    def find_child(self, dice_outcome: tuple[int, int]):
        return self.next_dice_nodes.get(dice_outcome)

    def back_propagate(self, search_sequence: List[SearchStep], winner: Side):
        self.visits += 1
        if winner == self.side:
            self.wins += 1
        if search_sequence[0].dice_outcome is None:
            return
        child = self.find_child(search_sequence[0].dice_outcome)
        child.back_propagate(search_sequence[1:], winner)

    def merge(self, other: "GameNode"):
        if self.game_state != other.game_state:
            print("Can only merge nodes with the same game state")
            return

        self.visits += other.visits
        self.wins += other.wins

        for dice_outcome, other_child in other.next_dice_nodes.items():
            if dice_outcome in self.next_dice_nodes:
                self.next_dice_nodes[dice_outcome].merge(other_child)
            else:
                self.next_dice_nodes[dice_outcome] = other_child