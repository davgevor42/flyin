class path:

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
