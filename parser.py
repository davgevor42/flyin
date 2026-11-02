"""Read a map file into a list of records."""


class MapParser:
    """Read a map file into a list of (type, content, line) records."""

    @staticmethod
    def parse_line(line: str) -> tuple[str, str]:
        """Return the line type and its content without the prefix."""
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

    @staticmethod
    def parse_file(filename: str) -> list[tuple[str, str, int]]:
        """Return every meaningful line of the file as a record."""
        data: list[tuple[str, str, int]] = []

        with open(filename, "r") as file:
            for line_number, line in enumerate(file, 1):
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                line_type, content = MapParser.parse_line(line)

                data.append((line_type, content, line_number))

        return data
