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


