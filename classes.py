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
        if zone.zone_type == "restricted":
            return 2
        return None
    
    def get_connection(self, zone1, zone2):
        for connection in self.connections:
            if ((connection.zone1 == zone1 and connection.zone2 == zone2)
                or (connection.zone1 == zone2
                    and connection.zone2 == zone1)):
                return connection
        return None

class Drone:
    def __init__(self, drone_id: int, start_zone: Zone) -> None:
        self.id = drone_id
        self.current_zone = Zone = start_zone
        self.path: list[Zone] = []
        self.path_index = 0
        self.moving = False
        self.next_zone = Zone | None = None 
        self.remaining_turns = 0


class PathInfo:
    def __init__(self, zones, cost, priority, capacity) -> None:
        self.zones = zones
        self.cost = cost
        self.priority = priority
        self.capacity = capacity
        self.assigned_drones = 0

    def uses_zone(self, zone) -> bool:
        return zone in self.zones
