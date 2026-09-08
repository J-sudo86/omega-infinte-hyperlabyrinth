import math, pygame
from settings import *

class Raycaster:
    def __init__(self): self.dists=[]
    def cast(self,player,walls):
        self.dists=[]
        rays=int(FOV/RAY_STEP)
        for i in range(rays):
            a=player.angle-FOV/2+(i/(rays-1))*FOV
            direction=(math.cos(a),math.sin(a)); best=None
            for w in walls:
                hit=w.ray_hit(player.pos,direction,900)
                if hit and (best is None or hit[2]<best):best=hit[2]
            self.dists.append(best)
    def draw_3d(self,surface,wall_color=(170,170,180)):
        for i,d in enumerate(self.dists):
            if d is None:continue
            d=max(.1,d); h=min(600,1200/d); shade=max(35,min(255,int(255-0.7*d)))
            col=tuple(int(c*shade/255) for c in wall_color)
            x=VIEW_W+i*VIEW_W/len(self.dists); pygame.draw.rect(surface,col,(int(x),int(300-h/2),max(1,int(VIEW_W/len(self.dists)+1)),int(h)))
