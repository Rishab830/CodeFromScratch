"""A Code From Scratch mission. Compile, then play with Space."""
import asyncio
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 2
COIN_STORAGE_ID = 8
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'sort_parcel'
CONCEPT = 'if'
LOOP_COMMANDS = ()
COIN_NAMES = ('first', 'second')
COLLECTED_COINS = set()


def sort_parcel():
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




class World:
    def __init__(self, colours=None):
        self.program = self.generator = None
        self.elapsed = self.cooldown = 0.0
        self.actions = self.sorted = 0
        self.colours = colours or random.sample(['red', 'blue', 'yellow'], 3) + random.sample(['red', 'blue', 'yellow'], 3)
        self.message = "Read the parcel colour. Press Space to run your sorter."

    def commands(self):
        return {'send_left': self.send_left, 'send_middle': self.send_middle, 'send_right': self.send_right}
    def sensors(self):
        return {'parcel_colour': self.parcel_colour}
    def send_left(self): return 'left'
    def send_middle(self): return 'middle'
    def send_right(self): return 'right'
    def parcel_colour(self): return self.colours[min(self.sorted, len(self.colours)-1)]

    def perform(self, command):
        expected = {'red': 'left', 'blue': 'middle', 'yellow': 'right'}[self.parcel_colour()]
        if command != expected:
            self.message = 'That parcel went to the wrong bay. Restart and check your branches.'
            return 'dead'
        self.sorted += 1
        self.generator = None
        if self.sorted >= 3: remember('first')
        if self.sorted == 6:
            remember('second')
            return 'won'
        self.message = f'{self.sorted} / 6 delivered. The next parcel is {self.parcel_colour()}.'
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



def draw_scene(surface, world, small, title):
    surface.fill((223, 217, 242))
    label(surface, title, 'THE DELIVERY DEPOT', 76, 20)
    colours = [(235, 160, 171), (153, 196, 229), (250, 219, 144)]
    for index, (name, colour) in enumerate(zip(('RED', 'BLUE', 'YELLOW'), colours)):
        x = 35 + index * 92
        pygame.draw.rect(surface, (146, 131, 169), (x-3, 65, 62, 39))
        pygame.draw.rect(surface, colour, (x, 68, 56, 34))
        pygame.draw.rect(surface, (112, 102, 139), (x+8, 72, 40, 12))
        label(surface, small, name, x+16, 91)
        label(surface, small, ('LEFT', 'MIDDLE', 'RIGHT')[index], x+15, 111)
    pygame.draw.rect(surface, (158, 148, 178), (12, 137, 296, 15))
    for x in range(14, 309, 12):
        pygame.draw.rect(surface, (191, 181, 205), (x, 140, 7, 9))
    colour = {'red': colours[0], 'blue': colours[1], 'yellow': colours[2]}[world.parcel_colour()]
    pygame.draw.rect(surface, (128, 109, 145), (145, 119, 30, 22))
    pygame.draw.rect(surface, colour, (147, 120, 26, 19))
    pygame.draw.rect(surface, (247, 228, 191), (156, 120, 7, 19))
    label(surface, small, f'{world.sorted} / 6 DELIVERED', 112, 155)
    for index, name in enumerate(COIN_NAMES): draw_coin(surface, pygame.Rect(284+index*12, 7, 8, 10), name in COLLECTED_COINS)
    label(surface, small, world.message[:67], 5, 172)



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
