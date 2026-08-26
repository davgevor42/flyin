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
    else:
        raise ValueError("unknown line type")


def parse_file(filename):
    data = {}

    with open(filename, "r") as file:
        first_line_found = False

        for line_number, line in enumerate(file, 1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            line_type, content = parse_line(line)

            if not first_line_found:
                if line_type != "nb_drones":
                    raise ValueError(
                        f"Line {line_number}: first line must be nb_drones"
                    )
                first_line_found = True

            data[line_type] = content, line_number

    if not first_line_found:
        raise ValueError("File is empty")

    return data
