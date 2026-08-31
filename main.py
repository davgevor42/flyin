from parser import parse_file
import validate
from graph_builder import build_map

if __name__ == "__main__":
    data = parse_file("01_linear_path.txt")

    validate.validate_data(data)
    graph = build_map(data)

    for name, zone in graph.zones.items():
        print(
            name,
            zone.x,
            zone.y,
            zone.zone_type,
            zone.color,
            zone.max_drones
        )

    for connection in graph.connections:
        print(
            connection.zone1.name,
            connection.zone2.name,
            connection.max_link_capacity
        )
