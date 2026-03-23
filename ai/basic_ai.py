import random

from engine.engine_types import GameState, Side

from ai.ai_abstract import AiAbstractClass
from game_state_dict import UniqueGameStates, Move
from game_state_generator import get_all_possible_moves


class BasicAi(AiAbstractClass):

    def move(self) -> Move:
        if self._chosen_move_ is None:
            if self.log:
                print("Choosing move for player", self.side)
            available_moves: UniqueGameStates = get_all_possible_moves(self.game_state, self.available_moves, self.side)
            if len(available_moves.values()) == 0 or available_moves.max_moves == 0:
                raise Exception("No possible moves to make, the code is not ready for this")
            min_value = 9999
            index_of_best_move = 0
            for move in available_moves.values():
                value = self.heuristic(move["possible_game_state"])
                if value < min_value:
                    min_value = value
                    index_of_best_move = available_moves.values().index(move)
            chosen_move = available_moves.values()[index_of_best_move]["moves_to_reach_it"]
            self.chose_move(chosen_move)
            # for move in chosen_move:
            #     print_move(move)
        return self.proceed_with_move()
    #chooses the move with the lowest heuristic value
    def heuristic(self, game_state: GameState) -> int:
        value = 0
        home = 0 if self.side == Side.FIRST else 23
        for i, point in enumerate(game_state.board):
            if point.side == self.side:
                value += point.count * ((home - i) ** 2 + 1)

        value += (game_state.first_hit if self.side == Side.FIRST else game_state.second_hit) * 25 ** 2
        return value