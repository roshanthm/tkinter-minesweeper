import tkinter as tk
from tkinter import messagebox, simpledialog
import random
from dataclasses import dataclass

@dataclass
class Cell:
    is_mine: bool = False
    is_revealed: bool = False
    is_flagged: bool = False
    adj_mines: int = 0

class GameLogic:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = []
        self.first_click_done = False
        self.game_over = False
        self._init_empty_board()

    def _init_empty_board(self):
        self.board = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]
        self.first_click_done = False
        self.game_over = False

    def within_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def neighbors(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self.within_bounds(nr, nc):
                    yield nr, nc

    def place_mines(self, safe_r, safe_c):
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        forbidden = {(safe_r, safe_c)}
        for nr, nc in list(self.neighbors(safe_r, safe_c)):
            forbidden.add((nr, nc))
        positions = [p for p in positions if p not in forbidden]
        random.shuffle(positions)

        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c].is_mine = False
                self.board[r][c].adj_mines = 0

        for (r, c) in positions[:self.mines]:
            self.board[r][c].is_mine = True

        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c].adj_mines = sum(
                    1 for nr, nc in self.neighbors(r, c) if self.board[nr][nc].is_mine
                )

    def reveal_cell(self, r, c):
        if self.game_over:
            return []
        cell = self.board[r][c]
        if cell.is_flagged or cell.is_revealed:
            return []

        revealed = []
        if not self.first_click_done:
            self.place_mines(r, c)
            self.first_click_done = True

        cell.is_revealed = True
        revealed.append((r, c))

        if cell.is_mine:
            self.game_over = True
            return revealed

        if cell.adj_mines == 0:
            queue = [(r, c)]
            while queue:
                cr, cc = queue.pop()
                for nr, nc in self.neighbors(cr, cc):
                    n = self.board[nr][nc]
                    if not n.is_revealed and not n.is_flagged and not n.is_mine:
                        n.is_revealed = True
                        revealed.append((nr, nc))
                        if n.adj_mines == 0:
                            queue.append((nr, nc))
        return revealed

    def toggle_flag(self, r, c):
        cell = self.board[r][c]
        if cell.is_revealed:
            return False
        cell.is_flagged = not cell.is_flagged
        return cell.is_flagged

    def check_victory(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.board[r][c]
                if not cell.is_mine and not cell.is_revealed:
                    return False
        return True

    def reveal_all_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c].is_mine:
                    self.board[r][c].is_revealed = True


class MinesweeperGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Minesweeper")

        self.default_sizes = {
            "Easy": (9, 9, 10),
            "Medium": (16, 16, 40),
            "Hard": (24, 24, 99)
        }

        self.rows, self.cols, self.mines = 10, 10, 15

        self.top_frame = tk.Frame(master, bg="#f0f0f0")
        self.top_frame.pack(fill=tk.X)

        self.restart_button = tk.Button(self.top_frame, text="Restart", command=self.new_game)
        self.restart_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.flag_label = tk.Label(self.top_frame, text="Flags: 0", bg="#f0f0f0")
        self.flag_label.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(self.top_frame, text="", bg="#f0f0f0")
        self.status_label.pack(side=tk.RIGHT, padx=10)

        self._create_menu()

        self.board_frame = tk.Frame(master)
        self.board_frame.pack(pady=10)

        self.game = None
        self.buttons = []
        self.flag_count = 0

        self.new_game()

    def _create_menu(self):
        menubar = tk.Menu(self.master)
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.new_game)

        diff_menu = tk.Menu(game_menu, tearoff=0)
        for label in self.default_sizes:
            diff_menu.add_command(label=label, command=lambda lvl=label: self.set_difficulty(lvl))

        game_menu.add_cascade(label="Difficulty", menu=diff_menu)
        menubar.add_cascade(label="Game", menu=game_menu)

        self.master.config(menu=menubar)

    def new_game(self):
        for w in self.board_frame.winfo_children():
            w.destroy()

        self.game = GameLogic(self.rows, self.cols, self.mines)
        self.buttons = []
        self.flag_count = 0
        self.flag_label.config(text="Flags: 0")
        self.status_label.config(text="")

        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                btn = tk.Button(self.board_frame, width=2, height=1,
                                command=lambda rr=r, cc=c: self.left_click(rr, cc))
                btn.grid(row=r, column=c)

                btn.bind("<Button-3>", lambda e, rr=r, cc=c: self.right_click(rr, cc))
                btn.bind("<Control-Button-1>", lambda e, rr=r, cc=c: self.right_click(rr, cc))

                row.append(btn)
            self.buttons.append(row)

    def set_difficulty(self, lvl):
        self.rows, self.cols, self.mines = self.default_sizes[lvl]
        self.new_game()

    def update_button(self, r, c):
        cell = self.game.board[r][c]
        btn = self.buttons[r][c]

        if cell.is_revealed:
            btn.config(relief=tk.SUNKEN, state=tk.DISABLED, bg="#ffffff")
            if cell.is_mine:
                btn.config(text="💣", fg="red", bg="#ffcccc")
            elif cell.adj_mines > 0:
                btn.config(text=str(cell.adj_mines))
            else:
                btn.config(text="")
        else:
            if cell.is_flagged:
                btn.config(text="🚩", bg="#ffe9c6")
            else:
                btn.config(text="", bg="#f0f0f0", relief=tk.RAISED, state=tk.NORMAL)

    def left_click(self, r, c):
        if self.game.game_over:
            return
        revealed = self.game.reveal_cell(r, c)
        for (rr, cc) in revealed:
            self.update_button(rr, cc)

        if self.game.game_over:
            self.game.reveal_all_mines()
            for rr in range(self.rows):
                for cc in range(self.cols):
                    self.update_button(rr, cc)
            messagebox.showinfo("Game Over", "You hit a mine!")
            self.status_label.config(text="You Lost.")
            return

        if self.game.check_victory():
            messagebox.showinfo("Victory", "You won!")
            self.status_label.config(text="You Won!")
            self.game.game_over = True

    def right_click(self, r, c):
        if self.game.game_over:
            return
        flagged = self.game.toggle_flag(r, c)

        if flagged:
            self.flag_count += 1
        else:
            self.flag_count -= 1
        self.flag_label.config(text=f"Flags: {self.flag_count}")

        self.update_button(r, c)

def main():
    root = tk.Tk()
    MinesweeperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
