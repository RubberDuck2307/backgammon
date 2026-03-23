import random

from ai.ai_abstract import AiAbstractClass
from game_state_dict import UniqueGameStates, Move
from game_state_generator import get_all_possible_moves


class RandomAi(AiAbstractClass):

    def move(self) -> Move:
        if self._chosen_move_ is None:
            available_moves: UniqueGameStates = get_all_possible_moves(self.game_state, self.available_moves, self.side)
            chosen_move = random.choice(available_moves.values())["moves_to_reach_it"]
            self.chose_move(chosen_move)
        return self.proceed_with_move()