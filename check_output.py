"""Independent rule checker: python3 check_output.py <map> <output_file>."""
import sys

from graph_builder import MapBuilder
from parser import MapParser
from validate import Validate


def check(graph, nb_drones, lines):
    """Raise AssertionError on the first violated rule; return turn count."""
    start, end = graph.start, graph.end
    pos = {i: start for i in range(1, nb_drones + 1)}
    flight = {}   # id -> (target zone, arrival turn)
    for turn, line in enumerate(lines, 1):
        used_links = {}
        moved = set()
        for token in line.split():
            ident, rest = token.split("-", 1)
            d = int(ident[1:])
            assert d not in moved, f"turn {turn}: D{d} twice"
            moved.add(d)
            if d in flight:
                target, arrival = flight.pop(d)
                assert rest == target.name and arrival == turn, \
                    f"turn {turn}: D{d} must arrive at {target.name}"
                pos[d] = target
                continue
            if "-" in rest:
                a, b = rest.split("-")
                origin = pos[d]
                assert origin.name == a, f"turn {turn}: D{d} not in {a}"
                target = graph.zones[b]
                assert graph.get_cost(target) == 2, \
                    f"turn {turn}: {rest} not restricted"
                flight[d] = (target, turn + 1)
                link = [graph.get_connection(origin, target)]
            else:
                target = graph.zones[rest]
                assert graph.get_cost(target) == 1, \
                    f"turn {turn}: {rest} needs 2 turns"
                link = [c for c in [graph.get_connection(pos[d], target)]
                        if c]
                assert link, f"turn {turn}: D{d} {pos[d].name}->{rest} no link"
                pos[d] = target
            conn = link[0]
            used_links[id(conn)] = used_links.get(id(conn), 0) + 1
            assert used_links[id(conn)] <= conn.max_link_capacity, \
                f"turn {turn}: link over capacity"
        for d in list(flight):
            assert flight[d][1] > turn, f"turn {turn}: D{d} stalled"
        counts = {}
        for d, z in pos.items():
            if d not in flight:
                counts[z.name] = counts.get(z.name, 0) + 1
        for name, count in counts.items():
            z = graph.zones[name]
            if z is not start and z is not end:
                assert count <= z.max_drones, \
                    f"turn {turn}: zone {name} has {count} drones"
    assert not flight and all(z is end for z in pos.values()), \
        "not all drones delivered"
    return len(lines)


if __name__ == "__main__":
    data = MapParser.parse_file(sys.argv[1])
    Validate.validate_data(data)
    net = MapBuilder.build_map(data)
    with open(sys.argv[2]) as file:
        out = [ln for ln in file.read().splitlines() if ln.strip()]
    print("OK, turns =", check(net, int(data[0][1]), out))