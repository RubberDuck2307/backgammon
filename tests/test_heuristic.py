import pygammon
from typing import Optional, Tuple, Union

from pygammon import GameState, OutputType, InvalidMoveCode, Side, InputType
from pygammon.structures import Point

from ai.greedy_best_first_ai import GreedyBestFirstAi
from ai.human_input_ai import print_move


class GreedyOldHeuristicAi(GreedyBestFirstAi):
    def heuristic(self, game_state: GameState, maximalize_hits: bool = False) -> int:
        value = 0
        for i, point in enumerate(game_state.board):
            if point.side == self.side:
                value += point.count * (24 - i) if self.side == Side.FIRST else point.count * (i + 1)
            if maximalize_hits:
                value -= game_state.first_hit * 100 if self.side == Side.SECOND else game_state.second_hit * 100
        return value

    def evaluate_state(self, game_state: GameState) -> int:
        return self.heuristic(game_state, maximalize_hits=False)


class GreedyNewHeuristicAi(GreedyBestFirstAi):
    def evaluate_state(self, game_state: GameState) -> int:
        return self.heuristic_new(game_state, maximalize_hits=False)


class CompareHeuristics:
    def __init__(self):
        self.turn_counter = 0
        self.last_state: Optional[GameState] = None
        self.next_player = None
        self.done = False

    @staticmethod
    def empty_board():
        return [Point() for _ in range(24)]

    @staticmethod
    def make_state(board, first_hit=0, second_hit=0, first_borne=0, second_borne=0):
        return GameState(
            board=board,
            first_hit=first_hit,
            second_hit=second_hit,
            first_borne=first_borne,
            second_borne=second_borne,
        )

    @staticmethod
    def summarize_state(state: GameState) -> str:
        pieces = []
        for i, point in enumerate(state.board):
            if point.side is not None and point.count > 0:
                pieces.append(f"point {i + 1}: {point.side.name} x{point.count}")

        return (
            f"first_hit={state.first_hit}, first_borne={state.first_borne}, "
            f"second_hit={state.second_hit}, second_borne={state.second_borne}\n"
            + ", ".join(pieces)
        )

    def compare_choices(self, state: GameState, dice, side: Side):
        old_ai = GreedyOldHeuristicAi(side)
        new_ai = GreedyNewHeuristicAi(side)

        old_ai.update_game_state(state)
        new_ai.update_game_state(state)

        old_ai.update_available_moves(dice)
        new_ai.update_available_moves(dice)

        old_candidates = old_ai.get_all_possible_moves(old_ai.game_state, old_ai.available_moves)
        new_candidates = new_ai.get_all_possible_moves(new_ai.game_state, new_ai.available_moves)

        print("=" * 100)
        print(f"REAL TURN COMPARISON: player = {side.name}")
        print("Current state:")
        print(self.summarize_state(state))
        print(f"\nDice / move rolls: {dice}")
        print("=" * 100)

        print("\nOLD HEURISTIC ON GREEDY BEST-FIRST SEARCH")
        best_old_value = float("inf")
        best_old_moves = None
        best_old_index = None
        for idx, candidate in enumerate(old_candidates.values()):
            candidate_state = candidate["possible_game_state"]
            candidate_moves = candidate["moves_to_reach_it"]
            value = old_ai.evaluate_state(candidate_state)

            print(f"\nCandidate {idx + 1} -> old heuristic value = {value}")
            for move in candidate_moves:
                print("   ", end="")
                print_move(move)

            if value < best_old_value:
                best_old_value = value
                best_old_moves = candidate_moves
                best_old_index = idx + 1

        print("\nChosen by OLD heuristic:")
        print(f"candidate = {best_old_index}, value = {best_old_value}")
        for move in best_old_moves:
            print("   ", end="")
            print_move(move)

        print("\nNEW HEURISTIC ON GREEDY BEST-FIRST SEARCH")
        best_new_value = float("inf")
        best_new_moves = None
        best_new_index = None
        for idx, candidate in enumerate(new_candidates.values()):
            candidate_state = candidate["possible_game_state"]
            candidate_moves = candidate["moves_to_reach_it"]
            value = new_ai.evaluate_state(candidate_state)

            print(f"\nCandidate {idx + 1} -> new heuristic value = {value}")
            for move in candidate_moves:
                print("   ", end="")
                print_move(move)

            if value < best_new_value:
                best_new_value = value
                best_new_moves = candidate_moves
                best_new_index = idx + 1

        print("\nChosen by NEW heuristic:")
        print(f"candidate = {best_new_index}, value = {best_new_value}")
        for move in best_new_moves:
            print("   ", end="")
            print_move(move)

        print("\nINTERPRETATION")
        print("If the old heuristic gives many ties while the new one separates candidates,")
        print("then the new heuristic is more informative for Greedy Best-First Search.")
        print("=" * 100)

    def compare_static_pair(self, label, state_a, state_b, preferred_label, side=Side.FIRST):
        old_ai = GreedyOldHeuristicAi(side)
        new_ai = GreedyNewHeuristicAi(side)

        old_a = old_ai.evaluate_state(state_a)
        old_b = old_ai.evaluate_state(state_b)
        new_a = new_ai.evaluate_state(state_a)
        new_b = new_ai.evaluate_state(state_b)

        print("\n" + "=" * 100)
        print(f"STATIC TEST: {label}")
        print("=" * 100)

        print("\nState A:")
        print(self.summarize_state(state_a))
        print("\nState B:")
        print(self.summarize_state(state_b))

        print("\nScores")
        print(f"OLD heuristic: A = {old_a}, B = {old_b}")
        print(f"NEW heuristic: A = {new_a}, B = {new_b}")

        if old_a < old_b:
            old_pref = "A"
        elif old_b < old_a:
            old_pref = "B"
        else:
            old_pref = "TIE"

        if new_a < new_b:
            new_pref = "A"
        elif new_b < new_a:
            new_pref = "B"
        else:
            new_pref = "TIE"

        print("\nPreference")
        print(f"OLD heuristic prefers: {old_pref}")
        print(f"NEW heuristic prefers: {new_pref}")
        print(f"Expected strategically stronger state: {preferred_label}")

        old_ok = (old_pref == preferred_label)
        new_ok = (new_pref == preferred_label)

        print("\nInterpretation")
        print(f"OLD heuristic matches expected preference: {old_ok}")
        print(f"NEW heuristic matches expected preference: {new_ok}")

        if old_pref == "TIE":
            print("OLD heuristic gives a tie here, so it provides little guidance.")
        if new_pref == "TIE":
            print("NEW heuristic gives a tie here, so it provides little guidance.")
        if new_ok and not old_ok:
            print("NEW heuristic is better on this test because it captures the strategic feature.")
        elif old_ok and not new_ok:
            print("OLD heuristic is better on this test.")
        elif new_ok and old_ok:
            print("Both heuristics agree with the expected strategic preference.")
        else:
            print("Neither heuristic matches the expected strategic preference well.")

    def run_static_board_tests(self):
        ai_side = Side.FIRST

        # 1. Blots vs safer structure
        board_a = self.empty_board()
        board_a[5] = Point(Side.FIRST, 1)
        board_a[6] = Point(Side.FIRST, 1)
        board_a[7] = Point(Side.FIRST, 2)
        state_a = self.make_state(board_a)

        board_b = self.empty_board()
        board_b[5] = Point(Side.FIRST, 2)
        board_b[7] = Point(Side.FIRST, 2)
        state_b = self.make_state(board_b)

        self.compare_static_pair(
            "Blotty structure vs safer structure",
            state_a,
            state_b,
            preferred_label="B",
            side=ai_side,
        )

        # 2. Weak home board vs strong home board
        board_c = self.empty_board()
        board_c[0] = Point(Side.FIRST, 2)
        board_c[1] = Point(Side.FIRST, 1)
        board_c[2] = Point(Side.FIRST, 1)
        state_c = self.make_state(board_c)

        board_d = self.empty_board()
        board_d[0] = Point(Side.FIRST, 2)
        board_d[1] = Point(Side.FIRST, 2)
        board_d[2] = Point(Side.FIRST, 2)
        state_d = self.make_state(board_d)

        self.compare_static_pair(
            "Weak home board vs strong home board",
            state_c,
            state_d,
            preferred_label="B",
            side=ai_side,
        )

        # 3. No anchor vs anchor
        board_e = self.empty_board()
        board_e[10] = Point(Side.FIRST, 2)
        board_e[12] = Point(Side.FIRST, 2)
        state_e = self.make_state(board_e)

        board_f = self.empty_board()
        board_f[10] = Point(Side.FIRST, 2)
        board_f[20] = Point(Side.FIRST, 2)
        state_f = self.make_state(board_f)

        self.compare_static_pair(
            "No anchor vs anchor",
            state_e,
            state_f,
            preferred_label="B",
            side=ai_side,
        )

        # 4. Opponent not on bar vs opponent on bar
        board_g = self.empty_board()
        board_g[5] = Point(Side.FIRST, 2)
        board_g[7] = Point(Side.FIRST, 2)
        state_g = self.make_state(board_g, second_hit=0)

        board_h = self.empty_board()
        board_h[5] = Point(Side.FIRST, 2)
        board_h[7] = Point(Side.FIRST, 2)
        state_h = self.make_state(board_h, second_hit=1)

        self.compare_static_pair(
            "Opponent not on bar vs opponent on bar",
            state_g,
            state_h,
            preferred_label="B",
            side=ai_side,
        )

        # 5. Scattered made points vs connected blocking structure
        board_i = self.empty_board()
        board_i[2] = Point(Side.FIRST, 2)
        board_i[5] = Point(Side.FIRST, 2)
        board_i[8] = Point(Side.FIRST, 2)
        state_i = self.make_state(board_i)

        board_j = self.empty_board()
        board_j[2] = Point(Side.FIRST, 2)
        board_j[3] = Point(Side.FIRST, 2)
        board_j[4] = Point(Side.FIRST, 2)
        state_j = self.make_state(board_j)

        self.compare_static_pair(
            "Scattered points vs connected blocking structure",
            state_i,
            state_j,
            preferred_label="B",
            side=ai_side,
        )

        # 6. Less borne off vs more borne off
        board_k = self.empty_board()
        board_k[0] = Point(Side.FIRST, 2)
        board_k[1] = Point(Side.FIRST, 2)
        state_k = self.make_state(board_k, first_borne=0)

        board_l = self.empty_board()
        board_l[0] = Point(Side.FIRST, 2)
        board_l[1] = Point(Side.FIRST, 2)
        state_l = self.make_state(board_l, first_borne=3)

        self.compare_static_pair(
            "Less borne off vs more borne off",
            state_k,
            state_l,
            preferred_label="B",
            side=ai_side,
        )

        # 7. Mixed realistic position
        board_m = self.empty_board()
        board_m[1] = Point(Side.FIRST, 2)
        board_m[4] = Point(Side.FIRST, 1)
        board_m[5] = Point(Side.FIRST, 1)
        board_m[12] = Point(Side.FIRST, 2)
        board_m[19] = Point(Side.SECOND, 2)
        state_m = self.make_state(board_m)

        board_n = self.empty_board()
        board_n[1] = Point(Side.FIRST, 2)
        board_n[4] = Point(Side.FIRST, 2)
        board_n[12] = Point(Side.FIRST, 2)
        board_n[19] = Point(Side.SECOND, 2)
        state_n = self.make_state(board_n)

        self.compare_static_pair(
            "Mixed realistic position: two blots vs made point",
            state_m,
            state_n,
            preferred_label="B",
            side=ai_side,
        )

    def do_move_handler(self, side: Side) -> Tuple[InputType, Optional[Tuple[int, Optional[int]]]]:
        raise SystemExit("Stopping before actual move execution; comparison already printed.")

    def current_game_state_handler(
        self,
        output_type: OutputType,
        data: Union[GameState, Tuple[int, int], InvalidMoveCode, Side],
        side: Optional[Side] = None,
    ):
        if output_type == OutputType.GAME_STATE:
            self.last_state = data
            self.turn_counter += 1

        elif output_type == OutputType.TURN_ROLLS:
            self.next_player = Side.FIRST if data[0] > data[1] else Side.SECOND

        elif output_type == OutputType.MOVE_ROLLS and not self.done:
            self.done = True
            self.compare_choices(self.last_state, data, self.next_player)
            print("\n\nRUNNING STATIC BOARD TESTS FOR HEURISTIC FUNCTIONALITY...")
            self.run_static_board_tests()
            raise SystemExit("Comparison finished successfully.")

        elif output_type == OutputType.INVALID_MOVE:
            print(f"Invalid move by {side}: {data}")


tester = CompareHeuristics()

try:
    pygammon.run(tester.do_move_handler, tester.current_game_state_handler)
except SystemExit as e:
    print(e)