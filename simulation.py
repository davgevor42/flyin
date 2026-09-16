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