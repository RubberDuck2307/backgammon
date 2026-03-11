import pygammon
from typing import Optional, Tuple, Union

from pygammon import GameState, OutputType, InvalidMoveCode, Side, InputType

from ai.greedy_best_first_ai import GreedyBestFirstAi
from ai.human_input_ai import print_move


class GreedyNewHeuristicAi(GreedyBestFirstAi):
    def evaluate_state(self, game_state: GameState) -> int:
        return self.heuristic_new(game_state, maximalize_hits=False)


class Game:
    def __init__(self):
        self.turn_counter = 0
        self.firstAi = GreedyNewHeuristicAi(Side.FIRST)
        self.secondAi = GreedyNewHeuristicAi(Side.SECOND)

        self.next_player = None
        self.last_state: Optional[GameState] = None

    def do_move_handler(self, side: Side) -> Tuple[InputType, Optional[Tuple[int, Optional[int]]]]:
        move = self.firstAi.move() if side == Side.FIRST else self.secondAi.move()
        print(f"{self.turn_counter}. move by player: {Side(side).name}")
        print_move(move)
        return move

    @staticmethod
    def summarize_state(state: GameState) -> str:
        pieces = []
        for i, point in enumerate(state.board):
            if point.side is not None and point.count > 0:
                pieces.append(f"point {i + 1}: {point.side.name} x{point.count}")

        board_text = ", ".join(pieces)
        return (
            f"first_hit={state.first_hit}, first_borne={state.first_borne}, "
            f"second_hit={state.second_hit}, second_borne={state.second_borne}\n"
            f"{board_text}"
        )

    def current_game_state_handler(
        self,
        output_type: OutputType,
        data: Union[GameState, Tuple[int, int], InvalidMoveCode, Side],
        side: Optional[Side] = None,
    ):
        if output_type == OutputType.GAME_STATE:
            self.firstAi.update_game_state(data)
            self.secondAi.update_game_state(data)
            self.last_state = data
            self.turn_counter += 1

            print("\nGAME STATE UPDATED")
            print(self.summarize_state(data))

        elif output_type == OutputType.TURN_ROLLS:
            self.next_player = Side.FIRST if data[0] > data[1] else Side.SECOND
            print("Turn rolls:", data, "Next player:", self.next_player)

        elif output_type == OutputType.MOVE_ROLLS:
            print(f"\nMOVE ROLLS for player: {self.next_player}", data)

            if self.next_player == Side.FIRST:
                self.firstAi.update_available_moves(data)
                self.next_player = Side.SECOND
            elif self.next_player == Side.SECOND:
                self.secondAi.update_available_moves(data)
                self.next_player = Side.FIRST

        elif output_type == OutputType.INVALID_MOVE:
            print(f"Invalid move by {side}: {data}")

        elif output_type == OutputType.GAME_WON:
            print("\nGAME WON")
            print(f"Winner: {data.name}")
            if self.last_state is not None:
                print("Final state:")
                print(self.summarize_state(self.last_state))


game = Game()
pygammon.run(game.do_move_handler, game.current_game_state_handler)