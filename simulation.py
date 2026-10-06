from classes import Drone, PathInfo
from path import path

class Simulation:
    def __init__(self, network, data):
        self.network = network
        self.drones = []
        self.turn = 0

        self.pathfinder = path(network)
        self.path_infos = []

        self.create_drones(int(data[0][1]))
        self.find_paths()
        self.sort_path()
        self.print_shared_zones()
        self.assign_paths()
        #self.run()

        for drone in self.drones:
            print(
                "Drone",
                drone.id,
                "->",
                [zone.name for zone in drone.path]
            )

    def create_drones(self, number_of_drones):
        for i in range(number_of_drones):
            drone = Drone(i + 1)
            drone.current_zone = self.network.start
            self.drones.append(drone)

    def assign_paths(self):
        for drone in self.drones:
            best_path = self.get_best_path()

            if best_path is None:
                return

            drone.path = best_path.zones.copy()
            best_path.assigned_drones += 1

    def move_drone(self, drone):
        if drone.moving:
            return

        if drone.path_index == len(drone.path) - 1:
            return

        next_zone = drone.path[drone.path_index + 1]
        cost = self.network.get_cost(next_zone)

        if cost is None:
            return

        if not self.can_enter_zone(next_zone):
            return

        if not self.can_use_connection(
            drone.current_zone,
            next_zone
        ):
            return

        drone.remaining_turns = cost
        drone.next_zone = next_zone
        drone.moving = True

    def is_finished(self):
        for drone in self.drones:
            if not drone.path:
                return False
            if drone.path_index != len(drone.path) - 1:
                return False
            if drone.moving:
                return False
        return True

    def move_one_step(self):
        self.turn += 1
        print("\nTURN:", self.turn)
        self.assign_waiting_drones()

        for drone in self.drones:
            self.finish_moving_drone(drone)

        proposed_moves = []
        accepted_moves = []

        for drone in self.drones:
            next_zone = self.get_proposed_move(drone)

            proposed_moves.append((drone, next_zone))

            print(
                "Drone",
                drone.id,
                "proposes:",
                next_zone.name if next_zone else "WAIT"
            )

        for drone, next_zone in proposed_moves:
            if next_zone is None:
                continue

            if self.can_accept_move(accepted_moves, proposed_moves, next_zone):
                accepted_moves.append((drone, next_zone))

        print("PROPOSED:", len(proposed_moves))
        print("ACCEPTED:", len(accepted_moves))

        for drone, next_zone in accepted_moves:
            print(
                "Drone",
                drone.id,
                "->",
                next_zone.name
            )
            self.apply_move(drone, next_zone)

        self.print_state()

    """
    def movement(self):
        step = 0
        while not self.is_finished():
            print(f"\n--- Step {step} ---")
            for drone in self.drones:
                self.move_drone(drone)
            self.print_state()
            step += 1
    """
    def can_enter_zone(self, zone):
        i = 0
        for drone in self.drones:
            if drone.current_zone == zone:
                i += 1
            elif drone.moving and drone.next_zone == zone:
                i += 1
        if zone == self.network.start or zone == self.network.end:
            return 1
        if i >= zone.max_drones:
            return 0
        return 1

    def can_use_connection(self, current_zone, next_zone):
        i = 0
        for drone in self.drones:
            if ((drone.current_zone == current_zone
                 and drone.next_zone == next_zone)
                    or (drone.current_zone == next_zone
                        and drone.next_zone == current_zone)):
                if drone.moving is True:
                    i += 1
        for con in self.network.connections:
            if ((con.zone1 == current_zone
                and con.zone2 == next_zone)
                    or (con.zone1 == next_zone
                        and con.zone2 == current_zone)):
                if (i >= con.max_link_capacity):
                    return 0
        return 1

    def find_paths(self):
        paths = self.pathfinder.find_all_paths(
            self.network.start,
            self.network.end
        )

        for current_path in paths:
            cost = self.pathfinder.get_path_cost(current_path)
            priority = self.pathfinder.get_priority_count(current_path)

            path_info = PathInfo(
                current_path,
                cost,
                priority
            )

            self.path_infos.append(path_info)

    def sort_path(self):
        self.path_infos.sort(
            key=lambda info: (info.cost, -info.priority)
        )

    def count_path_usage(self, path_info):
        count = 0

        for drone in self.drones:
            if drone.path == path_info.zones:
                count += 1
        return count

    def count_zone_usage(self, zone):
        count = 0

        for drone in self.drones:
            if zone in drone.path:
                count += 1

        return count

    def can_assign_path(self, path_info):
        for zone in path_info.zones:
            if zone == self.network.start or zone == self.network.end:
                continue
            usage = self.count_zone_usage(zone)

            if usage >= zone.max_drones:
                return False

        return True

    def assign_waiting_drones(self):
        for drone in self.drones:
            if drone.path:
                continue
            for path_info in self.path_infos:
                if self.can_assign_path(path_info):
                    drone.path = path_info.zones
                    break

    def get_best_path(self):
        best_path = None
        for path_info in self.path_infos:
            if best_path is None:
                best_path = path_info
                continue
            if path_info.cost < best_path.cost:
                best_path = path_info
            elif path_info.cost == best_path.cost:
                if path_info.priority > best_path.priority:
                    best_path = path_info
                elif path_info.priority == best_path.priority:
                    if path_info.assigned_drones < best_path.assigned_drones:
                        best_path = path_info
        return best_path

    def run(self):
        i = 0
        while not self.is_finished():
            i += 1
            self.move_one_step()
        print(i)

    def print_shared_zones(self):
        for i, path1 in enumerate(self.path_infos):
            for j, path2 in enumerate(self.path_infos):
                if i >= j:
                    continue

                shared = []

                for zone in path1.zones:
                    if zone in path2.zones:
                        shared.append(zone.name)

                print("PATH", i, "and PATH", j)
                print("shared:", shared)

    def finish_moving_drone(self, drone):
        print(
            "FINISH:",
            drone.id,
            "moving =", drone.moving,
            "remaining =", drone.remaining_turns
        )
        if not drone.moving:
            return
        drone.remaining_turns -=1

        if drone.remaining_turns == 0:
            drone.path_index += 1
            drone.current_zone = drone.next_zone
            drone.next_zone = None
            drone.moving = False

    def get_proposed_move(self, drone):
        if drone.moving:
            return None

        if drone.path_index == len(drone.path) - 1:
            return None

        next_zone = drone.path[drone.path_index + 1]
        cost = self.network.get_cost(next_zone)

        if cost is None:
            return None

        return next_zone

    def can_accept_move(self, accepted_moves, proposed_moves, next_zone):
        if next_zone == self.network.start:
            return True

        if next_zone == self.network.end:
            return True

        current = self.count_current_drones(next_zone)

        leaving = self.count_leaving_drones(
            next_zone,
            proposed_moves
        )

        proposed = 0

        for drone, zone in accepted_moves:
            if zone == next_zone:
                proposed += 1

        print(
            "ZONE:",
            next_zone.name,
            "current:",
            current,
            "leaving:",
            leaving,
            "accepted:",
            proposed
        )

        return current - leaving + proposed < next_zone.max_drones

    def count_proposed_entries(self, proposed_moves, zone):
        count = 0

        for drone, next_zone in proposed_moves:
            if next_zone == zone:
                count += 1

        return count

    def apply_move(self, drone, next_zone):
        cost = self.network.get_cost(next_zone)

        print(
            "APPLY:",
            drone.id,
            "zone:",
            next_zone.name,
            "cost:",
            cost
        )
        drone.remaining_turns = cost
        drone.next_zone = next_zone
        drone.moving = True


    def count_current_drones(self, zone):
        count = 0

        for drone in self.drones:
            if drone.current_zone == zone:
                count +=1

        return count

    def count_leaving_drones(self, zone, proposed_moves):
        count = 0

        for drone, next_zone in proposed_moves:
            if drone.current_zone == zone and next_zone != zone and next_zone is not None:
                count += 1
        return count

    def print_state(self):
        for drone in self.drones:
            print(
                drone.id,
                "cur:",
                drone.current_zone.name,
                "next:",
                drone.next_zone.name if drone.next_zone else None,
                "moving:",
                drone.moving,
                "remaining:",
                drone.remaining_turns
            )
        print("")


