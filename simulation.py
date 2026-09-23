from classes import Drone, PathInfo
from path import path

class Simulation:
    def __init__(self, network, data):
        self.network = network
        self.drones = []

        self.pathfinder = path(network)
        self.path_infos = []

        paths = self.pathfinder.find_all_paths(
        self.network.start,
        self.network.end
        )

        self.create_drones(int(data[0][1]))
        self.find_paths()
        self.sort_path()
        self.assign_paths()
        for path_info in self.path_infos:
            count = self.count_path_usage(path_info)
            print(count)
        for path_info in self.path_infos:
            print(
                [zone.name for zone in path_info.zones],
                self.can_assign_path(path_info)
            )
        for drone in self.drones:
            print(
                "Drone", drone.id,
                "->",
                [zone.name for zone in drone.path]
            )

    def create_drones(self, number_of_drones):
        for i in range(number_of_drones):
            drone = Drone(i + 1)
            drone.current_zone = self.network.start
            self.drones.append(drone)

    def assign_paths(self):
        if not self.path_infos:
            return

        for i, drone in enumerate(self.drones):
            path_info = self.path_infos[i % len(self.path_infos)]
            drone.path = path_info.zones

    def move_drone(self, drone):
        if drone.moving:
            drone.remaining_turns -= 1

            if drone.remaining_turns == 0:
                drone.path_index += 1
                drone.current_zone = drone.next_zone
                drone.next_zone = None
                drone.moving = False
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
        self.assign_waiting_drones()

        for drone in self.drones:
            self.move_drone(drone)

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

    def print_state(self):
        for drone in self.drones:
            print(
                drone.id,
                drone.current_zone.name,
                drone.next_zone.name if drone.next_zone else None,
                drone.remaining_turns
            )


