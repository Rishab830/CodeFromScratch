"""Drive an RC car outside. Its while-loop program takes over without signal."""
import asyncio
import math
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 8
COIN_STORAGE_ID = 11
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'escape'
CONCEPT = 'while'
LOOP_COMMANDS = ('move_forward',)
ANIMATED_SENSORS = ('exit_detected',)
COIN_NAMES = ('tunnel-1', 'tunnel-2', 'tunnel-3')
COLLECTED_COINS = set()
ENTRY_X, STEP_SIZE, DRIVE_SPEED = 104, 18, 48
SCAN_SECONDS, OPEN_SECONDS = 0.4, 0.7
IDLE_SECONDS = 5.0


def escape():
    # EDIT START
    pass
    # EDIT END


GIRL_SPRITE = ['...hhhh....', '..hhhhhh.pp', '.hhhhhhhhpp', '.hhsssshhh.', '.hssessesh.', '..ssssssh..', '...ssss....', '....ss.....', '..dddddd...', '.sdddddds..', '.sdddddds..', '.sdddddds..', '..dddddd...', '..dddddd...', '.dddddddd..', '...s..s....', '...s..s....', '...s..s....', '..bb..bb...', '.bbb..bbb..']
PALETTE = {'h': (88,66,99), 's': (255,207,173), 'e': (65,56,85), 'd': (237,160,185), 'p': (255,223,144), 'b': (101,85,121)}
COIN_SPRITE = ['..oooo..', '.offffo.', 'offffffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offffffo', '.offffo.', '..oooo..']

def label(surface, font, text, x, y, color=(216,207,235)):
    surface.blit(font.render(text,False,color),(x,y))

def draw_coin(surface, coin, collected):
    colors = {'o': (174,146,98) if collected else (188,132,59), 'f': (255,207,100), 'h': (255,242,179)}
    for y,row in enumerate(COIN_SPRITE):
        for x,pixel in enumerate(row):
            if pixel in colors and (not collected or pixel=='o'):
                surface.set_at((coin.x+x,coin.y+y),colors[pixel])

def remember(name):
    if name not in COLLECTED_COINS:
        COLLECTED_COINS.add(name)
        lesson_bridge.save_coins(COIN_STORAGE_ID,COLLECTED_COINS)


class World:
    def __init__(self,lengths=None):
        self.program = self.generator = None
        self.elapsed = self.cooldown = 0.0
        self.actions = self.round = self.scans = 0
        self.lengths = lengths or random.sample(range(4,10),3)
        self.error = ''
        self.reset_tunnel()

    def reset_tunnel(self):
        self.position = self.open_attempts = 0
        self.car_x = 64.0
        self.phase = 'outside'
        self.phase_time = self.door_lift = 0.0
        self.door_open = self.scan_result = self.moving = False
        self.generator = None
        self.cooldown = 0.0
        self.length = self.lengths[min(self.round,2)]
        self.exit_x = ENTRY_X+self.length*STEP_SIZE
        self.door_x = self.exit_x+12
        self.message = f'Tunnel {self.round+1}/3. Signal connected. Drive right to enter.'

    def commands(self): return {'move_forward':self.move_forward,'open_exit':self.open_exit}
    def sensors(self): return {'exit_detected':self.exit_detected}
    def move_forward(self): return 'move'
    def open_exit(self):
        if self.open_attempts >= 1:
            raise ValueError('open exit can only be attempted once')
        self.open_attempts = 1
        return 'open'
    def exit_detected(self): return self.position == self.length
    def has_signal(self): return self.phase in ('outside','between','complete')

    def perform(self,command):
        self.phase_time = 0.0
        if command == ('sensor','exit_detected'):
            self.scans += 1
            self.scan_result = self.exit_detected()
            self.phase = 'scan'
            self.message = 'Checking for an exit...'
        elif command == 'move':
            self.phase = 'drive'
            self.drive_target = self.car_x+STEP_SIZE
            self.will_crash = self.position >= self.length and not self.door_open
            if self.will_crash: self.drive_target = self.door_x-9
            self.message = 'No signal. Onboard code is driving the RC car.'
        elif command == 'open':
            self.phase = 'open'
            self.open_here = self.exit_detected()
            self.message = 'Opening the exit... (one attempt used)' if self.open_here else 'Trying to open... no exit here. One attempt used.'
        return None

    def program_finished(self):
        if self.door_open and self.position >= self.length:
            self.phase = 'exit'
            self.exit_target = max(self.car_x,self.door_x+27)
            self.message = 'Exit open! The car is driving out to restore its signal.'
            return None
        self.phase, self.phase_time = 'waiting', 0.0
        self.message = 'NO SIGNAL. Car idle. Waiting for onboard actions...'
        return None

    def update(self,dt,action=False,left=False,right=False):
        self.elapsed += dt
        self.moving = False
        self.phase_time += dt
        if self.phase in ('failed','complete','error'): return None
        if self.phase == 'waiting':
            if self.phase_time >= IDLE_SECONDS:
                self.phase = 'failed'
                self.message = 'No onboard action for five seconds. Check your while loop.'
                return 'dead'
            return None
        if self.phase == 'outside':
            direction = int(right)-int(left)
            self.car_x = max(56.0,min(ENTRY_X,self.car_x+direction*65*dt))
            self.moving = direction != 0
            if self.car_x >= ENTRY_X:
                self.phase = 'run'
                self.cooldown = 0.2
                self.message = 'NO SIGNAL. Remote disconnected. Onboard program starting...'
            return None
        if self.phase == 'scan':
            if self.phase_time >= SCAN_SECONDS:
                self.message = 'Exit detected: YES. The gate is within reach.' if self.scan_result else 'Exit detected: NO. Keep checking as the car moves.'
                self.phase,self.cooldown = 'run',0.12
            return None
        if self.phase == 'drive':
            self.moving = True
            self.car_x = min(self.drive_target,self.car_x+DRIVE_SPEED*dt)
            if self.car_x >= self.drive_target:
                if self.will_crash:
                    self.phase = 'failed'
                    self.message = 'The car hit the locked gate. Stop moving when the exit is detected.'
                    return 'dead'
                self.position += 1
                if self.position == self.length-1: remember(f'tunnel-{self.round+1}')
                self.phase,self.cooldown = 'run',0.08
            return None
        if self.phase == 'open':
            if self.open_here: self.door_lift = min(1.0,self.phase_time/OPEN_SECONDS)
            if self.phase_time >= OPEN_SECONDS:
                self.door_open = self.open_here
                self.phase,self.cooldown = 'run',0.12
            return None
        if self.phase == 'exit':
            self.moving = True
            self.car_x = min(self.exit_target,self.car_x+64*dt)
            if self.car_x >= self.exit_target:
                self.phase,self.phase_time = 'between',0.0
                self.message = 'Signal restored! Tunnel cleared.'
            return None
        if self.phase == 'between':
            if self.phase_time >= 0.7:
                self.round += 1
                if self.round == 3:
                    self.phase = 'complete'
                    return 'won'
                self.reset_tunnel()
            return None
        # Inside the tunnel, the onboard program advances on its own clock.
        self.cooldown = max(0.0,self.cooldown-dt)
        if self.cooldown == 0:
            return advance_program(self)
        return None


def draw_girl_and_remote(surface,world):
    for y,row in enumerate(GIRL_SPRITE):
        for x,pixel in enumerate(row):
            if pixel in PALETTE: surface.set_at((26+x,131+y),PALETTE[pixel])
    pygame.draw.line(surface,(255,207,173),(34,139),(43,138),2)
    pygame.draw.rect(surface,(89,77,117),(41,134,13,9))
    pygame.draw.rect(surface,(188,169,224),(42,135,11,7))
    pygame.draw.circle(surface,(73,66,98),(45,138),1)
    pygame.draw.circle(surface,(73,66,98),(50,138),1)
    pygame.draw.line(surface,(104,92,132),(51,134),(53,122),1)
    pygame.draw.circle(surface,(193,175,225),(53,121),1)
    phase = (world.elapsed*1.5)%1
    radius = 4+round(phase*15)
    color = (166,214,179) if world.has_signal() else (227,148,174)
    pygame.draw.arc(surface,color,(53-radius,121-radius,radius*2,radius*2),0.25,2.9,1)
    if not world.has_signal():
        pygame.draw.line(surface,(235,151,176),(48,114),(58,119),1)
        pygame.draw.line(surface,(235,151,176),(48,119),(58,114),1)

def draw_scene(surface,world,small,title):
    surface.fill((61,55,86))
    label(surface,title,'THE FOGGY TUNNEL',77,8)
    label(surface,small,f'{min(world.round+1,3)}/3',10,11)
    for index,name in enumerate(COIN_NAMES): draw_coin(surface,pygame.Rect(274+index*13,7,8,10),name in COLLECTED_COINS)
    for x,y in ((12,43),(46,32),(288,37),(306,61)):
        pygame.draw.rect(surface,(122,108,153),(x,y,2,2))
    pygame.draw.rect(surface,(164,183,169),(0,151,320,5))
    pygame.draw.rect(surface,(133,124,154),(0,156,320,9))
    for x in range(8,320,20): pygame.draw.rect(surface,(196,181,197),(x,159,9,2))
    tunnel_right = world.door_x+12
    # Draw the interior first; its wall becomes translucent after entry.
    pygame.draw.rect(surface,(44,40,64),(92,91,tunnel_right-92,60))
    for x in range(104,tunnel_right,18):
        pygame.draw.rect(surface,(105,92,130),(x,146,12,4))
        pygame.draw.line(surface,(70,60,91),(x,97),(x,145),1)
    coin_x = ENTRY_X+(world.length-1)*STEP_SIZE
    draw_coin(surface,pygame.Rect(coin_x-4,125,8,10),f'tunnel-{min(world.round+1,3)}' in COLLECTED_COINS)
    pygame.draw.rect(surface,(156,183,169),(world.door_x-3,111,9,40),1)
    door_height = round(37*(1-world.door_lift))
    if door_height:
        pygame.draw.rect(surface,(161,200,180),(world.door_x-1,113,5,door_height))
        for y in range(116,113+door_height,6): pygame.draw.line(surface,(113,151,142),(world.door_x,y),(world.door_x+3,y),1)
    pygame.draw.rect(surface,(216,217,181),(world.door_x-5,107,14,3))
    x = round(world.car_x)
    pygame.draw.rect(surface,(154,199,224),(x-9,139,19,8))
    pygame.draw.rect(surface,(190,222,231),(x-4,135,9,5))
    pygame.draw.rect(surface,(99,132,172),(x+1,136,3,3))
    pygame.draw.rect(surface,(248,218,157),(x+9,142,2,3))
    for wheel in (x-6,x+6):
        pygame.draw.rect(surface,(54,49,71),(wheel-2,146,5,5))
        spin = int(world.car_x/2)%2 if world.moving else 0
        pygame.draw.rect(surface,(185,171,199),(wheel-1+spin,148,2,1))
    if world.phase == 'scan':
        t = min(1,world.phase_time/SCAN_SECONDS)
        radius = 6+round(t*25)
        color = (176,224,204) if world.scan_result else (241,203,152)
        pygame.draw.arc(surface,color,(x+10-radius,133-radius,radius*2,radius*2),-0.7,0.7,1)
        if t>0.5: label(surface,small,'YES' if world.scan_result else 'NO',x-5,119,color)
    if world.phase == 'open' and not world.open_here:
        pygame.draw.line(surface,(238,158,174),(x+13,126),(x+21,134),1)
        pygame.draw.line(surface,(238,158,174),(x+13,134),(x+21,126),1)
    entered = world.phase != 'outside'
    wall = pygame.Surface((tunnel_right-92,64),pygame.SRCALPHA)
    wall.fill((112,101,142,65 if entered else 255))
    for block in range(0,wall.get_width(),24):
        pygame.draw.line(wall,(168,151,188,60 if entered else 255),(block,0),(block,64),1)
    surface.blit(wall,(92,87))
    pygame.draw.rect(surface,(147,132,170),(88,84,tunnel_right-84,7))
    pygame.draw.rect(surface,(147,132,170),(88,88,5,63))
    pygame.draw.rect(surface,(147,132,170),(tunnel_right,88,5,63))
    label(surface,small,'TUNNEL',97,76,(196,181,221))
    draw_girl_and_remote(surface,world)
    color = (171,218,185) if world.has_signal() else (245,166,188)
    label(surface,title,'SIGNAL OK' if world.has_signal() else 'NO SIGNAL',12,53,color)
    label(surface,small,'REMOTE' if world.has_signal() else 'ONBOARD CODE',13,69,color)
    label(surface,small,f'OPEN EXIT: {min(world.open_attempts,1)}/1',188,29,(218,205,231))
    if world.phase == 'scan': label(surface,small,'CHECKING EXIT...',101,37,(222,213,175))
    elif world.phase == 'open': label(surface,small,'OPENING EXIT...' if world.open_here else 'NO EXIT HERE',101,37,(222,213,175))
    elif world.phase == 'waiting': label(surface,small,'WAITING FOR CODE...',101,37,(222,213,175))
    if world.error:
        label(surface,small,world.error[:48].upper(),95,63,(244,174,191))
    pygame.draw.rect(surface,(48,42,69),(0,166,320,14))
    label(surface,small,world.message[:72],5,172)


def advance_program(world):
    if world.program is None: return world.program_finished()
    if world.generator is None: world.generator = world.program()
    try:
        command = next(world.generator)
    except StopIteration:
        world.generator = None
        return world.program_finished()
    if command != ('sensor','exit_detected'): world.actions += 1
    return world.perform(command)


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
                    candidate.commands(),candidate.sensors(),CONCEPT,LOOP_COMMANDS,ANIMATED_SENSORS)
                world=candidate
                state,has_input,previous_message='playing',False,''
                attempt+=1
                lesson_bridge.emit('started',attempt=attempt)
            except Exception as error:
                state='idle';lesson_bridge.emit('error',message=str(error))
        if state=='playing':
            try:
                keys=pygame.key.get_pressed()
                left=bool(keys[pygame.K_LEFT] or keys[pygame.K_a])
                right=bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])
                has_input=has_input or left or right
                result=world.update(dt,left=left,right=right)
                if world.message!=previous_message:
                    previous_message=world.message;lesson_bridge.emit('notice',message=world.message)
                if result and (result!='won' or has_input):
                    state=result
                    lesson_bridge.emit(result,seconds=round(world.elapsed,1),coins=sorted(COLLECTED_COINS))
            except Exception as error:
                world.error=str(error);world.message=world.error;world.phase='error'
                state='idle';lesson_bridge.emit('error',message=str(error))
        draw_scene(surface,world,small,title)
        pygame.transform.scale(surface,(800,450),screen)
        pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())
