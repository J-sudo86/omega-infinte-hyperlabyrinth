import math, pygame
from core.geometry import move_circle, clamp

from settings import *

class Player:
    def __init__(self,x,y,angle=0):
        self.x=x; self.y=y; self.angle=angle; self.health=100; self.max_health=100
        self.speed=0; self.dash_left=0; self.dash_cd=0; self.dash_damage=8; self.dash_hits={}
    @property
    def pos(self): return (self.x,self.y)
    def update(self,dt,walls, enemies):
        keys=pygame.key.get_pressed()
        self.angle += (keys[pygame.K_d]-keys[pygame.K_a]) * 2.4 * dt
        if self.dash_cd > 0:
            self.dash_cd -= dt
        forward = keys[pygame.K_w] - keys[pygame.K_s]
        self.speed += forward * PLAYER_SPEED
        self.speed *= PLAYER_FRICTION
        if self.speed < 10:
            self.speed = 0
        if self.speed > PLAYER_MAX_SPEED:
            self.speed = PLAYER_MAX_SPEED
        dx = math.cos(self.angle) * self.speed * dt
        dy = math.sin(self.angle) * self.speed * dt
        if self.dash_left > 0:
            self.dash_left -= dt
            for e in enemies:
                if e.alive and math.hypot(self.x-e.x,self.y-e.y) < PLAYER_RADIUS+e.radius:
                    e.hit(DASH_DAMAGE)
            dx = math.cos(self.angle) * DASH_SPEED * dt
            dy = math.sin(self.angle) * DASH_SPEED * dt
        self.x, self.y = move_circle(
            (self.x,self.y),
            (dx,dy),
            PLAYER_RADIUS,
            walls,
            is_permeable=(self.dash_left > 0)
            )
        self.x = clamp(self.x, PLAYER_RADIUS, WORLD_W - PLAYER_RADIUS)
        self.y = clamp(self.y, PLAYER_RADIUS, WORLD_H - PLAYER_RADIUS)
    def dash(self):
        if self.dash_cd<=0 and self.dash_left<=0:
            self.dash_left = DASH_TIME
            self.dash_cd = DASH_COOLDOWN
    def draw(self,s):
        pygame.draw.circle(s,WHITE,(int(self.x),int(self.y)),7)
        pygame.draw.line(s,CYAN,(self.x,self.y),(self.x+math.cos(self.angle)*18,self.y+math.sin(self.angle)*18),3)
