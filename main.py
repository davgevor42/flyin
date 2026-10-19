import sys

from parser import parse_file
import validate
from graph_builder import build_map
from simulation import Simulation
from visualizer import Visualizer
import tkinter


def main(argv: list[str]) -> int:
    """Load a map, prepare the simulation and open the window."""
    if len(argv) != 2:
        print("Usage: python3 main.py <map_file>", file=sys.stderr)
        return 1
    try:
        data = parse_file(argv[1])
        validate.validate_data(data)
        graph = build_map(data)
        simulation = Simulation(graph, data)
    except OSError as error:
        print(f"Error: cannot read '{argv[1]}': {error}", file=sys.stderr)
        return 1
    except (ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    try:
        Visualizer(graph, simulation).run()
    except tkinter.TclError as error:
        print(f"Error: cannot open the window: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
