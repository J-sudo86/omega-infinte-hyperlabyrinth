import pygame, sys, math
from settings import *
from systems.level_loader import load_levels, Level
from systems.pathfinding import AStarGrid
from systems.raycast import Raycaster
from entities.projectile import Projectile
from entities.explosion import Explosion
from ui import menu, hud, text

pygame.init(); screen=pygame.display.set_mode((WIDTH,HEIGHT)); pygame.display.set_caption('Rayfall - A* Edition'); clock=pygame.time.Clock()
levels=load_levels(); state='menu'; selected=0; level_idx=0
player=walls=enemies=pathfinder=None; projectiles=[]; explosions=[]; ammo=[12,4]; reload_timer=0; fire_cd=[0,0]

def start_level(idx):
    global level_idx,player,walls,enemies,pathfinder,projectiles,explosions,ammo,reload_timer,fire_cd
    level_idx=idx; player,walls,enemies=Level(levels[idx]).build(); pathfinder=AStarGrid(WORLD_W,WORLD_H,20,walls,12)
    projectiles=[];explosions=[];ammo=[12,4];reload_timer=0;fire_cd=[0,0]

def fire(big=False):
    global ammo
    slot=1 if big else 0
    if ammo[slot]<=0 or fire_cd[slot]>0 or reload_timer>0:return
    ammo[slot]-=1;fire_cd[slot]=.42 if big else .16
    projectiles.append(Projectile(player.x,player.y,player.angle,260 if big else 430,0 if big else 12,big))

running=True
while running:
    dt=min(clock.tick(FPS)/1000,.05)
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:running=False
        if state=='menu':
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_UP:selected=(selected-1)%len(levels)
                elif ev.key==pygame.K_DOWN:selected=(selected+1)%len(levels)
                elif ev.key==pygame.K_RETURN:start_level(selected);state='play'
                elif ev.key==pygame.K_ESCAPE:running=False
        elif state in ('dead','complete','victory'):
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_r and state=='dead':start_level(level_idx);state='play'
                elif ev.key==pygame.K_RETURN:
                    if state=='complete':
                        if level_idx+1<len(levels):start_level(level_idx+1);state='play'
                        else:state='victory'
                    elif state=='victory':state='menu'
                    else:state='menu'
                elif ev.key==pygame.K_ESCAPE:state='menu'
        else:
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_SPACE:player.dash()
                elif ev.key==pygame.K_1:fire(False)
                elif ev.key==pygame.K_2:fire(True)
                elif ev.key==pygame.K_r and reload_timer<=0:reload_timer=1.5
            if ev.type==pygame.MOUSEBUTTONDOWN:
                if ev.button==1:fire(False)
                elif ev.button==3:fire(True)
    if state=='menu':menu(screen,selected,levels);pygame.display.flip();continue
    if state=='play':
        player.update(dt,walls)
        for i in range(2):fire_cd[i]=max(0,fire_cd[i]-dt)
        if reload_timer>0:
            reload_timer-=dt
            if reload_timer<=0:ammo=[12,4]
        for e in enemies:e.update(dt,player,walls,pathfinder)
        for p in projectiles:
            effect=p.update(dt,walls,enemies)
            if effect: explosions.append(Explosion(effect[1],effect[2]))
        projectiles=[p for p in projectiles if p.alive]
        for x in explosions:x.update(dt,enemies,player,walls)
        explosions=[x for x in explosions if x.alive]
        if player.health<=0:state='dead'
        elif not any(e.alive for e in enemies):state='complete'
    screen.fill((10,10,16)); pygame.draw.rect(screen,(18,20,28),(0,0,VIEW_W,500));
    for w in walls:
        w.draw(screen)
    for e in enemies:
        e.draw(screen)
    for p in projectiles:
        p.draw(screen)
    for x in explosions:
        x.draw(screen)

    player.draw(screen)

    # Raycasting
    ray=Raycaster()
    ray.cast(player, walls)
    ray.draw_3d(screen)

    # Right side is the 3D view; redraw its floor/ceiling first would require separate surface, so overlay is intentionally simple.
    pygame.draw.rect(screen,(12,12,18),(500,0,500,500));ray.draw_3d(screen)
    for e in enemies:
        if e.alive:
            dx = e.x - player.x
            dy = e.y - player.y
            d = math.hypot(dx, dy)

            a = (math.atan2(dy,dx)-player.angle+math.pi)%(2*math.pi)-math.pi
            if abs(a)<FOV/2 and d>1 and (ray.dists[max(0,min(len(ray.dists)-1,int((a+FOV/2)/FOV*len(ray.dists))))] or 9999)>d:
                x = 500+(a/FOV+.5)*500;size=max(10,min(180,650/d))
                pygame.draw.circle(screen,RED,(int(x),300),int(size/2))
    hud(screen,level_idx,sum(e.alive for e in enemies),player,ammo,reload_timer>0)
    if state=='dead':
        pygame.draw.rect(screen,(80,0,0),(0,0,1000,600),width=0)
        text(screen,'YOU DIED',(500,240),60,WHITE)
        text(screen,'R: RESTART   ENTER: MENU',(500,330),24,WHITE)
    elif state=='complete':
        text(screen,'LEVEL CLEAR',(500,240),55,YELLOW)
        text(screen,'ENTER: NEXT LEVEL   ESC: MENU',(500,330),22,WHITE)
    pygame.display.flip()

pygame.quit()
sys.exit()
