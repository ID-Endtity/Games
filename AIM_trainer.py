import tkinter as tk
import time
import random

class AimTrainer:
    def __init__(self, master):
        self.master = master
        master.title("Aim Trainer (Minimal)")

        # Canvas settings
        self.canvas_width = 800
        self.canvas_height = 600
        self.target_radius = 25 # size of the target
        self.padding = self.target_radius + 5

        # Stats
        self.hits = 0
        self.misses = 0
        self.reaction_times = [] # store last few times for average
        self.target_start_time = None

        # Create GUI elements
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg='black')
        self.canvas.pack()

        self.stats_label = tk.Label(master, text="Hits: 0 | Misses: 0 | Avg Reaction: 0.00 s", font=("Arial", 14))
        self.stats_label.pack(pady=5)

        # Bind mouse click
        self.canvas.bind("<Button-1>", self.on_click)

        # Draw first target
        self.create_target()

    def create_target(self):
        """Place a new target at a random position within canvas."""
        x = random.randint(self.padding, self.canvas_width - self.padding)
        y = random.randint(self.padding, self.canvas_height - self.padding)
        # Store target ID and its bounding box for hit detection
        self.target_id = self.canvas.create_oval(
        x - self.target_radius, y - self.target_radius,
        x + self.target_radius, y + self.target_radius,
        fill='red', outline='white', width=2
        )
        # Record when this target appeared
        self.target_start_time = time.perf_counter()

    def on_click(self, event):
        """Handle mouse clicks on canvas."""
        # Get all canvas items under the click (coarse, but works)
        clicked_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)

        if self.target_id in clicked_items:
            # HIT
            self.hits += 1
            reaction = time.perf_counter() - self.target_start_time
            self.reaction_times.append(reaction)
            # Keep only last 10 times for average
            if len(self.reaction_times) > 10:
                self.reaction_times.pop(0)

            # Remove old target and create a new one
            self.canvas.delete(self.target_id)
            self.create_target()
        else:
            # MISS
            self.misses += 1

        # Update stats display
        self.update_stats()

    def update_stats(self):
        """Refresh the stats label."""
        avg_reaction = sum(self.reaction_times) / len(self.reaction_times) if self.reaction_times else 0
        self.stats_label.config(
        text=f"Hits: {self.hits} | Misses: {self.misses} | Avg Reaction: {avg_reaction:.3f} s"
        )

    def run(self):
        self.master.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    trainer = AimTrainer(root)
    trainer.run()




