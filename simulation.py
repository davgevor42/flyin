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
        if drone.path_index < len(drone.path) - 1:
            drone.path_index += 1
            drone.current_zone = drone.path[drone.path_index]

    def is_finished(self):
        for drone in self.drones:
            if drone.path_index != len(drone.path) - 1:
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

    def print_state(self):
        for drone in self.drones:
            print(
                f"Drone {drone.id}: "
                f"{drone.current_zone.name} "
                f"(step {drone.path_index})"
            )


