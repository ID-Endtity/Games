import tkinter as tk
import random
import time

class SpaceRacer:
    def __init__(self, master):
        self.master = master
        master.title("Space Racer")
        master.resizable(False, False)

        # Canvas dimensions
        self.width = 800
        self.height = 600
        self.canvas = tk.Canvas(master, width=self.width, height=self.height, bg='black')
        self.canvas.pack()

        # Ship properties
        self.ship_size = 20
        self.ship_x = self.width // 2
        self.ship_y = self.height - 50
        self.ship_speed = 8          # horizontal movement step

        # Game state
        self.score = 0
        self.game_over = False
        self.base_speed = 3           # scroll speed (pixels per frame)
        self.current_speed = self.base_speed
        self.boost_end_time = 0
        self.boost_active = False

        # Object lists
        self.obstacles = []   # each: (id, x, y, type) type: 'asteroid' or 'planet'
        self.boost_pads = []  # each: (id, x, y)

        # Colors
        self.asteroid_color = 'gray'
        self.planet_color = 'brown'
        self.boost_color = 'yellow'

        # Spawn timers (in frames)
        self.spawn_counter = 0
        self.spawn_delay = 30          # frames between spawn attempts

        # Create ship (triangle)
        self.ship = self.canvas.create_polygon(
            self.ship_x - self.ship_size//2, self.ship_y,
            self.ship_x, self.ship_y - self.ship_size,
            self.ship_x + self.ship_size//2, self.ship_y,
            fill='white', outline='cyan'
        )

        # Score display
        self.score_text = self.canvas.create_text(10, 10, anchor='nw',
                                                  text=f"Score: 0",
                                                  fill='white', font=('Arial', 14))
        self.speed_text = self.canvas.create_text(10, 30, anchor='nw',
                                                  text=f"Speed: {self.current_speed:.1f}",
                                                  fill='white', font=('Arial', 12))

        # Bind keys
        master.bind('<Left>', self.move_left)
        master.bind('<Right>', self.move_right)
        master.focus_set()

        # Start game loop
        self.update()

    def move_left(self, event):
        if not self.game_over:
            self.ship_x = max(self.ship_size//2, self.ship_x - self.ship_speed)
            self.update_ship_position()

    def move_right(self, event):
        if not self.game_over:
            self.ship_x = min(self.width - self.ship_size//2, self.ship_x + self.ship_speed)
            self.update_ship_position()

    def update_ship_position(self):
        coords = [
            self.ship_x - self.ship_size//2, self.ship_y,
            self.ship_x, self.ship_y - self.ship_size,
            self.ship_x + self.ship_size//2, self.ship_y
        ]
        self.canvas.coords(self.ship, *coords)

    def spawn_object(self):
        """Randomly spawn either an obstacle or a boost pad."""
        # Decide type: 0 = asteroid, 1 = planet, 2 = boost pad
        r = random.random()
        if r < 0.6:         # 60% asteroid
            type_ = 'asteroid'
            size = random.randint(15, 25)
            color = self.asteroid_color
            x = random.randint(size, self.width - size)
            obj_id = self.canvas.create_oval(x - size//2, -size, x + size//2, size,
                                             fill=color, outline='white')
            self.obstacles.append((obj_id, x, -size, type_, size))
        elif r < 0.85:      # 25% planet (larger)
            type_ = 'planet'
            size = random.randint(30, 45)
            color = self.planet_color
            x = random.randint(size, self.width - size)
            obj_id = self.canvas.create_oval(x - size//2, -size, x + size//2, size,
                                             fill=color, outline='orange')
            self.obstacles.append((obj_id, x, -size, type_, size))
        else:               # 15% boost pad
            size = 12
            x = random.randint(size, self.width - size)
            obj_id = self.canvas.create_rectangle(x - size//2, -size, x + size//2, size,
                                                  fill=self.boost_color, outline='white')
            self.boost_pads.append((obj_id, x, -size, size))

    def update(self):
        """Main game loop: move objects, check collisions, update score."""
        if self.game_over:
            return

        # Update speed: if boost active, check if expired
        if self.boost_active and time.time() > self.boost_end_time:
            self.boost_active = False
            self.current_speed = self.base_speed

        # Move obstacles down
        for i, (obj_id, x, y, type_, size) in enumerate(self.obstacles):
            y += self.current_speed
            self.canvas.coords(obj_id, x - size//2, y - size//2,
                               x + size//2, y + size//2)
            self.obstacles[i] = (obj_id, x, y, type_, size)

            # Check collision with ship
            if self.check_collision(x, y, size):
                self.game_over = True
                self.canvas.create_text(self.width//2, self.height//2,
                                        text="GAME OVER", fill='red', font=('Arial', 36))
                return

            # Remove if off screen
            if y - size//2 > self.height:
                self.canvas.delete(obj_id)
                self.obstacles.pop(i)
                # Increase score for avoiding obstacle
                self.score += 10
                break   # list changed, restart loop next frame

        # Move boost pads down
        for i, (obj_id, x, y, size) in enumerate(self.boost_pads):
            y += self.current_speed
            self.canvas.coords(obj_id, x - size//2, y - size//2,
                               x + size//2, y + size//2)
            self.boost_pads[i] = (obj_id, x, y, size)

            # Check collision with ship
            if self.check_boost_collision(x, y, size):
                self.activate_boost()
                self.canvas.delete(obj_id)
                self.boost_pads.pop(i)
                continue

            # Remove if off screen
            if y - size//2 > self.height:
                self.canvas.delete(obj_id)
                self.boost_pads.pop(i)

        # Spawn new objects occasionally
        self.spawn_counter += 1
        if self.spawn_counter >= self.spawn_delay:
            self.spawn_counter = 0
            self.spawn_object()

        # Update UI
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
        self.canvas.itemconfig(self.speed_text, text=f"Speed: {self.current_speed:.1f}")

        # Schedule next frame (~30 fps)
        self.master.after(33, self.update)

    def check_collision(self, x, y, size):
        """Check if an obstacle collides with the ship."""
        # Ship is a triangle approximated by its bounding box
        ship_left = self.ship_x - self.ship_size//2
        ship_right = self.ship_x + self.ship_size//2
        ship_top = self.ship_y - self.ship_size
        ship_bottom = self.ship_y

        obj_left = x - size//2
        obj_right = x + size//2
        obj_top = y - size//2
        obj_bottom = y + size//2

        return not (obj_right < ship_left or obj_left > ship_right or
                    obj_bottom < ship_top or obj_top > ship_bottom)

    def check_boost_collision(self, x, y, size):
        """Check collision with boost pad (similar bounding box)."""
        ship_left = self.ship_x - self.ship_size//2
        ship_right = self.ship_x + self.ship_size//2
        ship_top = self.ship_y - self.ship_size
        ship_bottom = self.ship_y

        obj_left = x - size//2
        obj_right = x + size//2
        obj_top = y - size//2
        obj_bottom = y + size//2

        return not (obj_right < ship_left or obj_left > ship_right or
                    obj_bottom < ship_top or obj_top > ship_bottom)

    def activate_boost(self):
        """Increase speed for 3 seconds."""
        self.boost_active = True
        self.boost_end_time = time.time() + 3.0
        self.current_speed = self.base_speed * 2.5
        # Visual feedback: flash or change speed text color? Optional.
        self.canvas.itemconfig(self.speed_text, fill='yellow')
        # Reset color after boost ends (handled in update)
        self.master.after(3000, lambda: self.canvas.itemconfig(self.speed_text, fill='white'))

def main():
    root = tk.Tk()
    game = SpaceRacer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
