from classes import Drone, PathInfo, Map, Zone
from path import path


class Simulation:
    def __init__(self, network: Map, data: list[tuple[str, str, int]]) -> None:
        self.network = network
        self.drones: list[Drone] = []
        self.turn = 0
        self.pathfinder = path(network)
        self.path_infos: list[PathInfo] = []
        self.candidates: list[PathInfo] = []
        self.verbose = False
        self.optimistic = True

        self.create_drones(int(data[0][1]))
        self.find_paths()
        self.sort_path()
        self.choose_best_assignment()
        self.verbose = True

    def create_drones(self, number_of_drones: int) -> None:
        start = self.network.start
        if start is None:
            raise ValueError("Missing start_hub")
        for i in range(number_of_drones):
            self.drones.append(Drone(i + 1, start))

    def find_paths(self) -> None:
        start, end = self.network.start, self.network.end
        if start is None or end is None:
            raise ValueError("Missing start_hub or end_hub")
        penalties: dict[Zone, int] = {}
        known: set[tuple[str, ...]] = set()
        attempts = min(max(10, 2 * len(self.drones)), 200)

        for _ in range(attempts):
            zones = self.pathfinder.find_path(start, end, penalties)
            if not zones:
                break
            for zone in zones[1:-1]:
                penalties[zone] = penalties.get(zone, 0) + 1
            key = tuple(zone.name for zone in zones)
            if key in known:
                continue
            known.add(key)
            self.path_infos.append(PathInfo(
                zones,
                self.pathfinder.get_path_cost(zones),
                self.pathfinder.get_priority_count(zones),
                self.pathfinder.get_path_capacity(zones)
            ))
        if not self.path_infos:
            raise ValueError("No path between start_hub and end_hub")

    def sort_path(self) -> None:
        self.path_infos.sort(key=lambda info: (info.cost, -info.priority))

    def estimated_finish(self, path_infos: PathInfo) -> int:
        return (path_infos.cost + path_infos.assigned_drones
                // path_infos.capacity)

    def get_best_path(self) -> PathInfo:
        best_path = self.candidates[0]
        for path_info in self.candidates[1:]:
            finish = self.estimated_finish(path_info)
            best_finish = self.estimated_finish(best_path)
            if finish < best_finish:
                best_path = path_info
            elif finish == best_finish:
                if path_info.priority > best_path.priority:
                    best_path = path_info
                elif path_info.priority == best_path.priority:
                    if path_info.assigned_drones < best_path.assigned_drones:
                        best_path = path_info
        return best_path

    def assign_paths(self, nb_paths: int) -> None:
        self.candidates = self.path_infos[:nb_paths]
        for info in self.path_infos:
            info.assigned_drones = 0
        for drone in self.drones:
            best_path = self.get_best_path()
            drone.path = best_path.zones.copy()
            best_path.assigned_drones += 1

    def move_one_step(self) -> str:
        self.turn += 1
        events: dict[int, str] = {}

        flying = [d for d in self.drones if d.moving]

        proposed_moves: list[tuple[Drone, Zone]] = []
        for drone in self.drones:
            next_zone = self.get_proposed_move(drone)
            if next_zone is not None:
                proposed_moves.append((drone, next_zone))

        accepted_moves = self.accept_moves(proposed_moves)

        for drone in flying:
            self.finish_moving_drone(drone)
            events[drone.id] = f"D{drone.id}-{drone.current_zone.name}"
        for drone, next_zone in accepted_moves:
            events[drone.id] = self.apply_move(drone, next_zone)

        line = " ".join(events[i] for i in sorted(events))
        if not line and not self.is_finished():
            raise RuntimeError(
                f"Deadlock at turn {self.turn}: no drone can move")
        if self.verbose:
            print(line)
        return line

    def accept_moves(
            self, proposed_moves: list[tuple[Drone, Zone]]
            ) -> list[tuple[Drone, Zone]]:
        accepted_moves: list[tuple[Drone, Zone]] = []
        pending = list(proposed_moves)
        changed = True
        while changed:
            changed = False
            for move in pending[:]:
                drone, next_zone = move
                if (self.can_accept_move(accepted_moves, next_zone)
                        and self.can_use_connection(
                            accepted_moves, drone.current_zone, next_zone)):
                    accepted_moves.append(move)
                    pending.remove(move)
                    changed = True
        self.check_arrivals(accepted_moves)
        return accepted_moves

    def check_arrivals(
            self, accepted_moves: list[tuple[Drone, Zone]]
            ) -> None:
        for drone in self.drones:
            zone = drone.next_zone
            if not drone.moving or zone is None:
                continue
            if zone == self.network.start or zone == self.network.end:
                continue
            total = (self.count_current_drones(zone)
                     - self.count_leaving_drones(zone, accepted_moves)
                     + self.count_flying_to(zone)
                     + self.count_proposed_entries(accepted_moves, zone))
            if total > zone.max_drones:
                raise RuntimeError(
                    f"Turn {self.turn}: no room in {zone.name} for a "
                    "drone that is on a restricted connection")

    def can_accept_move(self, accepted_moves: list[tuple[Drone, Zone]],
                        next_zone: Zone) -> bool:
        if next_zone == self.network.start or next_zone == self.network.end:
            return True
        if self.optimistic and self.network.get_cost(next_zone) == 2:
            return True
        current = self.count_current_drones(next_zone)
        leaving = self.count_leaving_drones(next_zone, accepted_moves)
        entering = self.count_proposed_entries(accepted_moves, next_zone)
        flying = self.count_flying_to(next_zone)

        return current - leaving + entering + flying < next_zone.max_drones

    def can_use_connection(self, accepted_moves: list[tuple[Drone, Zone]],
                           current_zone: Zone, next_zone: Zone) -> bool:
        connection = self.network.get_connection(current_zone, next_zone)
        if connection is None:
            return False
        used = 0
        for drone, zone in accepted_moves:
            other = self.network.get_connection(drone.current_zone, zone)
            if other is connection:
                used += 1
        return used < connection.max_link_capacity

    def get_proposed_move(self, drone: Drone) -> Zone | None:
        if drone.moving:
            return None
        if drone.path_index == len(drone.path) - 1:
            return None
        next_zone = drone.path[drone.path_index + 1]
        if self.network.get_cost(next_zone) is None:
            return None
        return next_zone

    def apply_move(self, drone: Drone, next_zone: Zone) -> str:
        cost = self.network.get_cost(next_zone)
        origin = drone.current_zone
        if cost == 1:
            drone.current_zone = next_zone
            drone.path_index += 1
            return f"D{drone.id}-{next_zone.name}"
        drone.remaining_turns = 1
        drone.next_zone = next_zone
        drone.moving = True
        return f"D{drone.id}-{origin.name}-{next_zone.name}"

    def finish_moving_drone(self, drone: Drone) -> bool:
        if not drone.moving or drone.next_zone is None:
            return False
        drone.remaining_turns -= 1
        if drone.remaining_turns == 0:
            drone.path_index += 1
            drone.current_zone = drone.next_zone
            drone.next_zone = None
            drone.moving = False
            return True
        return False

    def count_current_drones(self, zone: Zone) -> int:
        return sum(1 for d in self.drones
                   if d.current_zone == zone and not d.moving)

    def count_leaving_drones(self, zone: Zone,
                             accepted_moves: list[tuple[Drone, Zone]]) -> int:
        return sum(1 for d, _ in accepted_moves if d.current_zone == zone)

    def count_proposed_entries(self, moves: list[tuple[Drone, Zone]],
                               zone: Zone) -> int:
        if self.optimistic and self.network.get_cost(zone) == 2:
            return 0
        return sum(1 for _, nz in moves if nz == zone)

    def count_flying_to(self, zone: Zone) -> int:
        return sum(1 for d in self.drones
                   if d.moving and d.next_zone == zone)

    def is_finished(self) -> bool:
        for drone in self.drones:
            if not drone.path:
                return False
            if drone.path_index != len(drone.path) - 1:
                return False
            if drone.moving:
                return False
        return True

    def run(self) -> int:
        i = 0
        while not self.is_finished():
            i += 1
            self.move_one_step()
        return i

    def reset(self) -> None:
        start = self.network.start
        if start is None:
            raise ValueError("Missing start_hub")
        self.turn = 0
        for drone in self.drones:
            drone.current_zone = start
            drone.path_index = 0
            drone.moving = False
            drone.next_zone = None
            drone.remaining_turns = 0

    def dry_run(self) -> int | None:
        self.reset()
        try:
            return self.run()
        except RuntimeError:
            return None

    def choose_best_assignment(self) -> None:
        best_turns: int | None = None
        best_nb = 1
        for self.optimistic in (True, False):
            for nb_paths in range(1, len(self.path_infos) + 1):
                self.assign_paths(nb_paths)
                turns = self.dry_run()
                if turns is not None and (best_turns is None
                                          or turns < best_turns):
                    best_turns = turns
                    best_nb = nb_paths
            if best_turns is not None:
                break
        if best_turns is None:
            raise ValueError("The drones cannot reach the end zone")
        self.assign_paths(best_nb)
        counts = [info.assigned_drones for info in self.path_infos]
        self.improve_counts(counts, best_turns)
        self.reset()

    def assign_counts(self, counts: list[int]) -> None:
        order = sorted(range(len(counts)),
                       key=lambda i: -self.path_infos[i].cost)
        drone_index = 0
        for i in order:
            for _ in range(counts[i]):
                self.drones[drone_index].path = self.path_infos[i].zones.copy()
                drone_index += 1

    def improve_counts(self, counts: list[int], best_turns: int) -> None:
        nb = min(len(counts), 16)
        improved = True
        while improved:
            improved = False
            for a in range(nb):
                for b in range(nb):
                    if a == b or counts[a] == 0:
                        continue
                    counts[a] -= 1
                    counts[b] += 1
                    self.assign_counts(counts)
                    turns = self.dry_run()
                    if turns is not None and turns < best_turns:
                        best_turns = turns
                        improved = True
                    else:
                        counts[a] += 1
                        counts[b] -= 1
        self.assign_counts(counts)
