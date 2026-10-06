class path:

    def __init__(self, graph):
        self.graph = graph

    def find_path(self, start, end, penalties=None):
        distance = {}
        previous = {}
        priority_count = {}
        visited = set()

        if penalties is None:
            penalties = {}

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
                    new_distance = (distance[current] + cost + penalties.get(neighbor, 0))
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

    def get_path_cost(self, current_path):
        total_cost = 0
        for zone in current_path[1:]:
            cost = self.graph.get_cost(zone)
            if cost is not None:
                total_cost += cost
        return total_cost

    def get_path_capacity(self, current_path):
        capacity = None
        for i in range(len(current_path) - 1):
            link = self.graph.get_connection(current_path[i], current_path[i + 1])
            if link is not None:
                value = link.max_link_capacity
                capacity = value if capacity is None else min(capacity, value)
        for zone in current_path[1:-1]:
            capacity = (zone.max_drones if capacity is None
                        else min(capacity, zone.max_drones))
        return capacity if capacity is not None else 1
    
    def get_priority_count(self, current_path):
        count = 0

        for zone in current_path[1:]:
            if zone.zone_type == "priority":
                count += 1

        return count
