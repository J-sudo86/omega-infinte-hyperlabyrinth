import math
import random
import pygame
from core.geometry import segment_intersection
from settings import *


class Shrapnel:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = random.uniform(140, 280)
        self.life = random.uniform(.45, .9)
        self.alive = True
        self.damage = 2

    @property
    def pos(self):
        return self.x, self.y

    def update(self, dt, walls, enemies):
        if not self.alive:
            return
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return

        old = self.pos
        new = (
            self.x + math.cos(self.angle) * self.speed * dt,
            self.y + math.sin(self.angle) * self.speed * dt,
        )

        # Shrapnel cannot pass through walls.
        for wall in walls:
            hit = segment_intersection(old, new, wall.a, wall.b)
            if hit:
                self.x, self.y = hit[0], hit[1]
                self.alive = False
                return

        self.x, self.y = new
        for enemy in enemies:
            if enemy.alive and math.hypot(self.x - enemy.x, self.y - enemy.y) < enemy.radius + 4:
                enemy.hit(self.damage)
                self.alive = False
                return

        if not (0 <= self.x <= WORLD_W and 0 <= self.y <= WORLD_H):
            self.alive = False

    def draw(self, surface):
        if self.alive:
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), 3)
