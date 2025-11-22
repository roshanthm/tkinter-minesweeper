# 🧩 Minesweeper (Python Tkinter)

A complete classic Minesweeper game built in Python using Tkinter.
No external libraries required — works on all versions of Python 3.x.

---

## 🎮 Features

- Left-click to reveal a tile
- Right-click (or Ctrl+Click on Mac) to place/remove flags
- Auto-expand empty areas (0 adjacent mines)
- Win / Lose detection
- Restart button
- Choose difficulty:
  - Easy – 9x9 with 10 mines  
  - Medium – 16x16 with 40 mines  
  - Hard – 24x24 with 99 mines
- Emoji support: 💣 mines, 🚩 flags  
  (falls back to text if emojis unsupported)

---

## 🖥️ Requirements

- Python 3.x
- Tkinter (included with Python on Windows/macOS)

Linux users may need:  
```bash
sudo apt install python3-tk
