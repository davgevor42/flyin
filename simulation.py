from classes import Drone
from path import path

class Simulation:
    def __init__(self, network, data):
        self.network = network
        self.drones = []

        self.pathfinder = path(network)
        self.create_drones(int(data[0][1]))
        self.assign_path()

    def create_drones(self, number_of_drones):
        for i in range(number_of_drones):
            drone = Drone(i + 1)
            drone.current_zone = self.network.start
            self.drones.append(drone)

    def assign_path(self):
        for drone in self.drones:
            drone.path = self.pathfinder.find_path(
                self.network.start,
                self.network.end
            )

    def move_drone(self, drone):
        if (drone.moving is True):
            drone.remaining_turns -= 1
            if (drone.remaining_turns == 0):
                drone.path_index += 1
                drone.current_zone = drone.next_zone
                drone.next_zone = None
                drone.moving = False
        elif (drone.moving is False):
            if drone.path_index != len(drone.path) - 1:
                next_zone = drone.path[drone.path_index + 1]
                cost = self.network.get_cost(next_zone)
                if self.can_enter_zone(next_zone):
                    drone.remaining_turns = cost
                    drone.next_zone = next_zone
                    drone.moving = True

    def is_finished(self):
        for drone in self.drones:
            if drone.path_index != len(drone.path) - 1 or drone.moving:
                return 0
        return 1

    def movement(self):
        step = 0
        while not self.is_finished():
            print(f"\n--- Step {step} ---")
            for drone in self.drones:
                self.move_drone(drone)
            self.print_state()
            step += 1

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

    def print_state(self):
        for drone in self.drones:
            print(
                drone.id,
                drone.current_zone.name,
                drone.next_zone.name if drone.next_zone else None,
                drone.remaining_turns
            )


