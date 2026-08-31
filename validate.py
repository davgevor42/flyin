VALID_ZONE_TYPES = {
    "normal",
    "blocked",
    "restricted",
    "priority"
}


def validate_data(data):
    validate_nb_drones(data)
    validate_hubs(data)
    validate_start_end(data)
    validate_connections(data)


def validate_nb_drones(data):
    line_type, content, line_number = data[0]

    if line_type != "nb_drones":
        raise ValueError(
            f"Line {line_number}: first line must be nb_drones"
        )

    if not content.isdigit() or int(content) <= 0:
        raise ValueError(
            f"Line {line_number}: nb_drones must be a positive integer"
        )


def split_hub_content(content, line_number):
    metadata = None

    if "[" in content:
        if not content.endswith("]"):
            raise ValueError(
                f"Line {line_number}: invalid metadata syntax"
            )

        main, metadata = content.split("[", 1)
        metadata = metadata[:-1].strip()
        main = main.strip()
    else:
        main = content

    parts = main.split()

    if len(parts) != 3:
        raise ValueError(
            f"Line {line_number}: invalid hub syntax"
        )

    name, x, y = parts

    return name, x, y, metadata


def validate_hub_name(name, line_number):
    if not name:
        raise ValueError(
            f"Line {line_number}: hub name cannot be empty"
        )

    if "-" in name or " " in name:
        raise ValueError(
            f"Line {line_number}: invalid hub name '{name}'"
        )


def validate_coordinates(x, y, line_number):
    try:
        int(x)
        int(y)
    except ValueError:
        raise ValueError(
            f"Line {line_number}: coordinates must be integers"
        )


def parse_metadata(metadata, line_number):
    result = {}

    if metadata is None:
        return result

    parts = metadata.split()

    for part in parts:
        if "=" not in part:
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


def validate_zone_metadata(metadata, line_number, is_start_end=False):
    values = parse_metadata(metadata, line_number)

    if "zone" in values:
        if values["zone"] not in VALID_ZONE_TYPES:
            raise ValueError(
                f"Line {line_number}: invalid zone type "
                f"'{values['zone']}'"
            )

    if "max_drones" in values:
        if is_start_end:
            return

        value = values["max_drones"]

        if not value.isdigit() or int(value) <= 0:
            raise ValueError(
                f"Line {line_number}: max_drones must be "
                f"a positive integer"
            )


def validate_hub(content, line_number, names, is_start_end=False):
    name, x, y, metadata = split_hub_content(
        content,
        line_number
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
        is_start_end
    )

    names.add(name)


def validate_hubs(data):
    names = set()

    for line_type, content, line_number in data:

        if line_type == "start_hub":
            validate_hub(
                content,
                line_number,
                names,
                True
            )

        elif line_type == "hub":
            validate_hub(
                content,
                line_number,
                names
            )

        elif line_type == "end_hub":
            validate_hub(
                content,
                line_number,
                names,
                True
            )


def validate_start_end(data):
    start_count = 0
    end_count = 0

    for line_type, content, line_number in data:

        if line_type == "start_hub":
            start_count += 1

            if start_count > 1:
                raise ValueError(
                    f"Line {line_number}: multiple start_hub definitions"
                )

        elif line_type == "end_hub":
            end_count += 1

            if end_count > 1:
                raise ValueError(
                    f"Line {line_number}: multiple end_hub definitions"
                )

    if start_count == 0:
        raise ValueError("Missing start_hub")

    if end_count == 0:
        raise ValueError("Missing end_hub")


def split_connection_content(content, line_number):
    metadata = None

    if "[" in content:
        if not content.endswith("]"):
            raise ValueError(
                f"Line {line_number}: invalid metadata syntax"
            )

        main, metadata = content.split("[", 1)
        metadata = metadata[:-1].strip()
        main = main.strip()
    else:
        main = content

    parts = main.split("-")

    if len(parts) != 2:
        raise ValueError(
            f"Line {line_number}: invalid connection syntax"
        )

    zone1 = parts[0].strip()
    zone2 = parts[1].strip()

    if not zone1 or not zone2:
        raise ValueError(
            f"Line {line_number}: invalid connection syntax"
        )

    return zone1, zone2, metadata


def validate_connection_metadata(metadata, line_number):
    values = parse_metadata(metadata, line_number)

    if "max_link_capacity" in values:
        value = values["max_link_capacity"]

        if not value.isdigit() or int(value) <= 0:
            raise ValueError(
                f"Line {line_number}: max_link_capacity must be "
                f"a positive integer"
            )


def validate_connection(
    content,
    line_number,
    defined_hubs,
    connections
):
    zone1, zone2, metadata = split_connection_content(
        content,
        line_number
    )

    if zone1 not in defined_hubs:
        raise ValueError(
            f"Line {line_number}: zone '{zone1}' "
            f"was not previously defined"
        )

    if zone2 not in defined_hubs:
        raise ValueError(
            f"Line {line_number}: zone '{zone2}' "
            f"was not previously defined"
        )

    if zone1 == zone2:
        raise ValueError(
            f"Line {line_number}: connection cannot connect "
            f"a zone to itself"
        )

    connection = frozenset((zone1, zone2))

    if connection in connections:
        raise ValueError(
            f"Line {line_number}: duplicate connection"
        )

    validate_connection_metadata(
        metadata,
        line_number
    )

    connections.add(connection)


def validate_connections(data):
    defined_hubs = set()
    connections = set()

    for line_type, content, line_number in data:

        if line_type in ("start_hub", "hub", "end_hub"):
            name, x, y, metadata = split_hub_content(
                content,
                line_number
            )

            defined_hubs.add(name)

        elif line_type == "connection":
            validate_connection(
                content,
                line_number,
                defined_hubs,
                connections
            )

        elif line_type == "unknown":
            raise ValueError(
                f"Line {line_number}: unknown line type"
            )