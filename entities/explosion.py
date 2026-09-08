import math, pygame
from core.geometry import line_of_sight
from settings import *

class Explosion:
    def __init__(self,x,y):self.x=x;self.y=y;self.radius=4;self.max_radius=105;self.life=.42;self.hit=set()
    @property
    def alive(self):return self.life>0
    def update(self,dt,enemies,player,walls):
        self.life-=dt; self.radius=self.max_radius*(1-self.life/.42)
        for e in enemies:
            if e.alive and id(e) not in self.hit and math.hypot(self.x-e.x,self.y-e.y)<=self.radius and line_of_sight((self.x,self.y),e.pos,walls):
                e.hit(30);self.hit.add(id(e))
        if math.hypot(self.x-player.x,self.y-player.y)<=self.radius and line_of_sight((self.x,self.y),player.pos,walls):
            player.health=max(0,player.health-25*dt)
    def draw(self,s):
        if self.alive:
            pygame.draw.circle(s,ORANGE,(int(self.x),int(self.y)),max(1,int(self.radius)),4)
