
from typing import List, Tuple


class MazeWriter:
    """Write a generated maze to the required output format."""

    def __init__(
        self,
        grid: List[List[int]],
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        path: str,
    ) -> None:
        """Initialize the maze writer.

        Args:
            grid: Maze wall representation.
            entry: Entry coordinates.
            exit: Exit coordinates.
            path: Shortest path from entry to exit.
        """
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.path = path

    def _format_grid(self) -> str:
        """Convert the maze grid to hexadecimal rows.

        Returns:
            Maze represented as hexadecimal digits.
        """
        lines: List[str] = []

        for row in self.grid:
            line = "".join(format(cell, "X") for cell in row)
            lines.append(line)

        return "\n".join(lines)

    def write(self, filename: str) -> None:
        """Write the maze to a file.

        Args:
            filename: Destination file.
        """
        maze = self._format_grid()

        entry = f"{self.entry[0]},{self.entry[1]}"
        exit_position = f"{self.exit[0]},{self.exit[1]}"

        content = (
            f"{maze}\n\n"
            f"{entry}\n"
            f"{exit_position}\n"
            f"{self.path}\n"
        )

        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
