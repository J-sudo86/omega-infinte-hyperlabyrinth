import pygame
from settings import *

def text(s,msg,pos,size=28,color=WHITE,center=True):
    f=pygame.font.SysFont('dejavusansmono',size,bold=True); r=f.render(msg,True,color); rect=r.get_rect(center=pos) if center else r.get_rect(topleft=pos);s.blit(r,rect)

def menu(s,selected,levels):
    s.fill(BLACK);text(s,'RAYFALL', (500,100),64,CYAN);text(s,'A* EDITION',(500,155),22,WHITE)
    for i,l in enumerate(levels):
        c=YELLOW if i==selected else WHITE;text(s,f'{i+1}. {l["name"]}',(500,240+i*55),30,c)
    text(s,'ENTER: PLAY    UP/DOWN: SELECT    ESC: QUIT',(500,480),18,WHITE)

def hud(s,level_idx,enemies,player,ammo,reloading):
    text(s,f'LEVEL {level_idx+1}',(620,25),18,WHITE);text(s,f'ENEMIES {enemies}',(840,25),18,WHITE)
    pygame.draw.rect(s,(50,0,0),(20,565,260,18));pygame.draw.rect(s,GREEN,(20,565,260*player.health/player.max_health,18));text(s,f'HP {int(player.health)}',(150,574),15,WHITE)
    text(s,f'SMALL {ammo[0]}   BIG {ammo[1]}', (720,574),16,WHITE);text(s,'W/S move  A/D turn  SPACE dash  LMB/1 small  RMB/2 big  R reload',(500,545),15,WHITE)
