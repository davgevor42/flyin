from parser import parse_file
import validate
from graph_builder import build_map
import visualizer
import path
from simulation import Simulation

if __name__ == "__main__":
    data = parse_file("01_linear_path.txt")

    validate.validate_data(data)
    graph = build_map(data)

    simulation = Simulation(graph, data)

    v = visualizer.Visualizer(graph, simulation)
    v.run()

    finder = path.path(graph)
    result = finder.find_path(graph.start, graph.end)

    print("############")
"""
    for drone in simulation.drones:
        print(drone.id, [zone.name for zone in drone.path])
"""
