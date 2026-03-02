from typing import Tuple, Optional
import tkinter as tk

from pygammon import GameState, Side

BG = "#1a1a1a"
BOARD_BG = "#2b2318"
POINT_A = "#8b3a2a"  # dark red triangle
POINT_B = "#c8a96e"  # cream triangle
CHECKER_1 = "#e8dcc8"  # first player  (light)
CHECKER_2 = "#3a2a1a"  # second player (dark)
CHECKER_BORDER = "#111111"
BAR_COL = "#1e1a14"
TEXT_COL = "#c8a96e"
HIT_COL = "#e8dcc8"
LABEL_COL = "#706050"


# ── renderer ──────────────────────────────────────────────────────────────────

class BackgammonRenderer:
    """
    Minimal, non-interactive backgammon board renderer.

    Usage:
        renderer = BackgammonRenderer()
        renderer.render(game_state)   # call any time to re-render
        renderer.run()                # start tkinter main loop (blocking)

    For integration with an external event loop, skip run() and call
    renderer.root.update() manually.
    """
    render_counter = 0
    CELL_W = 52  # width of each point column
    CELL_H = 220  # height of each point (triangle area)
    BAR_W = 48
    MARGIN = 16
    CHECKER_R = 18  # checker radius
    PAD_TOP = 40  # space for point labels
    PAD_BOT = 40

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Backgammon")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.started = False

        total_w = self.MARGIN * 2 + 12 * self.CELL_W + self.BAR_W
        total_h = self.PAD_TOP + 2 * self.CELL_H + self.PAD_BOT + 60  # 60 for bar labels

        self.canvas = tk.Canvas(
            self.root,
            width=total_w, height=total_h,
            bg=BOARD_BG, highlightthickness=0
        )
        self.canvas.pack(padx=16, pady=16)

        self._W = total_w
        self._H = total_h
        self._state: Optional[GameState] = None

    # public ──────────────────────────────────────────────────────────────────

    def render(self, state: GameState):
        """Accepts a GameState and redraws the whole board."""
        self._state = state
        self.canvas.delete("all")
        self._draw_board()
        self._draw_labels()
        self._draw_pieces(state)
        self._draw_bar(state)
        self._draw_borne(state)
        self.root.update_idletasks()
        self.root.update()

        snapshot_canvas(self.canvas, filename=f"snap_{self.render_counter}.png")
        self.render_counter += 1

    def _point_x(self, col: int) -> int:
        """Left x-coordinate of the col-th column (0-11 left half, 12-23 right half)."""

        if col <= 11:
            x = self.MARGIN + ((12 - col) * self.CELL_W)
            if col > 5:
                x -= self.BAR_W

        if col > 11:
            x = self.MARGIN + (col - 12) * self.CELL_W
            if col > 17:
                x += self.BAR_W
        return x

    def _draw_triangle(self, col: int, top: bool, color: str):
        x = self._point_x(col)
        cx = x + self.CELL_W // 2

        if top:
            y0 = self.PAD_TOP
            y1 = self.PAD_TOP + self.CELL_H
        else:
            y0 = self._H - self.PAD_BOT
            y1 = self._H - self.PAD_BOT - self.CELL_H

        self.canvas.create_polygon(
            x, y0,
            x + self.CELL_W, y0,
            cx, y1,
            fill=color, outline=""
        )

    def _draw_board(self):
        # outer board rect
        self.canvas.create_rectangle(
            self.MARGIN, self.PAD_TOP,
            self._W - self.MARGIN, self._H - self.PAD_BOT,
            fill=BOARD_BG, outline=TEXT_COL, width=2
        )
        # bar
        bx = self.MARGIN + 6 * self.CELL_W
        self.canvas.create_rectangle(
            bx, self.PAD_TOP,
            bx + self.BAR_W, self._H - self.PAD_BOT,
            fill=BAR_COL, outline=TEXT_COL, width=1
        )

        for i in range(24):
            color = POINT_A if i % 2 == 0 else POINT_B
            top = i >= 12  # points 12-23 are drawn on top
            self._draw_triangle(i, top, color)

    def _draw_labels(self):
        """Point numbers 1-24."""
        font = ("Courier", 9)
        for i in range(24):
            cx = self._point_x(i) + self.CELL_W // 2
            if i < 12:
                y = self._H - self.PAD_BOT + 12
            else:
                y = self.PAD_TOP - 12

            self.canvas.create_text(cx, y, text=str(i + 1), fill=LABEL_COL, font=font)

    def _checker_color(self, side: Side) -> Tuple[str, str]:
        if side == Side.FIRST:
            return CHECKER_1, "#888877"
        else:
            return CHECKER_2, "#7a5a3a"

    def _draw_checker_stack(self, cx: int, base_y: int, direction: int,
                            side: Side, count: int):
        """
        Draw a stack of checkers.
        direction: +1 = stack grows downward (top triangles), -1 = upward (bottom).
        """
        fill, outline = self._checker_color(side)
        r = self.CHECKER_R
        step = r * 2 - 2  # slight overlap

        for k in range(min(count, 5)):
            cy = base_y + direction * (r + k * step)
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=fill, outline=outline, width=2
            )
            if count > 5 and k == 4:
                # show overflow number
                self.canvas.create_text(
                    cx, cy, text=str(count),
                    fill=BG if side == Side.FIRST else CHECKER_1,
                    font=("Courier", 9, "bold")
                )

    def _draw_pieces(self, state: GameState):
        for i, point in enumerate(state.board):
            if point.count == 0 or point.side is None:
                continue

            cx = self._point_x(i) + self.CELL_W // 2

            if i >= 12:
                base_y = self.PAD_TOP
                direction = 1
            else:
                base_y = self._H - self.PAD_BOT
                direction = -1

            self._draw_checker_stack(cx, base_y, direction, point.side, point.count)

    def _bar_cx(self) -> int:
        return self.MARGIN + 12 * self.CELL_W//2 + self.BAR_W // 2

    def _draw_bar(self, state: GameState):
        """Draw hit checkers on the bar."""
        bx = self._bar_cx()
        font = ("Courier", 8)

        if state.first_hit:
            self._draw_checker_stack(bx, self._H - self.PAD_BOT, -1,
                                     Side.FIRST, state.first_hit)
            self.canvas.create_text(bx, self._H - self.PAD_BOT - 10,
                                    text="bar", fill=LABEL_COL, font=font)

        if state.second_hit:
            self._draw_checker_stack(bx, self.PAD_TOP, 1,
                                     Side.SECOND, state.second_hit)
            self.canvas.create_text(bx, self.PAD_TOP + 10,
                                    text="bar", fill=LABEL_COL, font=font)

    def _draw_borne(self, state: GameState):
        """Simple borne-off counts at the sides."""
        font = ("Courier", 11)
        x = self._W - self.MARGIN + 4

        self.canvas.create_text(
            x, self._H // 4,
            text=f"↑{state.second_borne}", fill=CHECKER_2,
            font=font, anchor="w"
        )
        self.canvas.create_text(
            x, 3 * self._H // 4,
            text=f"↓{state.first_borne}", fill=CHECKER_1,
            font=font, anchor="w"
        )

from PIL import Image


def snapshot_canvas(canvas, filename="snapshot.png"):
    # Export canvas as PostScript
    canvas.postscript(file="temp.ps", colormode='color')

    img = Image.open("temp.ps")
    img.save(filename)
