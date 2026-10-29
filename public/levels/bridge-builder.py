"""A Code From Scratch mission. Compile, then play with Space."""
import asyncio
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 3
COIN_STORAGE_ID = 9
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'build_bridge'
CONCEPT = 'for'
LOOP_COMMANDS = ('place_plank',)
COIN_NAMES = ('first', 'second')
COLLECTED_COINS = set()


def build_bridge():
    # EDIT START
    for plank in range(2):
        place_plank()
    cross_bridge()
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
        self.actions = self.planks = 0
        self.x = 66.0
        self.crossing = False
        self.message = 'Count the missing bridge spaces. Press Space to step your loop.'
    def commands(self): return {'place_plank': self.place_plank, 'cross_bridge': self.cross_bridge}
    def sensors(self): return {}
    def place_plank(self): return 'plank'
    def cross_bridge(self): return 'cross'
    def perform(self, command):
        if command == 'plank':
            self.planks += 1
            if self.planks > 3:
                self.message = 'Too many planks. The bridge has three spaces.'
                return 'dead'
            self.message = f'Bridge: {self.planks} / 3 planks. Keep stepping.'
        elif command == 'cross':
            if self.planks != 3:
                self.message = 'The bridge is incomplete. Check how many times the loop repeats.'
                return 'dead'
            self.crossing = True
            self.message = 'Bridge complete. Walking to the flag!'
        return None
    def update(self, dt, action=False):
        self.elapsed += dt
        if self.crossing:
            self.x = min(280, self.x + 80*dt)
            if self.x > 170: remember('first')
            if self.x > 246: remember('second')
            return 'won' if self.x >= 280 else None
        self.cooldown = max(0.0, self.cooldown-dt)
        if action and self.cooldown == 0:
            self.cooldown = 0.24
            return advance_program(self)
        return None
    def program_finished(self):
        self.message = 'Use place_plank() in your loop, then cross_bridge().'
        return None



def draw_scene(surface, world, small, title):
    surface.fill((218, 220, 244))
    pixel_cloud(surface, 24, 30)
    pixel_cloud(surface, 203, 24)
    pygame.draw.rect(surface, (150, 188, 207), (0, 146, 320, 34))
    for left, width in [(0, 108), (174, 146)]:
        pygame.draw.rect(surface, (177, 211, 174), (left, 141, width, 7))
        pygame.draw.rect(surface, (232, 193, 180), (left, 148, width, 32))
    for index in range(3):
        rect = pygame.Rect(108+index*22, 140, 22, 7)
        pygame.draw.rect(surface, (224, 185, 147) if world.planks > index else (125, 153, 184), rect, 0 if world.planks > index else 1)
    label(surface, title, 'THREE SPACES. ONE BRIDGE.', 56, 67)
    for x, name in [(170, 'first'), (246, 'second')]: draw_coin(surface, pygame.Rect(x, 125, 8, 10), name in COLLECTED_COINS)
    pygame.draw.rect(surface, (111, 143, 131), (281, 106, 2, 35))
    pygame.draw.rect(surface, (181, 224, 177), (283, 107, 17, 10))
    draw_girl(surface, world.x, 141, world.crossing)
    label(surface, small, world.message[:68], 5, 172)



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
