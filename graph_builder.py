from classes import Zone, Connection, Map
from validate import split_hub_content, parse_metadata

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
            network.add_connection()

    return network