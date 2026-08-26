def validate_nb_drones(data):
    line_type, content = data

    if line_type != "nb_drones":
        raise ValueError(
            "Line : first line must be nb_drones"
        )

    if not content.isdigit() or int(content) <= 0:
        raise ValueError(
            "Line : nb_drones must be a positive integer"
        )


def split_hub_content(content):
    metadata = None

    if "[" in content:
        if not content.endswith("]"):
            raise ValueError("invalid metadata syntax")

        main, metadata = content.split("[", 1)
        metadata = metadata[:-1].strip()
        main = main.strip()
    else:
        main = content

    parts = main.split()

    if len(parts) != 3:
        raise ValueError("invalid hub syntax")

    name, x, y = parts

    return name, x, y, metadata

