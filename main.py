"""Entry point: load a map and open the drone simulation window."""

import sys
import tkinter

from graph_builder import MapBuilder
from parser import MapParser
from simulation import Simulation
from validate import Validate
from visualizer import Visualizer


def main(argv: list[str]) -> int:
    """Load a map, prepare the simulation and open the window."""
    if len(argv) != 2:
        print("Usage: python3 main.py <map_file>", file=sys.stderr)
        return 1
    try:
        data = MapParser.parse_file(argv[1])
        Validate.validate_data(data)
        graph = MapBuilder.build_map(data)
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
