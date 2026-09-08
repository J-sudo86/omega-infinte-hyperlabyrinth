import math, pygame
from core.geometry import move_circle, line_of_sight
from settings import *

class Enemy:
    def __init__(self,x,y,hp=20,speed=65,attack_damage=10):
        self.x=x
        self.y=y
        self.max_health=hp
        self.health=hp
        self.speed=speed
        self.attack_damage=attack_damage
        self.alive=True; self.attack_cd=0; self.path=[]; self.path_timer=0
    @property
    def pos(self):
        return (self.x,self.y)
    def update(self,dt,player,walls,pathfinder):
        if not self.alive:return
        self.attack_cd=max(0,self.attack_cd-dt); self.path_timer-=dt
        d=math.hypot(player.x-self.x,player.y-self.y)
        if d<28 and line_of_sight(self.pos,player.pos,walls):
            if self.attack_cd<=0: player.health=max(0,player.health-self.attack_damage); self.attack_cd=.65
            return
        if self.path_timer<=0:
            self.path=pathfinder.find_path(self.pos,player.pos); self.path_timer=.18
        target=player.pos
        if len(self.path)>1: target=self.path[1]
        ang=math.atan2(target[1]-self.y,target[0]-self.x)
        self.x, self.y = move_circle(
            self.pos,
            (math.cos(ang) * self.speed * dt, math.sin(ang) * self.speed * dt),
            radius=12,
            walls=walls)
    def hit(self,damage):
        self.health-=damage
        if self.health<=0:self.health=0;self.alive=False
    def draw(self,s):
        if not self.alive:return
        pygame.draw.circle(s,RED,(int(self.x),int(self.y)),36)
        pygame.draw.rect(s,(60,0,0),(self.x-15,self.y-22,30,4)); pygame.draw.rect(s,GREEN,(self.x-15,self.y-22,30*self.health/self.max_health,4))
