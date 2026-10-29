"""A Code From Scratch mission. Compile, then play with Space."""
import asyncio
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 10
COIN_STORAGE_ID = 7
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'escape_room'
CONCEPT = 'nested-loops'
LOOP_COMMANDS = ('power_cell',)
COIN_NAMES = ('first', 'second')
COLLECTED_COINS = set()


def escape_room():
    # EDIT START
    pass
    # EDIT END


COIN_SPRITE = ['..oooo..', '.offffo.', 'offffffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offffffo', '.offffo.', '..oooo..']

def draw_coin(surface, coin, collected):
    colors = {'o': (174, 146, 98) if collected else (188, 132, 59), 'f': (255, 207, 100), 'h': (255, 242, 179)}
    for y, row in enumerate(COIN_SPRITE):
        for x, pixel in enumerate(row):
            if pixel in colors and (not collected or pixel == 'o'):
                surface.set_at((coin.x + x, coin.y + y), colors[pixel])

def remember(name):
    if name not in COLLECTED_COINS:
        COLLECTED_COINS.add(name)
        lesson_bridge.save_coins(COIN_STORAGE_ID, COLLECTED_COINS)

def label(surface, font, text, x, y, color=(91, 79, 119)):
    surface.blit(font.render(text, False, color), (x, y))

GIRL_SPRITE = ['...hhhh....', '..hhhhhh.pp', '.hhhhhhhhpp', '.hhsssshhh.', '.hssessesh.', '..ssssssh..', '...ssss....', '....ss.....', '..dddddd...', '.sdddddds..', '.sdddddds..', '.sdddddds..', '..dddddd...', '..dddddd...', '.dddddddd..', '...s..s....', '...s..s....', '...s..s....', '..bb..bb...', '.bbb..bbb..']

PALETTE = {'h': (88, 66, 99), 's': (255, 207, 173), 'e': (65, 56, 85), 'd': (237, 160, 185), 'p': (255, 223, 144), 'b': (101, 85, 121)}

def pixel_cloud(surface, x, y):
    for dx, dy, w, h in [(6, 0, 20, 4), (2, 4, 33, 5), (0, 9, 39, 5), (5, 14, 29, 3)]:
        pygame.draw.rect(surface, (255, 247, 242), (x + dx, y + dy, w, h))

def draw_girl(surface, x, y, moving):
    for row, line in enumerate(GIRL_SPRITE):
        for col, pixel in enumerate(line):
            if pixel in PALETTE:
                offset = int(pygame.time.get_ticks() / 110) % 2 if moving and row >= 15 else 0
                surface.set_at((round(x) - 5 + col, round(y) - 20 + row - offset), PALETTE[pixel])


class World:
    def __init__(self):
        self.program = self.generator = None
        self.elapsed = self.cooldown = 0.0
        self.actions = 0
        self.powered = set()
        self.unlocked = False
        self.message = 'Two rows of power cells. Charge them, unlock the latch, and escape.'
    def commands(self): return {'power_cell':self.power_cell,'unlock_exit':self.unlock_exit,'open_exit':self.open_exit}
    def sensors(self): return {'all_powered':self.all_powered}
    def power_cell(self,row,column): return ('power',row,column)
    def unlock_exit(self): return ('unlock',)
    def open_exit(self): return ('open',)
    def all_powered(self): return len(self.powered)==6
    def perform(self,command):
        if command[0]=='power':
            row,column=command[1:]
            if type(row) is not int or type(column) is not int or not (0<=row<2 and 0<=column<3):
                self.message='That cell is outside the panel. Check both loop counts.'
                return 'dead'
            self.powered.add((row,column))
            if all((0,col) in self.powered for col in range(3)): remember('first')
            if self.all_powered(): remember('second')
            self.message=f'Power cells: {len(self.powered)}/6.'
        elif command[0]=='unlock':
            if not self.all_powered():
                self.message='The latch needs all six power cells.'
                return 'dead'
            self.unlocked=True
            self.message='Latch unlocked. Your program can open the exit now.'
        elif command[0]=='open':
            if not self.unlocked:
                self.message='The latch is still locked. Check your sequence.'
                return 'dead'
            return 'won'
        return None

    def update(self, dt, action=False):
        self.elapsed += dt
        self.cooldown = max(0.0, self.cooldown - dt)
        if action and self.cooldown == 0:
            self.cooldown = 0.24
            return advance_program(self)
        return None

    def program_finished(self):
        self.message = "Add your solution to the green function, then Compile."
        return None



def draw_scene(surface,world,small,title):
    surface.fill((217,212,237))
    label(surface,title,'THE FINAL ESCAPE',89,21)
    pygame.draw.rect(surface,(201,194,218),(0,65,320,80))
    pygame.draw.rect(surface,(180,210,179),(0,145,320,6))
    pygame.draw.rect(surface,(231,199,186),(0,151,320,29))
    for row in range(2):
        for column in range(3):
            x,y=97+column*39,66+row*36
            pygame.draw.rect(surface,(169,211,178) if (row,column) in world.powered else (155,141,181),(x,y,27,27))
            pygame.draw.rect(surface,(211,234,199) if (row,column) in world.powered else (188,173,207),(x+5,y+4,17,18))
    pygame.draw.rect(surface,(148,133,171),(270,89,30,56))
    pygame.draw.rect(surface,(178,222,186) if world.unlocked else (218,185,210),(273,92,24,53))
    label(surface,small,'EXIT',275,78)
    label(surface,small,'UNLOCKED' if world.unlocked else 'LOCKED',262,155)
    draw_girl(surface,49,145,False)
    label(surface,small,world.message[:67],5,174)



def advance_program(world):
    if world.program is None:
        world.message = "Compile your program first."
        return None
    if world.generator is None:
        world.generator = world.program()
    try:
        command = next(world.generator)
    except StopIteration:
        world.generator = None
        return world.program_finished()
    world.actions += 1
    return world.perform(command)


async def main():
    lesson_bridge.emit('loading', phase=4, label='Starting your game', fraction=None, loaded=0, total=0)
    pygame.init()
    screen = pygame.display.set_mode((800, 450))
    surface = pygame.Surface((WIDTH, HEIGHT))
    small, title = pygame.font.Font(None, 10), pygame.font.Font(None, 16)
    clock = pygame.time.Clock()
    world = World()
    COLLECTED_COINS.update(name for name in lesson_bridge.load_coins(COIN_STORAGE_ID) if name in COIN_NAMES)
    state, attempt, has_input, previous_message = 'idle', 0, False, ''
    lesson_bridge.ready()
    while True:
        dt = min(clock.tick(60) / 1000, 0.04)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        command = lesson_bridge.poll()
        if command:
            try:
                candidate = World()
                candidate.program = lesson_bridge.compile_lesson(command['body'], PROGRAM_NAME,
                    candidate.commands(), candidate.sensors(), CONCEPT, LOOP_COMMANDS)
                world = candidate
                state, has_input, previous_message = 'playing', False, ''
                attempt += 1
                lesson_bridge.emit('started', attempt=attempt)
            except Exception as error:
                state = 'idle'
                lesson_bridge.emit('error', message=str(error))
        if state == 'playing':
            try:
                keys = pygame.key.get_pressed()
                action = bool(keys[pygame.K_SPACE])
                has_input = has_input or action
                result = world.update(dt, action)
                if world.message != previous_message:
                    previous_message = world.message
                    lesson_bridge.emit('notice', message=world.message)
                if result and (result != 'won' or has_input):
                    state = result
                    lesson_bridge.emit(result, seconds=round(world.elapsed, 1), coins=sorted(COLLECTED_COINS))
            except Exception as error:
                state = 'idle'
                lesson_bridge.emit('error', message=str(error))
        draw_scene(surface, world, small, title)
        pygame.transform.scale(surface, (800, 450), screen)
        pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())
