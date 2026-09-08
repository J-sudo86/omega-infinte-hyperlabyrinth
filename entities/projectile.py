import math, pygame
from core.geometry import segment_intersection
from settings import *

class Projectile:
    def __init__(self,x,y,angle,speed,damage,big=False):
        self.x=x;self.y=y;self.angle=angle;self.speed=speed;self.damage=damage;self.big=big;self.alive=True
    def update(self,dt,walls,enemies):
        old=(self.x,self.y); new=(self.x+math.cos(self.angle)*self.speed*dt,self.y+math.sin(self.angle)*self.speed*dt)
        closest=None
        for w in walls:
            hit=segment_intersection(old,new,w.a,w.b)
            if hit and (closest is None or hit[2]<closest[2]):closest=hit
        if closest:
            self.x,self.y=closest[0],closest[1];self.alive=False
            return ('explosion',self.x,self.y) if self.big else None
        self.x,self.y=new
        for e in enemies:
            if e.alive and math.hypot(self.x-e.x,self.y-e.y)<16:
                e.hit(self.damage);self.alive=False
                return ('explosion',self.x,self.y) if self.big else None
        if not (0<=self.x<=WORLD_W and 0<=self.y<=WORLD_H):self.alive=False
        return None
    def draw(self,s):
        if self.alive:pygame.draw.circle(s,ORANGE,(int(self.x),int(self.y)),5 if not self.big else 8)
