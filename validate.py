
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
            )