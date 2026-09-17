import pygame, sys, math
from settings import *
from systems.level_loader import load_levels, Level
from systems.pathfinding import AStarGrid
from systems.raycast import Raycaster
from entities.projectile import Projectile
from entities.explosion import Explosion
from entities.shrapnel import Shrapnel
from ui import menu, hud, text, viewmodel

pygame.init(); screen=pygame.display.set_mode((WIDTH,HEIGHT),pygame.RESIZABLE); pygame.display.set_caption('Rayfall - A* Edition'); clock=pygame.time.Clock()
levels=load_levels(); state='menu'; selected=0; level_idx=0
coins=0
player=walls=enemies=pathfinder=None; projectiles=[]; explosions=[]; shrapnel=[]
ammo = [12, 4]
reload_timer = 0
reload_duration = 1.5

fire_cd = [0, 0]
selected_weapon = 0
viewmodel_phase = 0

def start_level(idx):
    global level_idx,player,walls,enemies,pathfinder,projectiles,explosions,shrapnel,ammo,reload_timer,fire_cd
    level_idx=idx; player,walls,enemies=Level(levels[idx]).build(); pathfinder=AStarGrid(WORLD_W,WORLD_H,20,walls,12)
    projectiles=[];explosions=[];shrapnel=[];ammo=[12,4];reload_timer=0;fire_cd=[0,0]

def has_ammo(slot):
    global ammo
    return ammo[slot] > 0

def fire(slot): # eventually put ammo as property of player class
    global ammo
    if slot == "dash":
        for number, bullet in enumerate(ammo):
            ammo[number] = math.floor(bullet * 0.5)
        return
    if ammo[slot]<=0 or fire_cd[slot]>0 or reload_timer>0:return
    ammo[slot] -= 1
    fire_cd[slot]=.42 if slot else .16
    projectiles.append(Projectile(player.x,player.y,player.angle,260 if slot else 430,0 if slot else 12,slot!=0))

running=True
while running:
    dt=min(clock.tick(FPS)/1000,.05)
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:running=False
        elif ev.type==pygame.VIDEORESIZE:
            # Keep the raytraced view full-window while allowing user resizing.
            screen=pygame.display.set_mode((max(MIN_WINDOW_WIDTH,ev.w),max(MIN_WINDOW_HEIGHT,ev.h)),pygame.RESIZABLE)
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
                if ev.key==pygame.K_SPACE and has_ammo(0) and has_ammo(1):
                    player.dash()
                    fire("dash")
                # Number keys select a weapon; firing is always left mouse button.
                elif ev.key==pygame.K_1: selected_weapon=0
                elif ev.key==pygame.K_2:selected_weapon=1
                elif ev.key == pygame.K_r and reload_timer <= 0:
                    reload_timer = reload_duration
            if ev.type==pygame.MOUSEBUTTONDOWN:
                if ev.button==1:fire(selected_weapon)
    if state=='menu':menu(screen,selected,levels);pygame.display.flip();continue
    if state=='play':
        player.update(dt,walls, enemies)
        # Advance the first-person rectangle bob only while the player moves or dashes.
        if abs(player.speed) > 0 or player.dash_left > 0: 
            viewmodel_phase += dt * 9
        for i in range(2):
            fire_cd[i]=max(0,fire_cd[i]-dt)
        if reload_timer > 0:
            reload_timer -= dt

            if reload_timer <= 0:
                reload_timer = 0
                ammo = [12, 4]
        for e in enemies:
            if e.update(dt,player,walls,pathfinder,enemies) == 1:
                coins += e.coins
                enemies.remove(e)
        for p in projectiles:
            effect=p.update(dt,walls,enemies)
            if effect:
                if effect[0]=='explosion':
                    explosions.append(Explosion(effect[1],effect[2]))
                elif effect[0]=='shrapnel':
                    for i in range(10):
                        a=math.tau*i/10+__import__('random').uniform(-.45,.45)
                        shrapnel.append(Shrapnel(effect[1],effect[2],a))
        projectiles=[p for p in projectiles if p.alive]
        for piece in shrapnel:piece.update(dt,walls,enemies)
        shrapnel=[piece for piece in shrapnel if piece.alive]
        for x in explosions:x.update(dt,enemies,player,walls)
        explosions=[x for x in explosions if x.alive]
        if player.health<=0:state='dead'
        elif not any(e.alive for e in enemies):state='complete'
    screen.fill((10,10,16))
    # The former left-hand top-down map is intentionally omitted: raytracing fills the window.
    ray=Raycaster();ray.cast(player,walls);ray.draw_3d(screen)
    _, view_height = screen.get_size()
    # 3D view: render enemies, projectiles, shrapnel and explosions as perspective sprites.
    for e in enemies:
        if not e.alive: continue
        proj=ray.project(player,e.pos,e.radius,1.0)
        if proj:
            x,d,size=proj
            if d <= ray.wall_depth_at(x)+max(2,size*0.015):
                r=max(2,int(size/2))
                pygame.draw.circle(screen,RED,(int(x),view_height//2),r)
                # simple highlight makes the sphere read as 3D
                pygame.draw.circle(screen,(255,150,150),(int(x-r*.35),int(view_height/2-r*.35)),max(1,int(r*.22)))
                bar=max(8,int(size*.9))
                pygame.draw.rect(screen,(60,0,0),(int(x-bar/2),view_height//2-r-8,bar,4))
                pygame.draw.rect(screen,GREEN,(int(x-bar/2),view_height//2-r-8,int(bar*e.health/e.max_health),4))

    for p in projectiles:
        if not p.alive: continue
        proj=ray.project(player,p.pos,p.radius,0.55)
        if proj:
            x,d,size=proj
            if d <= ray.wall_depth_at(x)+2:
                r=max(2,int(size/2))
                pygame.draw.circle(screen,ORANGE,(int(x),view_height//2),r)
                pygame.draw.circle(screen,YELLOW,(int(x-r*.25),int(view_height/2-r*.25)),max(1,int(r*.35)))

    for piece in shrapnel:
        if not piece.alive: continue
        proj=ray.project(player,piece.pos,4,0.6)
        if proj:
            x,d,size=proj
            if d <= ray.wall_depth_at(x)+2:
                r=max(1,int(size/2))
                pygame.draw.circle(screen,YELLOW,(int(x),view_height//2),r)

    for xpl in explosions:
        if not xpl.alive: continue
        proj=ray.project(player,(xpl.x,xpl.y),xpl.radius,1.0)
        if proj:
            x,d,size=proj
            if d <= ray.wall_depth_at(x)+2:
                r=max(2,int(size/2))
                pygame.draw.circle(screen,ORANGE,(int(x),view_height//2),r, max(2,int(r*.10)))
                pygame.draw.circle(screen,YELLOW,(int(x),view_height//2),max(1,int(r*.55)),max(1,int(r*.06)))

        # Normal walking/dashing bob
    bob = (
        math.sin(viewmodel_phase) * 12
        if state == 'play' and (abs(player.speed) > 0 or player.dash_left > 0)
        else 0
    )

    # Reload animation
    if reload_timer > 0:
        # 0 -> 1 as reload progresses
        progress = 1.0 - (reload_timer / reload_duration)

        # One smooth reload movement
        bob = math.sin(progress * math.pi) * 25

    viewmodel(screen, bob, weapon=selected_weapon)
    hud(screen,level_idx,sum(e.alive for e in enemies),player,ammo,reload_timer>0,selected_weapon,coins)
    view_width, view_height = screen.get_size()
    if state=='dead':
        pygame.draw.rect(screen,(80,0,0),(0,0,view_width,view_height),width=0)
        text(screen,'YOU DIED',(view_width/2,view_height*.4),60,WHITE)
        text(screen,'R: RESTART   ENTER: MENU',(view_width/2,view_height*.55),24,WHITE)
        coins = 0
    elif state=='complete':
        text(screen,'LEVEL CLEAR',(view_width/2,view_height*.4),55,YELLOW)
        text(screen,'ENTER: NEXT LEVEL   ESC: MENU',(view_width/2,view_height*.55),22,WHITE)
    pygame.display.flip()

pygame.quit();sys.exit()
