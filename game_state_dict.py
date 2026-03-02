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

    def append(self, state: PossibleGameState):
        key = game_state_key(state["possible_game_state"])
        self._data[key] = state  # overwrites duplicates

    def values(self) -> list[PossibleGameState]:
        return list(self._data.values())

    def __len__(self):
        return len(self._data)

    def extend(self, states: "UniqueGameStates"):
        for state in states.values():
            self.append(state)