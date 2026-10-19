import tkinter as tk

from classes import Map, Zone
from simulation import Simulation


class Visualizer:
    MARGIN = 60

    def __init__(self, graph: Map, simulation: Simulation) -> None:
        self.graph = graph
        self.simulation = simulation

        self.scale = 100.0
        self.off_x = 0.0
        self.off_y = 0.0
        self.min_x = 0
        self.max_y = 0

        self.root = tk.Tk()
        self.root.title("Fly-in Map")
        self.root.geometry("900x650")
        self.root.minsize(400, 300)

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill="both", expand=True)
        bar = tk.Frame(self.root)
        bar.pack(fill="x")
        self.button = tk.Button(bar, text="Next Step", command=self.next_step)
        self.button.pack(side="right", padx=5, pady=5)
        self.label = tk.Label(bar, text="Turns: 0")
        self.label.pack(side="left", padx=10)

        self.canvas.bind("<Configure>", lambda event: self.redraw())

    def run(self) -> None:
        self.root.mainloop()

    def destroy(self) -> None:
        self.root.destroy()

    def get_map_bounds(self) -> tuple[int, int, int, int]:
        zones = self.graph.zones.values()
        return (min(z.x for z in zones), max(z.x for z in zones),
                min(z.y for z in zones), max(z.y for z in zones))

    def update_transform(self) -> None:
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        min_x, max_x, min_y, max_y = self.get_map_bounds()
        span_x = max_x - min_x
        span_y = max_y - min_y

        avail_w = max(width - 2 * self.MARGIN, 1)
        avail_h = max(height - 2 * self.MARGIN, 1)
        self.scale = min(avail_w / max(span_x, 1),
                         avail_h / max(span_y, 1))

        self.off_x = (width - span_x * self.scale) / 2
        self.off_y = (height - span_y * self.scale) / 2
        self.min_x = min_x
        self.max_y = max_y

    def map_to_screen(self, x: float, y: float) -> tuple[float, float]:
        screen_x = self.off_x + (x - self.min_x) * self.scale
        screen_y = self.off_y + (self.max_y - y) * self.scale
        return screen_x, screen_y

    def redraw(self) -> None:
        self.canvas.delete("all")
        self.update_transform()
        for con in self.graph.connections:
            x1, y1 = self.map_to_screen(con.zone1.x, con.zone1.y)
            x2, y2 = self.map_to_screen(con.zone2.x, con.zone2.y)
            self.canvas.create_line(x1, y1, x2, y2, fill="black", width=1)
        for zone in self.graph.zones.values():
            self.draw_zone(zone)
        self.draw_drones()
        self.label.config(text=f"Turn: {self.simulation.turn}")

    def draw_zone(self, zone: Zone) -> None:
        x, y = self.map_to_screen(zone.x, zone.y)
        radius = max(8, min(25, self.scale * 0.3))
        if zone.color == "rainbow":
            self.draw_rainbow_zone(x, y, radius)
        else:
            color = "white" if zone.color == "none" else zone.color
            try:
                self.canvas.create_oval(x - radius, y - radius,
                                        x + radius, y + radius, fill=color)
            except tk.TclError:
                self.canvas.create_oval(x - radius, y - radius,
                                        x + radius, y + radius, fill="white")
        self.canvas.create_text(x, y - radius - 8, text=zone.name)

    def draw_rainbow_zone(self, x: float, y: float, radius: float) -> None:
        colors = ["#ff0000", "#ff7f00", "#ffff00", "#00ff00",
                  "#0000ff", "#4b0082", "#9400d3"]
        step = radius / len(colors)
        for i, color in enumerate(colors):
            r = radius - i * step
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill=color, outline="")

    def draw_drones(self) -> None:
        self.canvas.delete("dron")
        size = max(4, min(10, self.scale * 0.12))
        for i, drone in enumerate(self.simulation.drones):
            target = drone.next_zone
            if drone.moving and target is not None:
                a = drone.current_zone
                px, py = (a.x + target.x) / 2, (a.y + target.y) / 2
            else:
                px, py = drone.current_zone.x, drone.current_zone.y
            x, y = self.map_to_screen(px, py)
            x += (i % 4 - 1.5) * size * 2.2
            y += (i // 4) * size * 2.2 + size
            self.canvas.create_polygon(x, y - size, x - size, y + size,
                                       x + size, y + size,
                                       fill="gold", tags="drone")
            self.canvas.create_text(
                x, y + size * 0.4, text=str(drone.id),
                font=("Arial", max(6, int(size * 0.7))),
                fill="black", tags="drone")

    def next_step(self) -> None:
        if self.simulation.is_finished():
            return
        try:
            self.simulation.move_one_step()
        except RuntimeError as error:
            print("Simulation error:", error)
            return
        self.redraw()
