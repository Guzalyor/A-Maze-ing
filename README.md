*This project has been created as part of the 42 curriculum by gikromov, mtousian.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python. It reads a configuration
file, generates a random (but reproducible) maze, writes it to an output file
using a hexadecimal wall encoding, solves it, and draws it in the terminal
with the shortest path from the entry to the exit.

Every maze contains a visible **"42"** made of fully closed cells. The maze
can be generated in two modes:

- **Perfect** (`PERFECT=True`): there is exactly one path between any two
  cells, so exactly one path from the entry to the exit.
- **Non-perfect** (`PERFECT=False`): extra walls are opened to create loops,
  so there is more than one route between the entry and the exit.

The generation logic lives in a single class, `MazeGenerator`, which can be
reused in other projects.

## Instructions

Requirements: Python 3.10 or later. The program only uses the standard
library; `flake8` and `mypy` are needed for linting.

```sh
make install       # install the lint tools (flake8, mypy)
make run           # python3 a_maze_ing.py config.txt
make debug         # run the program under pdb
make lint          # flake8 + mypy with the required flags
make lint-strict   # flake8 + mypy --strict
make clean         # remove __pycache__, .mypy_cache, ...
```

Or run it directly with any configuration file:

```sh
python3 a_maze_ing.py config.txt
```

The maze is written to the file named by `OUTPUT_FILE` and displayed in the
terminal. Invalid input (missing file, bad syntax, missing keys, coordinates
outside the maze, entry equal to exit, ...) produces a clear error message
instead of a crash.

### Configuration file

One `KEY=VALUE` pair per line. Empty lines and lines starting with `#` are
ignored.

| Key           | Required | Description                               | Example              |
|---------------|----------|-------------------------------------------|----------------------|
| `WIDTH`       | yes      | Maze width in cells                       | `WIDTH=20`           |
| `HEIGHT`      | yes      | Maze height in cells                      | `HEIGHT=15`          |
| `ENTRY`       | yes      | Entry cell as `x,y`                       | `ENTRY=0,0`          |
| `EXIT`        | yes      | Exit cell as `x,y`                        | `EXIT=19,14`         |
| `OUTPUT_FILE` | yes      | File the maze is written to               | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | yes      | `True` for a perfect maze, else `False`   | `PERFECT=True`       |
| `SEED`        | no       | Integer seed; same seed gives same maze   | `SEED=42`            |

Rules:

- `WIDTH` and `HEIGHT` must be integers, and the maze must be at least 2x2.
- `ENTRY` and `EXIT` must be different, inside the maze, and not on a cell
  of the "42" pattern.
- The "42" needs a maze of at least **9x7** cells (the pattern is 7x5 plus a
  one-cell border). For smaller mazes the pattern is left out and an error
  message is printed, but the maze is still generated.

Default `config.txt`:

```
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

### Output file format

Each cell is one hexadecimal digit whose bits are the closed walls:

| Bit     | Value | Wall  |
|---------|-------|-------|
| 0 (LSB) | 1     | North |
| 1       | 2     | East  |
| 2       | 4     | South |
| 3       | 8     | West  |

Cells are written row by row, one row per line. After an empty line come
three more lines: the entry coordinates, the exit coordinates, and the
shortest path from entry to exit using the letters `N`, `E`, `S`, `W`.

## Maze generation algorithm

**Randomized depth-first search (recursive backtracker)**, implemented
iteratively with a stack:

1. Every cell starts with all four walls closed. The cells of the "42"
   pattern are marked as blocked.
2. Starting from the entry, the algorithm moves to a random unvisited,
   non-blocked neighbour, removes the wall between the two cells, and pushes
   the new cell on the stack. When a cell has no unvisited neighbours, it
   backtracks by popping the stack.
3. When the stack is empty, every reachable cell has been visited exactly
   once, which gives a spanning tree: a perfect maze.
4. If `PERFECT=False`, extra walls are removed to create loops, and the four
   corners and the centre are given extra openings.
5. Finally, the "42" cells are closed on all four sides (the neighbouring
   cells' walls are updated too, so the encoding stays coherent).

The shortest path is found with a **breadth-first search** from the entry,
which guarantees the shortest route in an unweighted grid.

### Why this algorithm

- It always produces a valid perfect maze (a spanning tree), so the
  `PERFECT=True` requirement holds by construction.
- It is simple to implement and to explain, and an iterative stack avoids
  Python's recursion limit on large mazes.
- It creates long, winding corridors and never leaves large open areas.
- Using `random.Random(seed)` makes every maze reproducible from its seed.

## Reusable code

The generator is the `MazeGenerator` class in `maze_generator.py`. It has no
dependency on the rest of the project (no file I/O, no display), so the file
can be copied into or imported from another project.

```python
from maze_generator import MazeGenerator

gen = MazeGenerator(
    width=20,           # number of columns
    height=15,          # number of rows
    entry=(0, 0),       # (x, y)
    exit=(19, 14),      # (x, y)
    seed=42,            # optional: same seed -> same maze
    perfect=True,       # False adds loops
)

grid = gen.generate()   # build the maze
path = gen.solve()      # shortest path, e.g. "EESENEEESE..."
```

- `generate()` returns the maze as `grid[y][x]`, a list of rows of integers
  using the same wall bits as the output file (`MazeGenerator.NORTH`,
  `EAST`, `SOUTH`, `WEST`).
- `get_grid()` returns the same structure after generation.
- `solve()` returns the shortest path from entry to exit as a string of
  `N`, `E`, `S`, `W`.
- `pattern` lists the `(x, y)` cells of the "42" (empty if the maze is too
  small).

`maze_writer.py` (`MazeWriter`) and `maze_display.py` (`MazeDisplay`) are
the project-specific parts: writing the output file and drawing the maze in
the terminal.

## Team and project management

### Roles

- **gikromov**: TODO
- **mtousian**: TODO

### Planning and how it evolved

TODO

### What worked well and what could be improved

TODO

### Tools

- Git and GitHub for version control and sharing branches
- flake8 and mypy for code style and type checking
- Make to automate install, run, debug, lint and clean
- Claude Code (AI assistant), see below

## Resources

- [Maze generation algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Jamis Buck, *Maze Generation: Recursive Backtracking*](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- Jamis Buck, *Mazes for Programmers* (Pragmatic Bookshelf, 2015)
- [Breadth-first search (Wikipedia)](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Python `random` module](https://docs.python.org/3/library/random.html)
  and [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque)
- [PEP 8](https://peps.python.org/pep-0008/) and
  [PEP 257](https://peps.python.org/pep-0257/)
- [mypy documentation](https://mypy.readthedocs.io/) and
  [flake8 documentation](https://flake8.pycqa.org/)

### How AI was used

Claude Code was used for:

- Testing the `main` and `mtousian` branches side by side and checking the
  generated mazes (wall coherence, valid shortest path, perfect-maze check,
  error handling).
- Merging the `mtousian` branch into `main`.
- Adding the error message printed when the maze is too small for the "42",
  and choosing the 9x7 minimum size.
- Writing the `Makefile` and a first draft of this README.

All AI output was reviewed, tested and is understood by the team.

TODO: add any other ways AI was used during the project.
