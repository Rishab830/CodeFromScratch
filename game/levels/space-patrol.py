"""Pilot the ship. Your Python controls when its auto-aimed weapon fires."""
import asyncio
import math
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 6
COIN_STORAGE_ID = 10
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'defend_sector'
CONCEPT = 'combat'
LOOP_COMMANDS = ('shoot',)
COIN_NAMES = ('wave-five', 'sector-clear')
COLLECTED_COINS = set()


def defend_sector():
    # EDIT START
    for bullet in range(30):
        shoot()
    # EDIT END


SHIP_SPRITE = ['....ppp....', '....ppp....', '...pwwwp...', '...pwwwp...', '..ppbbbpp..', '..ppbbbpp..', '.pppbbbppp.', 'ppppppppppp', 'pp.ppppp.pp', 'p...ppp...p']
ALIEN_SPRITE = ['..r...r..', '...r.r...', '..rrrrr..', '.rrerrerr', 'rrrrrrrrr', 'r.rrrrr.r', 'r.r...r.r', '..rr.rr..']
COIN_SPRITE = ['..oooo..', '.offffo.', 'offffffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offffffo', '.offffo.', '..oooo..']

def label(surface, font, text, x, y, color=(222, 214, 248)):
    surface.blit(font.render(text, False, color), (x, y))

def draw_coin(surface, coin, collected):
    colors = {'o': (174, 146, 98) if collected else (188, 132, 59), 'f': (255, 207, 100), 'h': (255, 242, 179)}
    for y, row in enumerate(COIN_SPRITE):
        for x, pixel in enumerate(row):
            if pixel in colors and (not collected or pixel == 'o'):
                surface.set_at((coin.x+x, coin.y+y), colors[pixel])

def remember(name):
    if name not in COLLECTED_COINS:
        COLLECTED_COINS.add(name)
        lesson_bridge.save_coins(COIN_STORAGE_ID, COLLECTED_COINS)


class World:
    def __init__(self, hostile_fire=True):
        self.program = self.generator = None
        self.elapsed = self.weapon_timer = 0.0
        self.actions = self.spawned = self.defeated = self.shots = self.wasted = 0
        self.ammo, self.shields = 30, 5
        self.x, self.y = 160.0, 143.0
        self.armed = self.cleared = self.finished = False
        self.enemy = None
        self.bullets, self.enemy_bullets, self.sparks = [], [], []
        self.spawn_timer = 0.8
        self.invulnerable = 0.0
        self.hostile_fire = hostile_fire
        self.message = 'Arrows / WASD fly. Space arms your weapon code once.'

    def commands(self): return {'shoot': self.shoot}
    def sensors(self): return {'enemy_visible': self.enemy_visible, 'bullets_left': self.bullets_left}
    def shoot(self): return 'shoot'
    def enemy_visible(self): return self.enemy is not None
    def bullets_left(self): return self.ammo

    def perform(self, command):
        if command != 'shoot' or self.ammo <= 0: return None
        self.ammo -= 1
        self.shots += 1
        target = self.enemy
        self.bullets.append({'x': self.x, 'y': self.y-7, 'target': target})
        if target is None:
            self.wasted += 1
            self.message = 'Empty space! That shot still used one bullet.'
        else:
            self.message = f'Target locked. Enemy needs {target["hp"]} more hits.'
        return None

    def program_finished(self):
        # The weapon checks the same routine again on the next weapon tick.
        return None

    def spawn_enemy(self):
        self.spawned += 1
        self.enemy = {'x': float(55+(self.spawned*67)%210), 'y': 45.0,
                      'hp': 3, 'fire': 0.3, 'direction': 1 if self.spawned%2 else -1}
        self.message = f'Enemy {self.spawned}/10 detected. Three hits needed.'

    def hit_enemy(self):
        self.enemy['hp'] -= 1
        self.sparks.append([self.enemy['x'], self.enemy['y'], 0.18])
        if self.enemy['hp'] == 0:
            self.defeated += 1
            self.enemy = None
            self.spawn_timer = 0.8
            if self.defeated == 5: remember('wave-five')
            if self.defeated == 10:
                self.cleared = True
                self.enemy_bullets.clear()
                remember('sector-clear')
                self.message = 'Sector clear! Fly to the green exit beacon at the top.'
            else:
                self.message = 'Wave clear. No enemy detected. Watch your ammunition!'

    def update(self, dt, action=False, left=False, right=False, up=False, down=False):
        if self.finished: return None
        self.elapsed += dt
        dx,dy = int(right)-int(left),int(down)-int(up)
        speed = 88 / (math.sqrt(2) if dx and dy else 1)
        self.x = max(12.0, min(308.0, self.x+dx*speed*dt))
        self.y = max(32.0, min(155.0, self.y+dy*speed*dt))
        self.invulnerable = max(0.0, self.invulnerable-dt)
        self.sparks = [[x,y,life-dt] for x,y,life in self.sparks if life>dt]
        if self.cleared:
            if math.hypot(self.x-160,self.y-40) < 13:
                self.finished = True
                return 'won'
            return None
        if action and not self.armed:
            self.armed = True
            self.message = 'Weapon armed. Your code is running. Keep flying!'
        if not self.armed: return None

        if self.enemy is None:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0 and self.spawned < 10: self.spawn_enemy()
        else:
            enemy = self.enemy
            enemy['x'] += enemy['direction']*18*dt
            if enemy['x'] < 30 or enemy['x'] > 290: enemy['direction'] *= -1
            enemy['y'] = 45+5*math.sin(self.elapsed*2)
            enemy['fire'] -= dt
            if self.hostile_fire and enemy['fire'] <= 0:
                length = max(1,math.hypot(self.x-enemy['x'],self.y-enemy['y']))
                self.enemy_bullets.append([enemy['x'],enemy['y'],
                    (self.x-enemy['x'])/length*48,(self.y-enemy['y'])/length*48])
                enemy['fire'] = 0.75

        # A shot in flight finishes before the next shot. Auto-aim never spends
        # a fourth bullet on an enemy whose third hit is already on its way.
        for bullet in list(self.bullets):
            target = bullet['target']
            if target is not None:
                dx,dy = target['x']-bullet['x'],target['y']-bullet['y']
                distance = math.hypot(dx,dy)
                if distance <= 360*dt+4:
                    self.bullets.remove(bullet)
                    self.hit_enemy()
                    continue
                bullet['x'] += dx/distance*360*dt
                bullet['y'] += dy/distance*360*dt
            else:
                bullet['y'] -= 360*dt
                if bullet['y'] < 22: self.bullets.remove(bullet)

        if self.cleared: return None
        for bullet in list(self.enemy_bullets):
            previous_x,previous_y = bullet[0],bullet[1]
            bullet[0] += bullet[2]*dt
            bullet[1] += bullet[3]*dt
            # Swept segment distance catches hits even if the frame is slow.
            bx,by = bullet[0]-previous_x,bullet[1]-previous_y
            segment = bx*bx+by*by
            t = max(0,min(1,((self.x-previous_x)*bx+(self.y-previous_y)*by)/segment)) if segment else 0
            hit = math.hypot(self.x-(previous_x+t*bx),self.y-(previous_y+t*by)) < 7
            if hit:
                self.enemy_bullets.remove(bullet)
                if self.invulnerable == 0:
                    self.shields -= 1
                    self.invulnerable = 0.8
                    self.message = 'Shield hit! Keep moving to dodge incoming fire.'
                    if self.shields == 0:
                        self.finished = True
                        return 'dead'
            elif not (-10<bullet[0]<330 and 20<bullet[1]<170):
                self.enemy_bullets.remove(bullet)

        if self.ammo == 0 and not self.bullets:
            self.message = 'Out of bullets before clearing ten enemies. Check when you shoot.'
            self.finished = True
            return 'dead'
        self.weapon_timer = max(0.0,self.weapon_timer-dt)
        if self.weapon_timer == 0 and not self.bullets:
            self.weapon_timer = 0.12
            return advance_program(self)
        return None


def draw_sprite(surface, sprite, x, y, palette):
    for row,line in enumerate(sprite):
        for col,pixel in enumerate(line):
            if pixel in palette: surface.set_at((round(x)+col,round(y)+row),palette[pixel])

def draw_scene(surface,world,small,title):
    surface.fill((33,30,56))
    for index in range(48):
        x = (index*73+19)%320
        y = 25+(index*37+int(world.elapsed*(3+index%3)))%136
        surface.set_at((x,y),(112,103,147) if index%3 else (191,180,220))
    pygame.draw.rect(surface,(54,46,80),(0,0,320,23))
    label(surface,small,f'AMMO {world.ammo:02}/30',8,7,(252,218,147))
    label(surface,small,f'ENEMIES {world.defeated:02}/10',83,7,(192,224,196))
    label(surface,small,f'SHIELDS {world.shields}',175,7,(184,211,245))
    for index,name in enumerate(COIN_NAMES): draw_coin(surface,pygame.Rect(286+index*13,5,8,10),name in COLLECTED_COINS)
    if world.cleared:
        pygame.draw.rect(surface,(143,203,168),(146,28,28,24),1)
        pygame.draw.rect(surface,(183,226,187),(151,33,18,14),1)
        label(surface,small,'EXIT',151,19,(183,226,187))
    elif not world.armed:
        label(surface,title,'SPACE PATROL',112,62)
        label(surface,small,'30 BULLETS. 10 ENEMIES. MAKE EVERY SHOT COUNT.',57,80)
        label(surface,small,'SPACE ARMS THE WEAPON / ARROWS OR WASD FLY',57,92)
    elif world.enemy is None:
        label(surface,small,'NO ENEMY DETECTED',120,45,(153,145,179))
    if world.enemy is not None:
        enemy = world.enemy
        draw_sprite(surface,ALIEN_SPRITE,enemy['x']-4,enemy['y']-4,
                    {'r':(239,173,194),'e':(78,62,109)})
        for i in range(3):
            pygame.draw.rect(surface,(246,207,156) if i<enemy['hp'] else (81,67,102),
                             (round(enemy['x'])-6+i*5,round(enemy['y'])-11,3,2))
    for bullet in world.bullets:
        pygame.draw.rect(surface,(177,231,213),(round(bullet['x'])-1,round(bullet['y'])-3,3,6))
    for x,y,vx,vy in world.enemy_bullets:
        pygame.draw.rect(surface,(248,176,154),(round(x)-1,round(y)-1,3,3))
    for x,y,life in world.sparks:
        radius = round((0.18-life)*38)+2
        for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
            pygame.draw.rect(surface,(252,218,147),(round(x)+dx*radius,round(y)+dy*radius,2,2))
    if world.invulnerable == 0 or int(world.elapsed*12)%2 == 0:
        draw_sprite(surface,SHIP_SPRITE,world.x-5,world.y-5,
                    {'p':(184,166,236),'w':(243,235,255),'b':(153,215,229)})
        pygame.draw.rect(surface,(255,208,148),(round(world.x)-1,round(world.y)+5,3,2+int(world.elapsed*12)%3))
    pygame.draw.rect(surface,(45,38,65),(0,162,320,18))
    label(surface,small,world.message[:72],5,170)
    label(surface,small,'TARGET: '+('YES' if world.enemy_visible() else 'NO'),7,153,(165,180,194))


def advance_program(world):
    if world.program is None: return None
    if world.generator is None: world.generator = world.program()
    try:
        command = next(world.generator)
    except StopIteration:
        world.generator = None
        return world.program_finished()
    if command is not None:
        world.actions += 1
        return world.perform(command)
    return None


async def main():
    lesson_bridge.emit('loading',phase=4,label='Starting your game',fraction=None,loaded=0,total=0)
    pygame.init()
    screen=pygame.display.set_mode((800,450))
    surface=pygame.Surface((WIDTH,HEIGHT))
    small,title=pygame.font.Font(None,10),pygame.font.Font(None,16)
    clock=pygame.time.Clock()
    world=World()
    COLLECTED_COINS.update(name for name in lesson_bridge.load_coins(COIN_STORAGE_ID) if name in COIN_NAMES)
    state,attempt,has_input,previous_message='idle',0,False,''
    lesson_bridge.ready()
    while True:
        dt=min(clock.tick(60)/1000,0.04)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: return
        command=lesson_bridge.poll()
        if command:
            try:
                candidate=World()
                candidate.program=lesson_bridge.compile_lesson(command['body'],PROGRAM_NAME,
                    candidate.commands(),candidate.sensors(),CONCEPT,LOOP_COMMANDS)
                world=candidate
                state,has_input,previous_message='playing',False,''
                attempt+=1
                lesson_bridge.emit('started',attempt=attempt)
            except Exception as error:
                state='idle';lesson_bridge.emit('error',message=str(error))
        if state=='playing':
            try:
                keys=pygame.key.get_pressed()
                action=bool(keys[pygame.K_SPACE])
                left=bool(keys[pygame.K_LEFT] or keys[pygame.K_a])
                right=bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])
                up=bool(keys[pygame.K_UP] or keys[pygame.K_w])
                down=bool(keys[pygame.K_DOWN] or keys[pygame.K_s])
                has_input=has_input or action or left or right or up or down
                result=world.update(dt,action,left,right,up,down)
                if world.message!=previous_message:
                    previous_message=world.message;lesson_bridge.emit('notice',message=world.message)
                if result and (result!='won' or has_input):
                    state=result
                    lesson_bridge.emit(result,seconds=round(world.elapsed,1),coins=sorted(COLLECTED_COINS))
            except Exception as error:
                state='idle';lesson_bridge.emit('error',message=str(error))
        draw_scene(surface,world,small,title)
        pygame.transform.scale(surface,(800,450),screen)
        pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())
