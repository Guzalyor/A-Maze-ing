import random
from collections import deque
from typing import List, Optional, Tuple


class MazeGenerator:
    """Generate and solve a maze."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    DIRECTIONS = [
        (NORTH, 0, -1),
        (EAST, 1, 0),
        (SOUTH, 0, 1),
        (WEST, -1, 0),
    ]

    OPPOSITE = {
        NORTH: SOUTH,
        EAST: WEST,
        SOUTH: NORTH,
        WEST: EAST,
    }

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        seed: Optional[int] = None,
        perfect: bool = True,
    ) -> None:
        """Create a maze generator."""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.random = random.Random(seed)

        self.pattern = self.get_42_pattern_for_size(
            width,
            height,
        )

        self.grid: List[List[int]] = [
            [15 for _ in range(width)]
            for _ in range(height)
        ]

    @staticmethod
    def get_42_pattern_for_size(
        width: int,
        height: int,
    ) -> List[Tuple[int, int]]:
        """Return cells used for the 42 pattern."""
        if width < 7 or height < 5:
            return []

        pattern = [
            "1010111",
            "1010001",
            "1110111",
            "0010100",
            "0010111",
        ]

        pattern_width = 7
        pattern_height = 5

        start_x = (width - pattern_width) // 2
        start_y = (height - pattern_height) // 2

        cells = []

        for y, row in enumerate(pattern):
            for x, value in enumerate(row):
                if value == "1":
                    cells.append(
                        (start_x + x, start_y + y)
                    )

        return cells

    def inside(self, x: int, y: int) -> bool:
        """Check whether a cell is inside the maze."""
        return (
            0 <= x < self.width
            and 0 <= y < self.height
        )

    def remove_wall(
        self,
        x: int,
        y: int,
        direction: int,
    ) -> None:
        """Remove a wall between two neighbouring cells."""
        for wall, dx, dy in self.DIRECTIONS:
            if wall == direction:
                nx = x + dx
                ny = y + dy

                if not self.inside(nx, ny):
                    return

                self.grid[y][x] &= ~direction
                self.grid[ny][nx] &= ~self.OPPOSITE[direction]
                return

    def blocked(self, x: int, y: int) -> bool:
        """Check whether a cell belongs to the 42 pattern."""
        return (x, y) in self.pattern

    def generate_perfect(self) -> None:
        """Generate a perfect maze using randomized DFS."""
        visited = [
            [False for _ in range(self.width)]
            for _ in range(self.height)
        ]

        x, y = self.entry
        visited[y][x] = True

        stack = [(x, y)]

        while stack:
            x, y = stack[-1]

            neighbours = []

            for direction, dx, dy in self.DIRECTIONS:
                nx = x + dx
                ny = y + dy

                if not self.inside(nx, ny):
                    continue

                if visited[ny][nx]:
                    continue

                if self.blocked(nx, ny):
                    continue

                neighbours.append((nx, ny, direction))

            if not neighbours:
                stack.pop()
                continue

            nx, ny, direction = self.random.choice(
                neighbours
            )

            self.remove_wall(x, y, direction)
            visited[ny][nx] = True
            stack.append((nx, ny))

    def add_loops(self) -> None:
        """Open extra walls to create alternative routes."""
        walls = []

        for y in range(self.height):
            for x in range(self.width):
                if x + 1 < self.width:
                    walls.append((x, y, self.EAST))

                if y + 1 < self.height:
                    walls.append((x, y, self.SOUTH))

        self.random.shuffle(walls)

        loops = 0

        for x, y, direction in walls:
            if loops >= 2:
                break

            nx = x
            ny = y

            if direction == self.EAST:
                nx += 1
            else:
                ny += 1

            if self.blocked(x, y) or self.blocked(nx, ny):
                continue

            if self.grid[y][x] & direction:
                self.remove_wall(x, y, direction)
                loops += 1

    def make_corners_and_center_open(self) -> None:
        """Give corners and centre more than one possible direction."""
        cells = [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
            (self.width // 2, self.height // 2),
        ]

        for x, y in cells:
            if self.blocked(x, y):
                continue

            neighbours = []

            for direction, dx, dy in self.DIRECTIONS:
                nx = x + dx
                ny = y + dy

                if not self.inside(nx, ny):
                    continue

                if self.blocked(nx, ny):
                    continue

                if self.grid[y][x] & direction:
                    neighbours.append(direction)

            self.random.shuffle(neighbours)

            for direction in neighbours[:2]:
                self.remove_wall(x, y, direction)

    def close_42(self) -> None:
        """Keep every 42 cell completely closed."""
        for x, y in self.pattern:
            self.grid[y][x] = 15

            for direction, dx, dy in self.DIRECTIONS:
                nx = x + dx
                ny = y + dy

                if self.inside(nx, ny):
                    self.grid[ny][nx] |= self.OPPOSITE[direction]

    def generate(self) -> List[List[int]]:
        """Generate and return the maze."""
        if self.width < 2 or self.height < 2:
            raise ValueError("Maze must be at least 2x2.")

        if self.entry == self.exit:
            raise ValueError("Entry and exit must be different.")

        if not self.inside(*self.entry):
            raise ValueError("Entry is outside the maze.")

        if not self.inside(*self.exit):
            raise ValueError("Exit is outside the maze.")

        if self.blocked(*self.entry):
            raise ValueError("Entry cannot be inside 42.")

        if self.blocked(*self.exit):
            raise ValueError("Exit cannot be inside 42.")

        self.generate_perfect()

        if not self.perfect:
            self.add_loops()
            self.make_corners_and_center_open()

        self.close_42()

        return self.grid

    def solve(self) -> str:
        """Find the shortest path from entry to exit."""
        queue = deque([self.entry])
        previous: dict[tuple[int, int], Optional[tuple[int, int]]] = {
            self.entry: None
        }
        moves: dict[tuple[int, int], str] = {}

        while queue:
            x, y = queue.popleft()

            if (x, y) == self.exit:
                break

            for direction, dx, dy in self.DIRECTIONS:
                if self.grid[y][x] & direction:
                    continue

                nx = x + dx
                ny = y + dy

                if not self.inside(nx, ny):
                    continue

                if self.blocked(nx, ny):
                    continue

                if (nx, ny) in previous:
                    continue

                previous[(nx, ny)] = (x, y)

                if direction == self.NORTH:
                    moves[(nx, ny)] = "N"
                elif direction == self.EAST:
                    moves[(nx, ny)] = "E"
                elif direction == self.SOUTH:
                    moves[(nx, ny)] = "S"
                else:
                    moves[(nx, ny)] = "W"

                queue.append((nx, ny))

        if self.exit not in previous:
            raise ValueError("No path from entry to exit.")

        path: list[str] = []
        current = self.exit

        while current != self.entry:
            path.append(moves[current])

            previous_cell = previous[current]
            if previous_cell is None:
                raise ValueError("Invalid path reconstruction.")

            current = previous_cell

        path.reverse()

        return "".join(path)

    def get_grid(self) -> List[List[int]]:
        """Return the maze structure."""
        return self.grid
