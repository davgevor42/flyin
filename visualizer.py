import tkinter as tk


class Visualizer:
    """Display the map graph."""

    def __init__(self, graph, simulation):
        self.graph = graph
        self.simulation = simulation
        self.root = tk.Tk()
        self.root.title("Fly-in Map")
        self.root.geometry("800x600")

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill="both", expand=True)
        self.button = tk.Button(self.root, text="Next Step", command=self.next_step)
        self.button.pack()
        
        for i in self.graph.connections:
            self.draw_connection(i)
        for i in self.graph.zones.values():
            self.draw_zone(i)
        self.draw_drones(self.simulation.drones)

    def run(self):
        """Start the graphical interface."""
        self.root.mainloop()

    def destroy(self):
        self.root.destroy()

    def map_to_screen(self, x, y):
        center_x = 100
        center_y = 400
        scale = 200

        screen_x = center_x + x * scale
        screen_y = center_y - y * scale

        return screen_x, screen_y

    def draw_zone(self, zone):
        x, y = self.map_to_screen(zone.x, zone.y)
        radius = 50
        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=zone.color
        )
        self.canvas.create_text(
            x,
            y - 50,
            text=zone.name
        )

    def draw_connection(self, con):
        zone1 = con.zone1
        zone2 = con.zone2
        x1, y1 = self.map_to_screen(zone1.x, zone1.y)
        x2, y2 = self.map_to_screen(zone2.x, zone2.y)
        self.canvas.create_line(x1, y1, x2, y2)

    def draw_drone(self, drone, offset):
        if not drone.moving:
            x, y = self.map_to_screen(
                drone.current_zone.x,
                drone.current_zone.y
            )
        else:
            current = drone.current_zone
            next_zone = drone.next_zone

            x = (current.x + next_zone.x) / 2
            y = (current.y + next_zone.y) / 2

            x, y = self.map_to_screen(x, y)

        x += offset[0]
        y += offset[1]

        size = 10

        self.canvas.create_polygon(
            x, y - size,
            x - size, y + size,
            x + size, y + size,
            tags="drone"
        )

        self.canvas.create_text(
            x,
            y + 18,
            text=str(drone.id),
            tags="drone"
        )

    def draw_drones(self, drones):
        self.canvas.delete("drone")
        for i, drone in enumerate(drones):
            offset = self.get_drone_offset(i)
            self.draw_drone(drone, offset)

    def next_step(self):
        self.simulation.move_one_step()
        self.draw_drones(self.simulation.drones)

    def get_drone_offset(self, index):
        columns = 4
        spacing = 20

        column = index % columns
        row = index // columns

        x_offset = (column - 1.5) * spacing
        y_offset = row * spacing

        return x_offset, y_offset

    def get_drone_position(self, drone):
        if not drone.moving:
            return self.map_to_screen(
                drone.current_zone.x,
                drone.current_zone.y
            )

        current = drone.current_zone
        next_zone = drone.next_zone

        x = (current.x + next_zone.x) / 2
        y = (current.y + next_zone.y) / 2

        return self.map_to_screen(x, y)

    def get_map_bounds(self):
        """Get the minimum and maximum map coordinates."""
        zones = self.graph.zones.values()

        min_x = min(zone.x for zone in zones)
        max_x = max(zone.x for zone in zones)
        min_y = min(zone.y for zone in zones)
        max_y = max(zone.y for zone in zones)

        return min_x, max_x, min_y, max_y

