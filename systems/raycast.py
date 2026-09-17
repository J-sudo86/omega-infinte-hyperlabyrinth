import math, pygame
from settings import *


class Raycaster:
    def __init__(self):
        self.dists = []

    def cast(self, player, walls):
        self.dists = []
        rays = int(FOV / RAY_STEP)
        for i in range(rays):
            a = player.angle - FOV / 2 + (i / (rays - 1)) * FOV
            direction = (math.cos(a), math.sin(a))
            best = None
            for w in walls:
                hit = w.ray_hit(player.pos, direction, 900)
                if hit and (best is None or hit[2] < best):
                    best = hit[2]
            # Store fish-eye-corrected distance for sprite occlusion.
            if best is not None:
                best *= math.cos(a - player.angle)
            self.dists.append(best)

    def draw_3d(self, surface, wall_color=(170, 170, 180)):
        view_width, view_height = surface.get_size()
        for i, d in enumerate(self.dists):
            if d is None:
                continue
            d = max(.1, d)
            # Taller wall slices make the raytraced walls read as longer.
            h = min(view_height, 1800 / d)
            shade = max(35, min(255, int(255 - 0.7 * d)))
            col = tuple(int(c * shade / 255) for c in wall_color)
            x = i * view_width / len(self.dists)
            pygame.draw.rect(
                surface,
                col,
                (int(x), int(view_height / 2 - h / 2), max(1, int(view_width / len(self.dists) + 1)), int(h)),
            )

    def project(self, player, pos, world_radius=10, height_scale=1.0):
        """Project a world-space object into the full-window 3D view."""
        dx = pos[0] - player.x
        dy = pos[1] - player.y
        distance = math.hypot(dx, dy)
        if distance <= 0.01:
            return None

        relative = math.atan2(dy, dx) - player.angle
        relative = (relative + math.pi) % (2 * math.pi) - math.pi
        if abs(relative) > FOV / 2 + 0.08:
            return None

        corrected = distance * math.cos(relative)
        if corrected <= 0.05:
            return None

        view_width, _ = pygame.display.get_surface().get_size()
        screen_x = (relative / FOV + 0.5) * view_width
        # 3D sprite scale. Larger world_radius means a genuinely larger sprite.
        size = max(2, (world_radius * 900 / corrected) * height_scale)
        return screen_x, corrected, size

    def wall_depth_at(self, screen_x):
        """Return the wall depth at a projected screen x coordinate."""
        if not self.dists:
            return 9999.0
        view_width, _ = pygame.display.get_surface().get_size()
        if screen_x < 0 or screen_x >= view_width:
            return 9999.0
        fraction = screen_x / view_width
        idx = int(fraction * len(self.dists))
        idx = max(0, min(len(self.dists) - 1, idx))
        return self.dists[idx] if self.dists[idx] is not None else 9999.0
