class Zone:
    """Represent a zone in the drone network."""
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        color: str = "none",
        max_drones: int = 1
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones


class Connection:
    """Represent a bidirectional connection between two zones."""
    def __init__(
        self,
        zone1: "Zone",
        zone2: "Zone",
        max_link_capacity: int = 1
    ) -> None:
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity


class Map:
    """Represent the complete drone network."""
    def __init__(self) -> None:
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.start: Zone | None = None
        self.end: Zone | None = None

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the map."""
        self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        """Add a connection to the map."""
        self.connections.append(connection)

    def get_neighbors(self, zone):
        neighbors = []

        for connection in self.connections:
            if connection.zone1 == zone:
                neighbors.append(connection.zone2)
            elif connection.zone2 == zone:
                neighbors.append(connection.zone1)

        return neighbors

    def get_cost(self, zone):
        if zone.zone_type == "normal" or zone.zone_type == "priority":
            return 1
        elif zone.zone_type == "restricted":
            return 2
        elif zone.zone_type == "blocked":
            return None


class Drone:
    def __init__(self, drone_id):
        self.id = drone_id
        self.current_zone = None
        self.path = []
        self.path_index = 0
        self.moving = False
        self.next_zone = None
        self.remaining_turns = 0


class PathInfo:
    def __init__(self, zones, cost, priority):
        self.zones = zones
        self.cost = cost
        self.priority = priority
        self.assigned_drones = 0

    def uses_zone(self, zone):
        return zone in self.zones
from classes import Zone, Connection, Map
from validate import split_hub_content, parse_metadata, split_connection_content


def zone_creating(content, line_number):
    name, x, y, metadata = split_hub_content(content, line_number)
    metadata_dict = parse_metadata(metadata, line_number)
    zone_type = metadata_dict.get("zone", "normal")
    color = metadata_dict.get("color", "none")
    max_drones = int(metadata_dict.get("max_drones", "1"))
    zone = Zone(
        name,
        int(x),
        int(y),
        zone_type,
        color,
        max_drones
        )
    return zone


def connection_creating(content, line_number, network):
    zone1_name, zone2_name, metadata = split_connection_content(content,
                                                                line_number)
    zone1 = network.zones[zone1_name]
    zone2 = network.zones[zone2_name]
    metadata_dict = parse_metadata(metadata, line_number)
    max_links = int(metadata_dict.get("max_link_capacity", "1"))
    connection = Connection(zone1, zone2, max_links)
    return connection


def build_map(data: list[tuple[str, str, int]]) -> Map:
    """Create a Map object from validated parser data."""
    network = Map()
    for line_type, content, line_number in data:
        if line_type in ("start_hub", "hub", "end_hub"):
            zone = zone_creating(content, line_number)
            network.add_zone(zone)
            if line_type == "start_hub":
                network.start = zone
            elif line_type == "end_hub":
                network.end = zone
        elif line_type == "connection":
            connection = connection_creating(content, line_number, network)
            network.add_connection(connection)
    return network

from parser import parse_file
import validate
from graph_builder import build_map
import visualizer
import path
from simulation import Simulation

if __name__ == "__main__":
    data = parse_file("01_linear_path.txt")

    validate.validate_data(data)
    graph = build_map(data)

    simulation = Simulation(graph, data)

    v = visualizer.Visualizer(graph, simulation)
    v.run()

    finder = path.path(graph)
    result = finder.find_path(graph.start, graph.end)

    print("############")
"""
    for drone in simulation.drones:
        print(drone.id, [zone.name for zone in drone.path])
"""
def parse_line(line):
    if line.startswith("nb_drones:"):
        return "nb_drones", line[len("nb_drones:"):].strip()

    elif line.startswith("start_hub:"):
        return "start_hub", line[len("start_hub:"):].strip()

    elif line.startswith("hub:"):
        return "hub", line[len("hub:"):].strip()

    elif line.startswith("end_hub:"):
        return "end_hub", line[len("end_hub:"):].strip()

    elif line.startswith("connection:"):
        return "connection", line[len("connection:"):].strip()

    return "unknown", line


def parse_file(filename):
    data = []

    with open(filename, "r") as file:
        for line_number, line in enumerate(file, 1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            line_type, content = parse_line(line)

            data.append((line_type, content, line_number))

    return dataclass path:

    def __init__(self, graph):
        self.graph = graph

    def find_path(self, start, end):
        distance = {}
        previous = {}
        priority_count = {}
        visited = set()

        for zone in self.graph.zones.values():
            distance[zone] = float("inf")
            priority_count[zone] = 0

        distance[start] = 0
        while True:
            current = None

            for zone in self.graph.zones.values():
                if zone not in visited and distance[zone] != float("inf"):
                    if current is None or distance[zone] < distance[current]:
                        current = zone

            if current is None:
                break
            if current == end:
                break
            visited.add(current)

            neighbors = self.graph.get_neighbors(current)

            for neighbor in neighbors:
                cost = self.graph.get_cost(neighbor)
                if cost is not None:
                    new_distance = distance[current] + cost
                    new_priority = priority_count[current]
                    if neighbor.zone_type == "priority":
                        new_priority += 1
                    if new_distance < distance[neighbor]:
                        distance[neighbor] = new_distance
                        previous[neighbor] = current
                        priority_count[neighbor] = new_priority
                    elif new_distance == distance[neighbor]:
                        if new_priority > priority_count[neighbor]:
                            distance[neighbor] = new_distance
                            priority_count[neighbor] = new_priority
                            previous[neighbor] = current

        path = []
        current = end

        if end != start and end not in previous:
            return []

        while current != start:
            path.append(current)
            current = previous[current]
        path.append(start)
        path.reverse()

        return path

    def find_all_paths(self, start, end):
        paths = []
        current_path = [start]

        self.find_paths_recursive(
            start,
            end,
            current_path,
            paths
        )

        return paths

    def find_paths_recursive(
        self,
        current,
        end,
        current_path,
        paths
        ):
        if current == end:
            paths.append(current_path.copy())
            return

        for neighbor in self.graph.get_neighbors(current):
            cost = self.graph.get_cost(neighbor)

            if cost is not None and neighbor not in current_path:
                current_path.append(neighbor)

                self.find_paths_recursive(
                    neighbor,
                    end,
                    current_path,
                    paths
                )

                current_path.pop()

    def get_path_cost(self, current_path):
        total_cost = 0
        for zone in current_path[1:]:
            cost = self.graph.get_cost(zone)
            if cost is not None:
                total_cost += cost
        return total_cost

    def get_priority_count(self, current_path):
        count = 0

        for zone in current_path[1:]:
            if zone.zone_type == "priority":
                count += 1

        return count
from classes import Drone, PathInfo
from path import path

class Simulation:
    def __init__(self, network, data):
        self.network = network
        self.drones = []
        self.turn = 0

        self.pathfinder = path(network)
        self.path_infos = []

        self.create_drones(int(data[0][1]))
        self.find_paths()
        self.sort_path()
        self.print_shared_zones()
        self.assign_paths()
        #self.run()

        for drone in self.drones:
            print(
                "Drone",
                drone.id,
                "->",
                [zone.name for zone in drone.path]
            )

    def create_drones(self, number_of_drones):
        for i in range(number_of_drones):
            drone = Drone(i + 1)
            drone.current_zone = self.network.start
            self.drones.append(drone)

    def assign_paths(self):
        for drone in self.drones:
            best_path = self.get_best_path()

            if best_path is None:
                return

            drone.path = best_path.zones.copy()
            best_path.assigned_drones += 1

    def move_drone(self, drone):
        if drone.moving:
            return

        if drone.path_index == len(drone.path) - 1:
            return

        next_zone = drone.path[drone.path_index + 1]
        cost = self.network.get_cost(next_zone)

        if cost is None:
            return

        if not self.can_enter_zone(next_zone):
            return

        if not self.can_use_connection(
            drone.current_zone,
            next_zone
        ):
            return

        drone.remaining_turns = cost
        drone.next_zone = next_zone
        drone.moving = True

    def is_finished(self):
        for drone in self.drones:
            if not drone.path:
                return False
            if drone.path_index != len(drone.path) - 1:
                return False
            if drone.moving:
                return False
        return True

    def move_one_step(self):
        self.turn += 1
        print("\nTURN:", self.turn)
        self.assign_waiting_drones()

        for drone in self.drones:
            self.finish_moving_drone(drone)

        proposed_moves = []
        accepted_moves = []

        for drone in self.drones:
            next_zone = self.get_proposed_move(drone)

            proposed_moves.append((drone, next_zone))

            print(
                "Drone",
                drone.id,
                "proposes:",
                next_zone.name if next_zone else "WAIT"
            )

        for drone, next_zone in proposed_moves:
            if next_zone is None:
                continue

            if self.can_accept_move(accepted_moves, proposed_moves, next_zone):
                accepted_moves.append((drone, next_zone))

        print("PROPOSED:", len(proposed_moves))
        print("ACCEPTED:", len(accepted_moves))

        for drone, next_zone in accepted_moves:
            print(
                "Drone",
                drone.id,
                "->",
                next_zone.name
            )
            self.apply_move(drone, next_zone)

        self.print_state()

    """
    def movement(self):
        step = 0
        while not self.is_finished():
            print(f"\n--- Step {step} ---")
            for drone in self.drones:
                self.move_drone(drone)
            self.print_state()
            step += 1
    """
    def can_enter_zone(self, zone):
        i = 0
        for drone in self.drones:
            if drone.current_zone == zone:
                i += 1
            elif drone.moving and drone.next_zone == zone:
                i += 1
        if zone == self.network.start or zone == self.network.end:
            return 1
        if i >= zone.max_drones:
            return 0
        return 1

    def can_use_connection(self, current_zone, next_zone):
        i = 0
        for drone in self.drones:
            if ((drone.current_zone == current_zone
                 and drone.next_zone == next_zone)
                    or (drone.current_zone == next_zone
                        and drone.next_zone == current_zone)):
                if drone.moving is True:
                    i += 1
        for con in self.network.connections:
            if ((con.zone1 == current_zone
                and con.zone2 == next_zone)
                    or (con.zone1 == next_zone
                        and con.zone2 == current_zone)):
                if (i >= con.max_link_capacity):
                    return 0
        return 1

    def find_paths(self):
        paths = self.pathfinder.find_all_paths(
            self.network.start,
            self.network.end
        )

        for current_path in paths:
            cost = self.pathfinder.get_path_cost(current_path)
            priority = self.pathfinder.get_priority_count(current_path)

            path_info = PathInfo(
                current_path,
                cost,
                priority
            )

            self.path_infos.append(path_info)

    def sort_path(self):
        self.path_infos.sort(
            key=lambda info: (info.cost, -info.priority)
        )

    def count_path_usage(self, path_info):
        count = 0

        for drone in self.drones:
            if drone.path == path_info.zones:
                count += 1
        return count

    def count_zone_usage(self, zone):
        count = 0

        for drone in self.drones:
            if zone in drone.path:
                count += 1

        return count

    def can_assign_path(self, path_info):
        for zone in path_info.zones:
            if zone == self.network.start or zone == self.network.end:
                continue
            usage = self.count_zone_usage(zone)

            if usage >= zone.max_drones:
                return False

        return True

    def assign_waiting_drones(self):
        for drone in self.drones:
            if drone.path:
                continue
            for path_info in self.path_infos:
                if self.can_assign_path(path_info):
                    drone.path = path_info.zones
                    break

    def get_best_path(self):
        best_path = None
        for path_info in self.path_infos:
            if best_path is None:
                best_path = path_info
                continue
            if path_info.cost < best_path.cost:
                best_path = path_info
            elif path_info.cost == best_path.cost:
                if path_info.priority > best_path.priority:
                    best_path = path_info
                elif path_info.priority == best_path.priority:
                    if path_info.assigned_drones < best_path.assigned_drones:
                        best_path = path_info
        return best_path

    def run(self):
        i = 0
        while not self.is_finished():
            i += 1
            self.move_one_step()
        print(i)

    def print_shared_zones(self):
        for i, path1 in enumerate(self.path_infos):
            for j, path2 in enumerate(self.path_infos):
                if i >= j:
                    continue

                shared = []

                for zone in path1.zones:
                    if zone in path2.zones:
                        shared.append(zone.name)

                print("PATH", i, "and PATH", j)
                print("shared:", shared)

    def finish_moving_drone(self, drone):
        print(
            "FINISH:",
            drone.id,
            "moving =", drone.moving,
            "remaining =", drone.remaining_turns
        )
        if not drone.moving:
            return
        drone.remaining_turns -=1

        if drone.remaining_turns == 0:
            drone.path_index += 1
            drone.current_zone = drone.next_zone
            drone.next_zone = None
            drone.moving = False

    def get_proposed_move(self, drone):
        if drone.moving:
            return None

        if drone.path_index == len(drone.path) - 1:
            return None

        next_zone = drone.path[drone.path_index + 1]
        cost = self.network.get_cost(next_zone)

        if cost is None:
            return None

        return next_zone

    def can_accept_move(self, accepted_moves, proposed_moves, next_zone):
        if next_zone == self.network.start:
            return True

        if next_zone == self.network.end:
            return True

        current = self.count_current_drones(next_zone)

        leaving = self.count_leaving_drones(
            next_zone,
            proposed_moves
        )

        proposed = 0

        for drone, zone in accepted_moves:
            if zone == next_zone:
                proposed += 1

        print(
            "ZONE:",
            next_zone.name,
            "current:",
            current,
            "leaving:",
            leaving,
            "accepted:",
            proposed
        )

        return current - leaving + proposed < next_zone.max_drones

    def count_proposed_entries(self, proposed_moves, zone):
        count = 0

        for drone, next_zone in proposed_moves:
            if next_zone == zone:
                count += 1

        return count

    def apply_move(self, drone, next_zone):
        cost = self.network.get_cost(next_zone)

        print(
            "APPLY:",
            drone.id,
            "zone:",
            next_zone.name,
            "cost:",
            cost
        )
        drone.remaining_turns = cost
        drone.next_zone = next_zone
        drone.moving = True


    def count_current_drones(self, zone):
        count = 0

        for drone in self.drones:
            if drone.current_zone == zone:
                count +=1

        return count

    def count_leaving_drones(self, zone, proposed_moves):
        count = 0

        for drone, next_zone in proposed_moves:
            if drone.current_zone == zone and next_zone != zone and next_zone is not None:
                count += 1
        return count

    def print_state(self):
        for drone in self.drones:
            print(
                drone.id,
                "cur:",
                drone.current_zone.name,
                "next:",
                drone.next_zone.name if drone.next_zone else None,
                "moving:",
                drone.moving,
                "remaining:",
                drone.remaining_turns
            )
        print("")



VALID_ZONE_TYPES = {
    "normal",
    "blocked",
    "restricted",
    "priority",
}

VALID_HUB_METADATA = {
    "zone",
    "color",
    "max_drones",
}

VALID_CONNECTION_METADATA = {
    "max_link_capacity",
}


def validate_data(data: list[tuple[str, str, int]]) -> None:
    """Validate all parsed input records."""
    validate_nb_drones(data)
    validate_hubs(data)
    validate_start_end(data)
    validate_connections(data)


def validate_nb_drones(
    data: list[tuple[str, str, int]]
) -> None:
    """Validate the number of drones."""
    if not data:
        raise ValueError("Input file is empty")

    line_type, content, line_number = data[0]

    if line_type != "nb_drones":
        raise ValueError(
            f"Line {line_number}: first line must be nb_drones"
        )

    if not content.isdigit() or int(content) <= 0:
        raise ValueError(
            f"Line {line_number}: "
            "nb_drones must be a positive integer"
        )


def split_hub_content(
    content: str,
    line_number: int,
) -> tuple[str, str, str, str | None]:
    """Split hub content into name, coordinates, and metadata."""
    metadata = None

    if "[" in content:
        if content.count("[") != 1 or not content.endswith("]"):
            raise ValueError(
                f"Line {line_number}: invalid metadata syntax"
            )

        main, metadata = content.split("[", 1)
        metadata = metadata[:-1].strip()
        main = main.strip()

        if "]" in main or "]" in metadata:
            raise ValueError(
                f"Line {line_number}: invalid metadata syntax"
            )
    else:
        if "]" in content:
            raise ValueError(
                f"Line {line_number}: invalid metadata syntax"
            )
        main = content.strip()

    parts = main.split()

    if len(parts) != 3:
        raise ValueError(
            f"Line {line_number}: invalid hub syntax"
        )

    name, x, y = parts

    return name, x, y, metadata


def validate_hub_name(name: str, line_number: int) -> None:
    """Validate a hub name."""
    if not name or "-" in name or " " in name:
        raise ValueError(
            f"Line {line_number}: invalid hub name '{name}'"
        )


def validate_coordinates(
    x: str,
    y: str,
    line_number: int,
) -> None:
    """Validate hub coordinates."""
    try:
        int(x)
        int(y)
    except ValueError:
        raise ValueError(
            f"Line {line_number}: coordinates must be integers"
        ) from None


def parse_metadata(
    metadata: str | None,
    line_number: int,
) -> dict[str, str]:
    """Parse metadata into key-value pairs."""
    result: dict[str, str] = {}

    if metadata is None:
        return result

    if not metadata:
        raise ValueError(
            f"Line {line_number}: metadata cannot be empty"
        )

    for part in metadata.split():
        if part.count("=") != 1:
            raise ValueError(
                f"Line {line_number}: invalid metadata syntax"
            )

        key, value = part.split("=", 1)

        if not key or not value:
            raise ValueError(
                f"Line {line_number}: invalid metadata syntax"
            )

        if key in result:
            raise ValueError(
                f"Line {line_number}: duplicate metadata '{key}'"
            )

        result[key] = value

    return result


def validate_zone_metadata(
    metadata: str | None,
    line_number: int,
    is_start_end: bool = False,
) -> None:
    """Validate hub metadata values."""
    values = parse_metadata(metadata, line_number)

    for key in values:
        if key not in VALID_HUB_METADATA:
            raise ValueError(
                f"Line {line_number}: unknown metadata '{key}'"
            )

    if "zone" in values:
        if values["zone"] not in VALID_ZONE_TYPES:
            raise ValueError(
                f"Line {line_number}: invalid zone type "
                f"'{values['zone']}'"
            )

    if "max_drones" in values and not is_start_end:
        value = values["max_drones"]

        if not value.isdigit() or int(value) <= 0:
            raise ValueError(
                f"Line {line_number}: "
                "max_drones must be a positive integer"
            )


def validate_hub(
    content: str,
    line_number: int,
    names: set[str],
    is_start_end: bool = False,
) -> None:
    """Validate a hub definition and record its name."""
    name, x, y, metadata = split_hub_content(
        content,
        line_number,
    )

    validate_hub_name(name, line_number)
    validate_coordinates(x, y, line_number)

    if name in names:
        raise ValueError(
            f"Line {line_number}: duplicate hub name '{name}'"
        )

    validate_zone_metadata(
        metadata,
        line_number,
        is_start_end,
    )

    names.add(name)


def validate_hubs(data: list[tuple[str, str, int]]) -> None:
    """Validate all hub definitions."""
    names: set[str] = set()

    for line_type, content, line_number in data:
        if line_type == "start_hub":
            validate_hub(content, line_number, names, True)

        elif line_type == "hub":
            validate_hub(content, line_number, names)

        elif line_type == "end_hub":
            validate_hub(content, line_number, names, True)


def validate_start_end(
    data: list[tuple[str, str, int]]
) -> None:
    """Require exactly one start hub and one end hub."""
    start_count = 0
    end_count = 0

    for line_type, _, line_number in data:
        if line_type == "start_hub":
            start_count += 1
            if start_count > 1:
                raise ValueError(
                    f"Line {line_number}: "
                    "multiple start_hub definitions"
                )

        elif line_type == "end_hub":
            end_count += 1
            if end_count > 1:
                raise ValueError(
                    f"Line {line_number}: "
                    "multiple end_hub definitions"
                )

    if start_count == 0:
        raise ValueError("Missing start_hub")

    if end_count == 0:
        raise ValueError("Missing end_hub")


def split_connection_content(
    content: str,
    line_number: int,
) -> tuple[str, str, str | None]:
    """Split connection content into endpoints and metadata."""
    metadata = None

    if "[" in content:
        if content.count("[") != 1 or not content.endswith("]"):
            raise ValueError(
                f"Line {line_number}: invalid metadata syntax"
            )

        main, metadata = content.split("[", 1)
        metadata = metadata[:-1].strip()
        main = main.strip()

        if "]" in main or "]" in metadata:
            raise ValueError(
                f"Line {line_number}: invalid metadata syntax"
            )
    else:
        if "]" in content:
            raise ValueError(
                f"Line {line_number}: invalid metadata syntax"
            )
        main = content.strip()

    if main.count("-") != 1:
        raise ValueError(
            f"Line {line_number}: invalid connection syntax"
        )

    zone1, zone2 = main.split("-", 1)
    zone1 = zone1.strip()
    zone2 = zone2.strip()

    if not zone1 or not zone2:
        raise ValueError(
            f"Line {line_number}: invalid connection syntax"
        )

    return zone1, zone2, metadata


def validate_connection_metadata(
    metadata: str | None,
    line_number: int,
) -> None:
    """Validate connection metadata."""
    values = parse_metadata(metadata, line_number)

    for key in values:
        if key not in VALID_CONNECTION_METADATA:
            raise ValueError(
                f"Line {line_number}: unknown metadata '{key}'"
            )

    if "max_link_capacity" in values:
        value = values["max_link_capacity"]

        if not value.isdigit() or int(value) <= 0:
            raise ValueError(
                f"Line {line_number}: "
                "max_link_capacity must be a positive integer"
            )


def validate_connection(
    content: str,
    line_number: int,
    defined_hubs: set[str],
    connections: set[frozenset[str]],
) -> None:
    """Validate one connection."""
    zone1, zone2, metadata = split_connection_content(
        content,
        line_number,
    )

    if zone1 not in defined_hubs:
        raise ValueError(
            f"Line {line_number}: zone '{zone1}' "
            "was not previously defined"
        )

    if zone2 not in defined_hubs:
        raise ValueError(
            f"Line {line_number}: zone '{zone2}' "
            "was not previously defined"
        )

    if zone1 == zone2:
        raise ValueError(
            f"Line {line_number}: connection cannot connect "
            "a zone to itself"
        )

    connection = frozenset((zone1, zone2))

    if connection in connections:
        raise ValueError(
            f"Line {line_number}: duplicate connection"
        )

    validate_connection_metadata(metadata, line_number)
    connections.add(connection)


def validate_connections(
    data: list[tuple[str, str, int]]
) -> None:
    """Validate connections in input order."""
    defined_hubs: set[str] = set()
    connections: set[frozenset[str]] = set()

    for line_type, content, line_number in data:
        if line_type in ("start_hub", "hub", "end_hub"):
            name, _, _, _ = split_hub_content(
                content,
                line_number,
            )
            defined_hubs.add(name)

        elif line_type == "connection":
            validate_connection(
                content,
                line_number,
                defined_hubs,
                connections,
            )

        elif line_type == "unknown":
            raise ValueError(
                f"Line {line_number}: unknown line type"
            )import tkinter as tk


class Visualizer:
    """Display the map graph."""

    def __init__(self, graph, simulation):
        self.graph = graph
        self.simulation = simulation
        self.root = tk.Tk()
        self.root.title("Fly-in Map")
        self.root.geometry("800x600")

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill="both", expand=True)
        self.button = tk.Button(self.root, text="Next Step", command=self.next_step)
        self.button.pack()

        for i in self.graph.connections:
            self.draw_connection(i)
        for i in self.graph.zones.values():
            self.draw_zone(i)
        self.draw_drones(self.simulation.drones)

    def run(self):
        """Start the graphical interface."""
        self.root.mainloop()

    def destroy(self):
        self.root.destroy()

    def map_to_screen(self, x, y):
        center_x = 100
        center_y = 400
        scale = 100

        screen_x = center_x + x * scale
        screen_y = center_y - y * scale

        return screen_x, screen_y

    def draw_zone(self, zone):
        x, y = self.map_to_screen(zone.x, zone.y)
        radius = 25

        if zone.color == "rainbow":
            self.draw_rainbow_zone(x, y, radius)
        else:
            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=zone.color
            )

        self.canvas.create_text(
            x,
            y - radius,
            text=zone.name
        )

    def draw_connection(self, con):
        zone1 = con.zone1
        zone2 = con.zone2
        x1, y1 = self.map_to_screen(zone1.x, zone1.y)
        x2, y2 = self.map_to_screen(zone2.x, zone2.y)
        self.canvas.create_line(x1, y1, x2, y2)

    def draw_drone(self, drone, offset):
        if not drone.moving:
            x, y = self.map_to_screen(
                drone.current_zone.x,
                drone.current_zone.y
            )
        else:
            current = drone.current_zone
            next_zone = drone.next_zone

            x = (current.x + next_zone.x) / 2
            y = (current.y + next_zone.y) / 2

            x, y = self.map_to_screen(x, y)

        x += offset[0]
        y += offset[1]

        size = 10

        self.canvas.create_polygon(
            x, y - size,
            x - size, y + size,
            x + size, y + size,
            tags="drone"
        )

        self.canvas.create_text(
            x,
            y + 18,
            text=str(drone.id),
            tags="drone"
        )

    def draw_drones(self, drones):
        self.canvas.delete("drone")
        for i, drone in enumerate(drones):
            offset = self.get_drone_offset(i)
            self.draw_drone(drone, offset)

    def next_step(self):
        if self.simulation.is_finished():
            return
        self.simulation.move_one_step()
        self.draw_drones(self.simulation.drones)

    def get_drone_offset(self, index):
        columns = 4
        spacing = 20

        column = index % columns
        row = index // columns

        x_offset = (column - 1.5) * spacing
        y_offset = row * spacing

        return x_offset, y_offset

    def get_drone_position(self, drone):
        if not drone.moving:
            return self.map_to_screen(
                drone.current_zone.x,
                drone.current_zone.y
            )

        current = drone.current_zone
        next_zone = drone.next_zone

        x = (current.x + next_zone.x) / 2
        y = (current.y + next_zone.y) / 2

        return self.map_to_screen(x, y)

    def get_map_bounds(self):
        """Get the minimum and maximum map coordinates."""
        zones = self.graph.zones.values()

        min_x = min(zone.x for zone in zones)
        max_x = max(zone.x for zone in zones)
        min_y = min(zone.y for zone in zones)
        max_y = max(zone.y for zone in zones)

        return min_x, max_x, min_y, max_y

    def draw_rainbow_zone(self, x, y, radius):
        colors = [
            "#ff0000",
            "#ff7f00",
            "#ffff00",
            "#00ff00",
            "#0000ff",
            "#4b0082",
            "#9400d3"
        ]

        steps = len(colors)

        for i, color in enumerate(colors):
            current_radius = radius - i * (radius // steps)

            self.canvas.create_oval(
                x - current_radius,
                y - current_radius,
                x + current_radius,
                y + current_radius,
                fill=color,
            )

