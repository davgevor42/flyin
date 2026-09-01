import tkinter as tk


class Visualizer:
    """Display the map graph."""

    def __init__(self, graph):
        self.graph = graph
        self.root = tk.Tk()
        self.root.title("Fly-in Map")
        self.root.geometry("800x600")

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill="both", expand=True)
        for i in self.graph.connections:
            self.draw_connection(i)
        for i in self.graph.zones.values():
            self.draw_zone(i)

    def run(self):
        """Start the graphical interface."""
        self.root.mainloop()
    
    def destroy(self):
        self.root.destroy()

    def map_to_screen(self, x, y):
        center_x = 100
        center_y = 800
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
            y - 100,
            text=zone.name
        )

    def draw_connection(self, con):
        zone1 = con.zone1
        zone2 = con.zone2
        x1, y1 = self.map_to_screen(zone1.x, zone1.y)
        x2, y2 = self.map_to_screen(zone2.x, zone2.y)
        self.canvas.create_line(x1, y1, x2, y2)

    def get_map_bounds(self):
        """Get the minimum and maximum map coordinates."""
        zones = self.graph.zones.values()

        min_x = min(zone.x for zone in zones)
        max_x = max(zone.x for zone in zones)
        min_y = min(zone.y for zone in zones)
        max_y = max(zone.y for zone in zones)

        return min_x, max_x, min_y, max_y

