import pygame
from settings import *
from os.path import join

IMAGE_GUN = pygame.image.load(join("images", "gun.png"))
IMAGE_STAFF = pygame.image.load(join("images", "staff.png"))

def text(s,msg,pos,size=28,color=WHITE,center=True):
    f=pygame.font.SysFont('dejavusansmono',size,bold=True); r=f.render(msg,True,color); rect=r.get_rect(center=pos) if center else r.get_rect(topleft=pos);s.blit(r,rect)

def menu(s,selected,levels):
    width, height = s.get_size()
    s.fill(BLACK);text(s,'CALAMITY', (width/2,height*.17),64,CYAN);text(s,'PYGAME RAYCASTING',(width/2,height*.26),22,WHITE)
    for i,l in enumerate(levels):
        c=YELLOW if i==selected else WHITE;text(s,f'{i+1}. {l["name"]}',(width/2,height*.40+i*55),30,c)
    text(s,'ENTER: PLAY    UP/DOWN: SELECT    ESC: QUIT',(width/2,height*.80),18,WHITE)

def hud(s,level_idx,enemies,player,ammo,reloading,selected_weapon, coins):
    width, height = s.get_size()
    text(s,f'COINS: {coins}',(width*.4,25),18,WHITE)
    text(s,f'LEVEL {level_idx+1}',(width*.62,25),18,WHITE);text(s,f'ENEMIES {enemies}',(width*.84,25),18,WHITE)
    pygame.draw.rect(s,(50,0,0),(20,height-35,260,18));pygame.draw.rect(s,GREEN,(20,height-35,260*player.health/player.max_health,18));text(s,f'HP {int(player.health)}',(150,height-26),15,WHITE)
    weapon_name=('SMALL','BIG')[selected_weapon]
    text(s,f'SMALL {ammo[0]}   BIG {ammo[1]}   SELECTED: {weapon_name}', (width*.70,height-26),16,WHITE)
    text(s,'W/S move  A/D turn  SPACE dash  LMB fire  1/2 select weapon  R reload',(width/2,height-55),15,WHITE)

def viewmodel(s, bob, weapon=1):
    """Draw a simple two-rectangle first-person viewmodel."""
    width, height = s.get_size()
    y = int(height - 150 + bob)
    # These are deliberately only two generic rectangular weapon/hand forms.
    if weapon == 0:
        s.blit(IMAGE_GUN, (int(width*.30), y-69, int(width*.16), 115))
    elif weapon == 1:
        s.blit(IMAGE_STAFF, (int(width*.30), y-42, int(width*.16), 115))
        