import tkinter as tk
import random

class WolfCatchEggs:
    def __init__(self, master):
        self.master = master
        master.title("Wolf Catch Eggs")
        master.resizable(False, False)

        # Game constants
        self.canvas_width = 600
        self.canvas_height = 400
        self.wolf_width = 80
        self.wolf_height = 30
        self.wolf_y = self.canvas_height - 50  # near bottom
        self.egg_radius = 12
        self.egg_speed = 3
        self.max_misses = 10

        # Game state
        self.score = 0
        self.misses = 0
        self.game_over = False
        self.eggs = []          # list of egg canvas ids
        self.egg_positions = [] # list of (x, y) for each egg (for collision)

        # Create UI
        self.canvas = tk.Canvas(master, width=self.canvas_width,
                                height=self.canvas_height, bg='sky blue')
        self.canvas.pack()

        # Draw wolf (a simple rectangle)
        self.wolf = self.canvas.create_rectangle(
            0, 0, self.wolf_width, self.wolf_height,
            fill='brown', outline='black'
        )
        self.update_wolf_position(self.canvas_width//2)

        # Score display
        self.score_text = self.canvas.create_text(
            10, 10, anchor='nw', text=f"Score: {self.score}  Misses: {self.misses}/{self.max_misses}",
            font=('Arial', 14), fill='white'
        )

        # Key bindings
        master.bind('<Left>', self.move_left)
        master.bind('<Right>', self.move_right)
        master.focus_set()

        # Start game loops
        self.create_egg()
        self.update()

    def update_wolf_position(self, center_x):
        """Move wolf so its center is at center_x."""
        x1 = center_x - self.wolf_width//2
        y1 = self.wolf_y - self.wolf_height//2
        x2 = center_x + self.wolf_width//2
        y2 = self.wolf_y + self.wolf_height//2
        self.canvas.coords(self.wolf, x1, y1, x2, y2)

    def move_left(self, event):
        if not self.game_over:
            coords = self.canvas.coords(self.wolf)
            if coords:
                new_center = (coords[0] + coords[2])//2 - 15
                if new_center - self.wolf_width//2 > 0:
                    self.update_wolf_position(new_center)

    def move_right(self, event):
        if not self.game_over:
            coords = self.canvas.coords(self.wolf)
            if coords:
                new_center = (coords[0] + coords[2])//2 + 15
                if new_center + self.wolf_width//2 < self.canvas_width:
                    self.update_wolf_position(new_center)

    def create_egg(self):
        """Create a new egg at a random top position."""
        if self.game_over:
            return
        x = random.randint(self.egg_radius, self.canvas_width - self.egg_radius)
        y = self.egg_radius
        egg_id = self.canvas.create_oval(
            x - self.egg_radius, y - self.egg_radius,
            x + self.egg_radius, y + self.egg_radius,
            fill='yellow', outline='orange'
        )
        self.eggs.append(egg_id)
        self.egg_positions.append([x, y])  # mutable list for updates
        # Schedule next egg after random delay (0.5 to 1.5 seconds)
        self.master.after(random.randint(500, 1500), self.create_egg)

    def check_collision(self, egg_x, egg_y, egg_idx):
        """Check if egg collides with wolf."""
        wolf_coords = self.canvas.coords(self.wolf)
        if not wolf_coords:
            return False
        wx1, wy1, wx2, wy2 = wolf_coords
        # Simple bounding box collision
        if (wx1 < egg_x < wx2) and (wy1 < egg_y < wy2):
            return True
        return False

    def update(self):
        """Game loop: move eggs, check collisions, update display."""
        if not self.game_over:
            # Move each egg down
            to_remove = []
            for i, (egg_id, pos) in enumerate(zip(self.eggs, self.egg_positions)):
                pos[1] += self.egg_speed
                self.canvas.coords(egg_id,
                                   pos[0] - self.egg_radius, pos[1] - self.egg_radius,
                                   pos[0] + self.egg_radius, pos[1] + self.egg_radius)

                # Collision detection
                if self.check_collision(pos[0], pos[1], i):
                    self.score += 1
                    to_remove.append(i)
                    continue

                # Egg reached bottom (miss)
                if pos[1] + self.egg_radius >= self.canvas_height:
                    self.misses += 1
                    to_remove.append(i)

            # Remove eggs that were caught or missed (from end to start to keep indices valid)
            for i in reversed(to_remove):
                self.canvas.delete(self.eggs[i])
                del self.eggs[i]
                del self.egg_positions[i]

            # Update score display
            self.canvas.itemconfig(self.score_text,
                                   text=f"Score: {self.score}  Misses: {self.misses}/{self.max_misses}")

            # Check game over
            if self.misses >= self.max_misses:
                self.game_over = True
                self.canvas.create_text(self.canvas_width//2, self.canvas_height//2,
                                        text="GAME OVER", font=('Arial', 24), fill='red')
                return  # stop update loop

        # Continue loop every 30ms
        self.master.after(30, self.update)

def main():
    root = tk.Tk()
    game = WolfCatchEggs(root)
    root.mainloop()

if __name__ == "__main__":
    main()