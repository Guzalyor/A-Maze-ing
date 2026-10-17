
import sys
from typing import Dict, Tuple

from maze_generator import MazeGenerator
from maze_writer import MazeWriter
from maze_display import MazeDisplay


def parse_bool(value: str) -> bool:
    """Convert a configuration value to a boolean.

    Args:
        value: Text representation of a boolean.

    Returns:
        True or False.

    Raises:
        ValueError: If the value is not a valid boolean.
    """
    value = value.strip().lower()

    if value == "true":
        return True

    if value == "false":
        return False

    raise ValueError("Boolean value must be True or False.")


def parse_coordinates(value: str) -> Tuple[int, int]:
    """Parse coordinates in the form x,y.

    Args:
        value: Coordinate string.

    Returns:
        A tuple containing x and y.

    Raises:
        ValueError: If the coordinates are invalid.
    """
    parts = value.split(",")

    if len(parts) != 2:
        raise ValueError("Coordinates must have the format x,y.")

    try:
        x = int(parts[0].strip())
        y = int(parts[1].strip())
    except ValueError as error:
        raise ValueError(
            "Coordinates must contain integers."
        ) from error

    return x, y


def read_config(filename: str) -> Dict[str, str]:
    """Read the maze configuration file.

    Args:
        filename: Path to the configuration file.

    Returns:
        Dictionary containing configuration values.

    Raises:
        ValueError: If the configuration is invalid.
        OSError: If the file cannot be opened.
    """
    config: Dict[str, str] = {}

    with open(filename, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise ValueError(
                    f"Invalid configuration at line {line_number}."
                )

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key or not value:
                raise ValueError(
                    f"Invalid configuration at line {line_number}."
                )

            config[key] = value

    required = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    ]

    for key in required:
        if key not in config:
            raise ValueError(
                f"Missing required configuration key: {key}"
            )

    return config


def create_generator(config: Dict[str, str]) -> MazeGenerator:
    """Create a maze generator from configuration values.

    Args:
        config: Parsed configuration dictionary.

    Returns:
        Configured MazeGenerator instance.
    """
    try:
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])
    except ValueError as error:
        raise ValueError(
            "WIDTH and HEIGHT must be integers."
        ) from error

    entry = parse_coordinates(config["ENTRY"])
    exit_position = parse_coordinates(config["EXIT"])

    perfect = parse_bool(config["PERFECT"])

    seed = None

    if "SEED" in config:
        try:
            seed = int(config["SEED"])
        except ValueError as error:
            raise ValueError("SEED must be an integer.") from error

    return MazeGenerator(
        width=width,
        height=height,
        entry=entry,
        exit=exit_position,
        seed=seed,
        perfect=perfect,
    )


def clear_screen() -> None:
    """Clear the terminal before drawing the maze again."""
    print("\033[2J\033[H", end="")


def save_and_display(
    generator: MazeGenerator,
    show_path: bool,
    wall_color: str,
    output_file: str,
) -> None:
    """Write and display the current maze."""
    grid = generator.get_grid()
    path = generator.solve()

    writer = MazeWriter(
        grid=grid,
        entry=generator.entry,
        exit=generator.exit,
        path=path,
    )
    writer.write(output_file)

    display = MazeDisplay(
        grid=grid,
        entry=generator.entry,
        exit=generator.exit,
        path=path,
        show_path=show_path,
        wall_color=wall_color,
    )
    display.show()

    print()
    print("N - Generate a new maze")
    print("P - Show/hide shortest path")
    print("C - Change wall colour")
    print("Q - Quit")


def main() -> None:
    """Run the maze generator program."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    config_file = sys.argv[1]

    try:
        config = read_config(config_file)

        show_path = True
        colours = [
            "",
            "\033[91m",
            "\033[92m",
            "\033[93m",
            "\033[94m",
            "\033[95m",
            "\033[96m",
        ]
        colour_index = 0

        generator = create_generator(config)

        if not generator.pattern:
            print(
                "Error: maze is too small to display the 42 pattern "
                "(minimum size is 9x7)."
            )

        grid = generator.generate()

        while True:
            # Clear the terminal before displaying the maze.
            print("\033[2J\033[H", end="")

            path = generator.solve()

            writer = MazeWriter(
                grid=grid,
                entry=generator.entry,
                exit=generator.exit,
                path=path,
            )
            writer.write(config["OUTPUT_FILE"])

            display = MazeDisplay(
                grid=grid,
                entry=generator.entry,
                exit=generator.exit,
                path=path,
                show_path=show_path,
                wall_color=colours[colour_index],
            )
            display.show()

            print()
            print("N - Generate a new maze")
            print("P - Show/hide shortest path")
            print("C - Change wall colour")
            print("Q - Quit")

            choice = input("\nChoose an option: ").strip().lower()

            if choice == "q":
                print("Goodbye!")
                break

            elif choice == "p":
                show_path = not show_path

            elif choice == "c":
                colour_index = (colour_index + 1) % len(colours)

            elif choice == "n":
                new_config = config.copy()
                new_config.pop("SEED", None)

                generator = create_generator(new_config)

                if not generator.pattern:
                    print(
                        "Error: maze is too small to display the 42 pattern "
                        "(minimum size is 9x7)."
                    )

                grid = generator.generate()

            else:
                input("Invalid option. Press Enter to continue.")

    except FileNotFoundError:
        print(f"Error: configuration file '{config_file}' not found.")

    except PermissionError:
        print(f"Error: permission denied for '{config_file}'.")

    except (ValueError, OSError) as error:
        print(f"Error: {error}")

    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()
