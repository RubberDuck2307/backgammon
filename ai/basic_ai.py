from ai.ai_abstract import AiAbstractClass
from ai.human_input_ai import print_move
from game_state_dict import UniqueGameStates
from game_state_generator import Move
from pygammon import GameState, Side


class BasicAi(AiAbstractClass):

    def move(self) -> Move:
        if self.chosen_move is None:
            available_moves: UniqueGameStates = self.get_all_possible_moves(self.game_state, self.available_moves)
            if len(available_moves.values()) == 0:
                self.get_all_possible_moves(self.game_state, self.available_moves) # for debug
                raise Exception("No possible moves to make, the code is not ready for this")
            min_value = 9999
            index_of_best_move = 0
            for move in available_moves.values():
                value = self.heuristic(move["possible_game_state"])
                if value < min_value:
                    min_value = value
                    index_of_best_move = available_moves.values().index(move)
            self.chosen_move = available_moves.values()[index_of_best_move]["moves_to_reach_it"]
            for move in self.chosen_move:
                print_move(move)
        return self.proceed_with_move()

    def heuristic(self, game_state: GameState) -> int:
        value = 0
        for i, point in enumerate(game_state.board):
            if point.side == self.side:
                value += point.count * (24 - i) if self.side == Side.FIRST else point.count * (i + 1)
        return value

