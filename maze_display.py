
from typing import List, Tuple

from maze_generator import MazeGenerator


class MazeDisplay:
    """Display a maze in the terminal using ASCII characters."""

    def __init__(
        self,
        grid: List[List[int]],
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        path: str,
        show_path: bool = True,
        wall_color: str = "",
    ) -> None:
        """Initialize the display.

        Args:
            grid: Maze wall representation.
            entry: Entry coordinates.
            exit: Exit coordinates.
            path: Shortest path.
            show_path: Whether to draw the path.
            wall_color: ANSI colour code for the walls ("" = default).
        """
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.path = path
        self.show_path = show_path
        self.wall_color = wall_color

    def _path_cells(self) -> List[Tuple[int, int]]:
        """Calculate cells belonging to the solution path.

        Returns:
            List of coordinates along the path.
        """
        x, y = self.entry
        cells = [(x, y)]

        movements = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
        }

        for move in self.path:
            dx, dy = movements[move]
            x += dx
            y += dy
            cells.append((x, y))

        return cells

    def show(self) -> None:

        """Print the maze to the terminal."""
        if self.show_path:
            path_cells = set(self._path_cells())
        else:
            path_cells = set()

        north = 1
        east = 2
        south = 4
        west = 8

        pattern_42 = MazeGenerator.get_42_pattern_for_size(
            len(self.grid[0]),
            len(self.grid),
        )

        yellow = "\033[93m"
        red = "\033[91m"
        reset = "\033[0m"
        wall = self.wall_color

        for y, row in enumerate(self.grid):
            top = ""

            for cell in row:
                if cell & north:
                    top += f"{wall}+---{reset}"
                else:
                    top += f"{wall}+---{reset}"

            print(top + f"{wall}+{reset}")

            middle = ""

            for x, cell in enumerate(row):
                if cell & west:
                    middle += f"{wall}|{reset}"
                else:
                    middle += " "

                if (x, y) in pattern_42:
                    middle += f"{yellow}███{reset}"

                elif (x, y) == self.entry:
                    middle += " E "

                elif (x, y) == self.exit:
                    middle += " X "

                elif (x, y) in path_cells:
                    middle += f"{red} ● {reset}"

                else:
                    middle += "   "

            if row:
                if row[-1] & east:
                    middle += f"{wall}|{reset}"
                else:
                    middle += " "

            print(middle)

        bottom = ""

        for cell in self.grid[-1]:
            if cell & south:
                bottom += f"{wall}+---{reset}"
            else:
                bottom += f"{wall}+{reset}   "

        print(bottom + f"{wall}+{reset}")
