from time import sleep
from typing import Union, Tuple, Optional

import pygammon
from basic_ai import BasicAi
from pygammon import GameState, OutputType, InvalidMoveCode, Side, InputType

from renderer import BackgammonRenderer

renderer = BackgammonRenderer()

firstAi = BasicAi(Side.FIRST)
secondAi = BasicAi(Side.SECOND)


def do_move_handler(side: Side) -> Tuple[InputType, Optional[Tuple[int, Optional[int]]]]:
    print("input",  Side(side))
    sleep(5) #sleep between turns
    return firstAi.move() if side == Side.FIRST else secondAi.move()


def current_game_state_handler(output_type: OutputType,
           data: Union[GameState, Tuple[int, int], InvalidMoveCode, Side],
           side: Optional[Side] = None):
    print("output", output_type, side)
    if isinstance(data, GameState):
        firstAi.update_game_state(data)
        secondAi.update_game_state(data)
        renderer.render(data)

    elif isinstance(data, tuple):
        first, second = data
        print("rools", first, second)

    elif isinstance(data, InvalidMoveCode):
        print("Invalid:", data)

    elif isinstance(data, Side):
        print("Side:", data)

#Check https://pygammon.readthedocs.io/en/latest/protocol.html
pygammon.run(do_move_handler, current_game_state_handler)
