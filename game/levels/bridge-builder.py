"""A Code From Scratch mission. Compile, then play with Space."""
import asyncio
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 4
COIN_STORAGE_ID = 9
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'build_bridge'
CONCEPT = 'for'
LOOP_COMMANDS = ('place_plank',)
COIN_NAMES = ('first', 'second')
COLLECTED_COINS = set()
BRIDGE_START, PLANK_WIDTH, REQUIRED_PLANKS = 98, 14, 10
BRIDGE_END = BRIDGE_START + PLANK_WIDTH * REQUIRED_PLANKS


def build_bridge():
    # EDIT START
    for plank in range(5):
        place_plank()
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
        self.x, self.y, self.vy = 66.0, 141.0, 0.0
        self.moving = self.program_done = False
        self.build_started = False
        self.message = 'Tap Space once to build. Left / Right moves Maya.'
    def commands(self): return {'place_plank': self.place_plank}
    def sensors(self): return {}
    def place_plank(self): return 'plank'
    def perform(self, command):
        if command == 'plank':
            self.planks += 1
            self.message = 'Bridge reaches the bank! Walk to the flag with Left / Right.' if self.planks >= REQUIRED_PLANKS else f'Building: {self.planks} / {REQUIRED_PLANKS} planks. Your loop is running.'
        return None
    def update(self, dt, action=False, left=False, right=False):
        self.elapsed += dt
        self.cooldown = max(0.0, self.cooldown-dt)
        if action:
            self.build_started = True
        if self.build_started and self.cooldown == 0 and not self.program_done:
            self.cooldown = 0.16
            result = advance_program(self)
            if result: return result
        direction = int(right) - int(left)
        self.moving = direction != 0
        # Small physics steps prevent walking across an unbuilt space in one frame.
        steps = max(1, int(dt * 120) + 1)
        for _ in range(steps):
            step = dt / steps
            self.x = max(12.0, min(309.0, self.x + direction * 65 * step))
            supported = self.x < BRIDGE_START or self.x >= BRIDGE_END or self.x < BRIDGE_START + self.planks * PLANK_WIDTH
            previous_y = self.y
            self.vy += 460 * step
            self.y += self.vy * step
            if supported and previous_y <= 141 and self.y >= 141:
                self.y, self.vy = 141.0, 0.0
            if self.y > HEIGHT + 20:
                self.message = 'You fell through a missing plank. Fix the loop and rebuild.'
                return 'dead'
        if self.y == 141:
            if abs(self.x - 192) < 8: remember('first')
            if abs(self.x - 250) < 8: remember('second')
            if self.x >= 280: return 'won'
        return None
    def program_finished(self):
        self.program_done = True
        self.message = f'{self.planks} planks built. Walk to the flag with Left / Right.' if self.planks >= REQUIRED_PLANKS else f'Your loop built {self.planks} planks. The gap needs {REQUIRED_PLANKS}. Check its count.'
        return None



def draw_scene(surface, world, small, title):
    surface.fill((218, 220, 244))
    pixel_cloud(surface, 24, 30)
    pixel_cloud(surface, 203, 24)
    pygame.draw.rect(surface, (150, 188, 207), (0, 146, 320, 34))
    for left, width in [(0, BRIDGE_START), (BRIDGE_END, WIDTH-BRIDGE_END)]:
        pygame.draw.rect(surface, (177, 211, 174), (left, 141, width, 7))
        pygame.draw.rect(surface, (232, 193, 180), (left, 148, width, 32))
    for index in range(max(REQUIRED_PLANKS,world.planks)):
        x = BRIDGE_START+index*PLANK_WIDTH
        rect = pygame.Rect(x, 140, PLANK_WIDTH, 7)
        pygame.draw.rect(surface, (224, 185, 147) if world.planks > index else (125, 153, 184), rect, 0 if world.planks > index else 1)
        if world.planks > index:
            pygame.draw.line(surface,(164,130,112),(x+PLANK_WIDTH-1,141),(x+PLANK_WIDTH-1,146),1)
            pygame.draw.rect(surface,(147,121,110),(x+3,142,1,1))
    label(surface, title, 'TEN PLANKS TO THE OTHER SIDE.', 33, 67)
    label(surface, small, f'PLANKS {world.planks:02} / {REQUIRED_PLANKS}',125,91)
    for x, name in [(188, 'first'), (246, 'second')]: draw_coin(surface, pygame.Rect(x, 125, 8, 10), name in COLLECTED_COINS)
    pygame.draw.rect(surface, (111, 143, 131), (281, 106, 2, 35))
    pygame.draw.rect(surface, (181, 224, 177), (283, 107, 17, 10))
    draw_girl(surface, world.x, world.y, world.moving)
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
                left = bool(keys[pygame.K_LEFT] or keys[pygame.K_a])
                right = bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])
                has_input = has_input or action or left or right
                result = world.update(dt, action, left, right)
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
