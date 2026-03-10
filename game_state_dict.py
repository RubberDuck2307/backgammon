from pygammon import GameState

from game_state_generator import PossibleGameState


def game_state_key(gs: GameState) -> tuple:
    board_key = tuple(
        (point.side, point.count)
        for point in gs.board
    )

    return (
        board_key,
        gs.first_hit,
        gs.first_borne,
        gs.second_hit,
        gs.second_borne,
    )
class UniqueGameStates:
    def __init__(self):
        self._data: dict[tuple, PossibleGameState] = {}
        self.max_moves: int = 0

    def append(self, state: PossibleGameState):
        moves_used = len(state["moves_to_reach_it"])

        if moves_used < self.max_moves:
            return

        key = game_state_key(state["possible_game_state"])

        # If this state uses more moves than previous, reset the dict
        if moves_used > self.max_moves:
            self._data = {}
            self.max_moves = moves_used

        # Add / overwrite the state
        self._data[key] = state

    def values(self) -> list[PossibleGameState]:
        return list(self._data.values())

    def __len__(self):
        return len(self._data)

    def extend(self, states: "UniqueGameStates"):
        for state in states.values():
            self.append(state)