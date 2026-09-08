import math
import pygame
from .geometry import segment_intersection

class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.a=(float(x1),float(y1)); self.b=(float(x2),float(y2))

    def draw(self, surface, offset=(0,0)):
        ox, oy=offset
        pygame.draw.line(surface,(235,235,235),(self.a[0]+ox,self.a[1]+oy),(self.b[0]+ox,self.b[1]+oy),5)

    def ray_hit(self, origin, direction, max_dist=1000):
        end=(origin[0]+direction[0]*max_dist, origin[1]+direction[1]*max_dist)
        hit=segment_intersection(origin,end,self.a,self.b)
        if not hit: return None
        x,y,t=hit
        return x,y,t*max_dist

    def collides_circle(self, center, radius):
        # Distance from point to segment.
        px,py=center; ax,ay=self.a; bx,by=self.b
        vx,vy=bx-ax,by-ay; wx,wy=px-ax,py-ay
        denom=vx*vx+vy*vy
        t=0 if denom==0 else max(0,min(1,(wx*vx+wy*vy)/denom))
        qx,qy=ax+t*vx,ay+t*vy
        return math.hypot(px-qx,py-qy) < radius
