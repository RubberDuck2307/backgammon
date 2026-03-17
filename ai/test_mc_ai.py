from ai.ai_abstract import AiAbstractClass
from ai.human_input_ai import print_move
from game_state_dict import Move
from generators.monter_carlo_generator import get_possible_moves_sequence_for_side


class TestMonteCarloAi(AiAbstractClass):
    def move(self) -> Move:
        if self._chosen_move_ is None:
            chosen_move = get_possible_moves_sequence_for_side(self.game_state, self.available_moves, self.side)["moves_to_reach_it"]
            self.chose_move(chosen_move)
            if self.log:
                print("player :", self.side, "chosing moves:")
                for move in chosen_move:
                    print_move(move)
        return self.proceed_with_move()
