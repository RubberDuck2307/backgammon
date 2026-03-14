from ai.ai_abstract import AiAbstractClass
from ai.human_input_ai import print_move
from game_state_dict import UniqueGameStates, Move
from game_state_generator import  get_all_possible_moves
from pygammon import GameState, Side


class BasicAi(AiAbstractClass):

    def move(self) -> Move:
        if self._chosen_move_ is None:
            available_moves: UniqueGameStates = get_all_possible_moves(self.game_state, self.available_moves, self.side)
            if len(available_moves.values()) == 0 or available_moves.max_moves == 0:
                raise Exception("No possible moves to make, the code is not ready for this")
            min_value = 9999
            index_of_best_move = 0
            for move in available_moves.values():
                value = self.heuristic(move["possible_game_state"], maximalize_hits=False)
                if value < min_value:
                    min_value = value
                    index_of_best_move = available_moves.values().index(move)
            chosen_move = available_moves.values()[index_of_best_move]["moves_to_reach_it"]
            self.chose_move(chosen_move)
            print("player :", self.side, "chosing moves:")
            for move in chosen_move:
                print_move(move)
        return self.proceed_with_move()
#chooses the move with the lowest heuristic value
    def heuristic(self, game_state: GameState, maximalize_hits:bool = False) -> int:
        value = 0
        for i, point in enumerate(game_state.board):
            if point.side == self.side:
                value += point.count * (24 - i) if self.side == Side.FIRST else point.count * (i + 1)
            if maximalize_hits:
                value -= game_state.first_hit * 100 if self.side == Side.SECOND else game_state.second_hit * 100
        return value
        