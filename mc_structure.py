from game_state_dict import game_state_key
from game_state_generator import PossibleGameState
from threading import Lock


class GameNode:
    game_state: PossibleGameState
    next_game_states: dict[tuple, "GameNode"]
    parent: "GameNode"
    visits: int
    wins: int
    losses: int

    def __init__(self, state: PossibleGameState, parent=None):
        self.game_state = state
        self.parent = parent
        self.visits = 0
        self.wins = 0
        self.losses = 0
        self.next_game_states = {}


    def add_child(self, child_state):
        key = game_state_key(child_state["possible_game_state"])
        if key in self.next_game_states:
            return self.next_game_states[key]
        child_node = GameNode(child_state, parent=self)
        self.next_game_states[key] = child_node
        return child_node

    def find_child(self, state) -> "GameNode":
        key = game_state_key(state)
        return self.next_game_states.get(key)

    def update_sequence(self, search_sequence, is_win):
        self.visits += 1
        if is_win:
            self.wins += 1
        else:
            self.losses += 1
        if len(search_sequence) == 1:
            return
        child = self.find_child(search_sequence[0]["possible_game_state"])
        if child is None:
            child = self.add_child(search_sequence[0])
        child.update_sequence(search_sequence[1:], is_win)

    def best_child(self) -> PossibleGameState:
        best_score = -1
        best_child = None
        for child in self.next_game_states.values():
            score = child.wins / child.visits if child.visits > 0 else 0
            if score > best_score:
                best_score = score
                best_child = child
        return best_child.game_state