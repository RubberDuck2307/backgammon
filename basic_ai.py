from typing import Tuple, Optional

from pygammon import GameState, InputType

from ai_abstract import AiAbstractClass


class BasicAi(AiAbstractClass):
    my_points_locations = {}
    enemy_points_locations = {}

    def move(self) -> Tuple[InputType, Optional[Tuple[int, Optional[int]]]]:
        return InputType.MOVE, (0, 5)

    def update_game_state(self, game_state: GameState):
        super().update_game_state(game_state)
