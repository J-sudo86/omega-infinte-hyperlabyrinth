import math
import pygame
import time
import random
import keyboard

colors = ["red", "blue", "green", "white", "purple", "orange", "cyan", "yellow"]


class Wall:
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def draw(self):
        pygame.draw.line(window, (255, 255, 255), (self.x1, self.y1), (self.x2, self.y2))


class LightRay:
    def __init__(self, x: float, y: float, ang: float):
        self.x, self.y = x, y
        self.dirx, self.diry = math.cos(ang), math.sin(ang)
        self.ang = ang

    def set_angle(self, ang: float):
        self.dirx, self.diry = math.cos(ang), math.sin(ang)

    def collision(self, wall: Wall):
        sx1, sy1 = self.x, self.y
        sx2, sy2 = self.x + self.dirx, self.y + self.diry
        wx1, wy1 = wall.x1, wall.y1
        wx2, wy2 = wall.x2, wall.y2
        denom = (wx1 - wx2) * (sy1 - sy2) - (wy1 - wy2) * (sx1 - sx2)
        if denom == 0:
            return None
        wint = ((wx1 - sx1) * (sy1 - sy2) - (wy1 - sy1) * (sx1 - sx2)) / denom
        sint = ((wy1 - wy2) * (wx1 - sx1) - (wx1 - wx2) * (wy1 - sy1)) / denom
        if 0 <= wint <= 1 and sint >= 0:
            return wx1 + wint * (wx2 - wx1), wy1 + wint * (wy2 - wy1)
        return None

    def draw(self):
        pygame.draw.line(
            window, random.choice(colors), (self.x, self.y),
            (self.x + self.dirx * 250, self.y + self.diry * 250)
        )


class LightSource:
    def __init__(self, x: float, y: float, ang: float, fov: float = 1.2, step: float = 0.002):
        self.fov = fov
        self.ang = ang
        self.step = step
        self.rays: list[LightRay] = []
        self.dists, self.lines = [], []
        self.hits = []
        self.rect = pygame.Rect(0, 0, 10, 10)
        self.rect.center = (x, y)
        self.update_rays()

    def move(self, dx: int):
        global wlst
        self.rect.move_ip(math.cos(self.ang) * dx, math.sin(self.ang) * dx)
        self.rect.centerx = clamp(self.rect.centerx, 0, 500)
        self.rect.centery = clamp(self.rect.centery, 0, 500)
        for line in wlst:
            if self.rect.clipline(line.x1, line.y1, line.x2, line.y2):
                self.rect.move_ip(-math.cos(self.ang) * dx, -math.sin(self.ang) * dx)
                print(f"Collision detected: {self.rect.x, self.rect.y}")


    def rotate(self, da: float):
        self.ang += da                                   

    def update_rays(self):
        self.rays = []
        a = -self.fov / 2
        while a < self.fov / 2:
            self.rays.append(LightRay(self.rect.centerx, self.rect.centery, a + self.ang))
            a += self.step

    def calc(self, walls):
        self.lines = []
        self.dists = []
        self.hits = []

        for ray in self.rays:
            min_dist = None
            min_hit = None
            min_wall = None

            for wall in walls:
                hit = ray.collision(wall)

                if hit is None:
                    continue

                hit_x, hit_y = hit

                raw_distance = math.hypot(
                    hit_x - ray.x,
                    hit_y - ray.y
                )

                # Fish-eye correction
                corrected_distance = (
                    raw_distance
                    * math.cos(ray.ang - self.ang)
                )

                if (
                    min_dist is None
                    or corrected_distance < min_dist
                ):
                    min_dist = corrected_distance
                    min_hit = hit
                    min_wall = wall

            self.lines.append(
                (
                    (ray.x, ray.y),
                    min_hit
                )
            )

            self.dists.append(min_dist)
            self.hits.append((min_hit, min_wall))

    def draw(self):
        for i, (xy1, xy2) in enumerate(self.lines):
            if xy2 is not None:
                pygame.draw.line(window, (255, 0, 0), xy1, xy2)
            else:
                self.rays[i].draw()
        pygame.draw.rect(window, "white", self.rect)



def clamp(a, l, h):
    return min(max(a, l), h)


def mapval(n, l1, h1, l2, h2):
    return clamp((n - l1) / (h1 - l1) * (h2 - l2) + l2, l2, h2)


def show_message(msg, x, y, colour, size=25):
    font = pygame.font.SysFont("dejavusansmono", size)
    renderedText = font.render(msg, True, colour)
    textArea = renderedText.get_rect()
    textArea.center = x, y
    window.blit(renderedText, textArea)


def random_walls(n: int):
    ret = []
    for _ in range(n):
        ret.append(Wall(
            random.randint(0, 500), random.randint(0, 500),
            random.randint(0, 500), random.randint(0, 500)
        ))
    return ret

wall_texture = pygame.image.load("wall_texture2.png")
pygame.init()



window = pygame.display.set_mode((1000, 500), pygame.DOUBLEBUF, 32)
clock = pygame.time.Clock()
pygame.display.set_caption("Ray Tracing")

window.fill((0, 0, 0))
pygame.display.update()
loop = True

src = LightSource(250, 250, 1.5 * math.pi)
wlst = random_walls(5)

down = [False, False, False, False]
last_frame = 0

while loop:
    dt = clock.tick(60) / 1000.0

    # Prevent huge movement if the game freezes
    dt = min(dt, 0.05)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False
            break
    

    if keyboard.is_pressed("w"):
        src.move(100 * dt)
    if keyboard.is_pressed("s"):
        src.move(-100 * dt)
    if keyboard.is_pressed("a"):
        src.rotate(-0.05)
    if keyboard.is_pressed("d"):
        src.rotate(0.05)

    window.fill((0, 0, 0))

    for wl in wlst:
        wl.draw()

    src.update_rays()
    src.calc(wlst)
    src.draw()

    for j, d in enumerate(src.dists):
        if d is None:
            continue

        hit, wall = src.hits[j]

        if hit is None or wall is None:
            continue

        # -----------------------------------------------------
        # Find where along the wall we hit
        # -----------------------------------------------------

        wall_dx = wall.x2 - wall.x1
        wall_dy = wall.y2 - wall.y1

        wall_length_sq = wall_dx ** 2 + wall_dy ** 2

        if wall_length_sq == 0:
            continue

        wall_pos = (
            (hit[0] - wall.x1) * wall_dx +
            (hit[1] - wall.y1) * wall_dy
        ) / wall_length_sq

        wall_pos = clamp(wall_pos, 0, 1)

        # Convert wall position into texture X coordinate
        tex_x = int(wall_pos * (wall_texture.get_width() - 1))

        # -----------------------------------------------------
        # Perspective wall height
        # -----------------------------------------------------

        height = 1400 / max(d, 0.001)

        # Don't let walls become ridiculously huge
        height = min(height, 1000)

        width = 500 / len(src.dists)

        posx = 500 + j * width
        posy = 250 - height / 2

        # -----------------------------------------------------
        # Distance shading
        # -----------------------------------------------------

        shade = 255 - mapval(
            d ** 2,
            0,
            500 ** 2,
            0,
            200
        )

        shade = int(clamp(shade, 40, 255))

        # -----------------------------------------------------
        # Grab one vertical column from the wall texture
        # -----------------------------------------------------

        tex_column = wall_texture.subsurface(
            (tex_x, 0, 1, wall_texture.get_height())
        )

        tex_column = pygame.transform.scale(
            tex_column,
            (
                max(1, int(width + 1)),
                max(1, int(height))
            )
        )

        # Apply distance lighting
        tex_column = tex_column.copy()
        tex_column.fill(
            (shade, shade, shade),
            special_flags=pygame.BLEND_RGB_MULT
        )

        window.blit(
            tex_column,
            (int(posx), int(posy))
        )

    show_message(str(round(1 / (time.time() - last_frame))) + " FPS", 50, 25, "white")
    last_frame = time.time()

    pygame.display.update()