"""Run every map, check the output rules and print a summary."""
import contextlib
import io
import sys
import time

from check_output import check
from graph_builder import MapBuilder
from parser import MapParser
from simulation import Simulation
from validate import Validate

# part of the file name -> optimum (adjust to your file names)
OPTIMUM = {
    "linear": 4, "fork": 4, "basic": 4,
    "dead_end": 8, "loop": 10, "priority": 6,
    "maze": 13, "hell": 16, "ultimate": 26, "impossible": 43,
}


def find_optimum(path):
    """Return the optimum for a map whose file name matches a key."""
    for key, value in OPTIMUM.items():
        if key in path:
            return value
    return None


def run_map(path):
    """Simulate one map and return a one-line result."""
    start = time.time()
    try:
        data = MapParser.parse_file(path)
        Validate.validate_data(data)
        graph = MapBuilder.build_map(data)
        simulation = Simulation(graph, data)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            simulation.run()
        lines = [ln for ln in buffer.getvalue().splitlines() if ln.strip()]
        turns = check(graph, int(data[0][1]), lines)
    except AssertionError as error:
        return f"RULE VIOLATION: {error}"
    except Exception as error:
        return f"ERROR ({type(error).__name__}): {error}"
    elapsed = time.time() - start

    best = find_optimum(path)
    note = ""
    if best is not None:
        if turns == best:
            note = f"OPTIMUM ({best})"
        elif turns <= best * 1.25:
            note = f"within 25% (optimum {best})"
        else:
            note = f"TOO SLOW (optimum {best})"
    return f"turns={turns}  {elapsed:.2f}s  {note}"


def main():
    """Run all maps given on the command line."""
    if len(sys.argv) < 2:
        print("Usage: python3 check_all.py maps/*/*.txt")
        return
    for path in sys.argv[1:]:
        print(f"{path}: {run_map(path)}")


if __name__ == "__main__":
    main()