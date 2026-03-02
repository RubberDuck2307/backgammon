from ai.ai_abstract import AiAbstractClass
from game_state_dict import UniqueGameStates
from game_state_generator import Move, PossibleGameState


class HumanInputAI(AiAbstractClass):

    def move(self) -> Move:
        if self.chosen_move is None:
            available_moves: UniqueGameStates = self.get_all_possible_moves(self.game_state, self.available_moves)
            print("Dices:", self.available_moves)
            for i, move in enumerate(available_moves.values()):
                print_available_move(move, i)

            move_index = int(input("Enter the index of the move you want to make: "))
            self.chosen_move = available_moves.values()[move_index]["moves_to_reach_it"]
        move_to_make = self.chosen_move[len(self.chosen_move) - self.move_counter]
        self.move_counter -= 1
        if self.move_counter == 0:
            self.chosen_move = None
        return move_to_make


def print_available_move(move: PossibleGameState, move_index: int):
    print(f"Move {move_index}:")
    for move in move["moves_to_reach_it"]:
        print_move(move)

def print_move(move: Move):
    if move[1][1] is None:
        print("- Restore token from bar using dice index", move[1][0], )
    else:
        print("- Move token from point", move[1][1] + 1, "using dice", move[1][0])