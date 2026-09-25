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

        # Every cell starts with four walls.
        self.grid: List[List[int]] = [
            [15 for _ in range(width)]
            for _ in range(height)
        ]

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
            if wall != direction:
                continue

            nx = x + dx
            ny = y + dy

            if not self.inside(nx, ny):
                return

            self.grid[y][x] &= ~direction
            self.grid[ny][nx] &= ~self.OPPOSITE[direction]
            return

    def get_unvisited_neighbours(
        self,
        x: int,
        y: int,
        visited: List[List[bool]],
    ) -> List[Tuple[int, int, int]]:
        """Get unvisited neighbouring cells."""
        neighbours = []

        for direction, dx, dy in self.DIRECTIONS:
            nx = x + dx
            ny = y + dy

            if self.inside(nx, ny) and not visited[ny][nx]:
                neighbours.append((nx, ny, direction))

        return neighbours

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

            neighbours = self.get_unvisited_neighbours(
                x,
                y,
                visited,
            )

            if not neighbours:
                stack.pop()
                continue

            nx, ny, direction = self.random.choice(neighbours)

            self.remove_wall(x, y, direction)

            visited[ny][nx] = True
            stack.append((nx, ny))

    def add_loops(self) -> None:
        """Open extra walls to create loops."""
        walls = []

        for y in range(self.height):
            for x in range(self.width):
                if x < self.width - 1:
                    walls.append((x, y, self.EAST))

                if y < self.height - 1:
                    walls.append((x, y, self.SOUTH))

        self.random.shuffle(walls)

        amount = (self.width * self.height) // 8

        for x, y, direction in walls[:amount]:
            if self.grid[y][x] & direction:
                self.remove_wall(x, y, direction)

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

        self.generate_perfect()

        if not self.perfect:
            self.add_loops()

        return self.grid

    def solve(self) -> str:
        """Find the shortest path from entry to exit."""
        queue = deque([self.entry])

        previous = {
            self.entry: None
        }

        move_used = {}

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

                if (nx, ny) in previous:
                    continue

                previous[(nx, ny)] = (x, y)

                if direction == self.NORTH:
                    move_used[(nx, ny)] = "N"
                elif direction == self.EAST:
                    move_used[(nx, ny)] = "E"
                elif direction == self.SOUTH:
                    move_used[(nx, ny)] = "S"
                else:
                    move_used[(nx, ny)] = "W"

                queue.append((nx, ny))

        if self.exit not in previous:
            raise ValueError("No path from entry to exit.")

        path = []
        current = self.exit

        while current != self.entry:
            path.append(move_used[current])
            current = previous[current]

        path.reverse()

        return "".join(path)

    def get_grid(self) -> List[List[int]]:
        """Return the maze structure."""
        return self.grid