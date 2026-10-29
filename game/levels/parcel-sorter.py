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
BAY_CENTRES = {'left': 63, 'middle': 155, 'right': 247}
PARCEL_COLOURS = {'red': (235, 160, 171), 'blue': (153, 196, 229), 'yellow': (250, 219, 144)}
TRAVEL_SECONDS, DEPOSIT_SECONDS, ARRIVAL_SECONDS = 0.65, 0.55, 0.4


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
        self.phase = 'ready'
        self.delivery = None
        self.animation_time = self.belt_offset = 0.0
        self.parcel_x, self.parcel_y = 155.0, 71.0
        self.parcel_visible = True
        self.deposited = {bay: 0 for bay in BAY_CENTRES}
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
        self.delivery = command
        self.animation_time = 0.0
        self.phase = 'deposit' if command == 'middle' else 'travel'
        self.message = f'Sending the {self.parcel_colour()} parcel to the {command} bay...'
        return None

    def finish_deposit(self):
        self.parcel_visible = False
        self.deposited[self.delivery] += 1
        expected = {'red': 'left', 'blue': 'middle', 'yellow': 'right'}[self.parcel_colour()]
        if self.delivery != expected:
            self.phase = 'failed'
            self.message = 'That parcel went to the wrong bay. Restart and check your branches.'
            return 'dead'
        self.sorted += 1
        self.generator = None
        if self.sorted >= 3: remember('first')
        if self.sorted == 6:
            self.phase = 'complete'
            remember('second')
            return 'won'
        self.phase = 'arrive'
        self.animation_time = 0.0
        self.parcel_x, self.parcel_y = 155.0, 40.0
        self.parcel_visible = True
        self.message = f'{self.sorted} / 6 delivered. Bringing in the next parcel...'
        return None

    def update(self, dt, action=False):
        self.elapsed += dt
        self.cooldown = max(0.0, self.cooldown - dt)
        if self.phase in ('travel', 'deposit', 'arrive'):
            self.animation_time += dt
            if self.phase == 'travel':
                t = min(1.0, self.animation_time / TRAVEL_SECONDS)
                next_x = 155 + (BAY_CENTRES[self.delivery] - 155) * t
                self.belt_offset += next_x - self.parcel_x
                self.parcel_x = next_x
                if t == 1:
                    self.phase, self.animation_time = 'deposit', 0.0
            elif self.phase == 'deposit':
                t = min(1.0, self.animation_time / DEPOSIT_SECONDS)
                self.parcel_y = 71 + 69 * t * t
                if t == 1:
                    return self.finish_deposit()
            else:
                t = min(1.0, self.animation_time / ARRIVAL_SECONDS)
                self.parcel_y = 40 + 31 * (1 - (1 - t) ** 2)
                if t == 1:
                    self.phase = 'ready'
                    self.delivery = None
                    self.message = f'{self.sorted} / 6 delivered. The next parcel is {self.parcel_colour()}.'
            return None
        if self.phase in ('failed', 'complete'):
            return None
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
    # The feeder brings each new parcel down onto the centre of the belt.
    pygame.draw.rect(surface, (197, 187, 217), (137, 35, 36, 22))
    pygame.draw.rect(surface, (112, 102, 139), (141, 38, 28, 16))
    label(surface, small, 'PARCEL: ' + world.parcel_colour().upper(), 12, 43)
    for bay, name in zip(BAY_CENTRES, ('red', 'blue', 'yellow')):
        x = BAY_CENTRES[bay]
        pygame.draw.rect(surface, (146, 131, 169), (x-31, 110, 62, 39))
        pygame.draw.rect(surface, PARCEL_COLOURS[name], (x-28, 113, 56, 33))
        pygame.draw.rect(surface, (91, 80, 116), (x-21, 111, 42, 23))
        label(surface, small, bay.upper(), x-12, 99)
    # Moving slats and roller marks follow the parcel's horizontal travel.
    pygame.draw.rect(surface, (125, 114, 151), (12, 82, 296, 13))
    pygame.draw.rect(surface, (158, 148, 178), (12, 82, 296, 3))
    belt_clip = surface.get_clip()
    surface.set_clip(pygame.Rect(14, 85, 292, 8).clip(belt_clip))
    for x in range(-12, 320, 12):
        slat = x + round(world.belt_offset) % 12
        pygame.draw.rect(surface, (207, 197, 222), (slat, 85, 2, 3))
        pygame.draw.circle(surface, (191, 181, 205), (slat+5, 90), 3)
        turn = (round(world.belt_offset) // 3) % 2
        pygame.draw.line(surface, (113, 101, 141), (slat+3, 88+turn*4), (slat+7, 92-turn*4))
    surface.set_clip(belt_clip)
    if world.phase == 'deposit':
        x = BAY_CENTRES[world.delivery]
        pygame.draw.rect(surface, (91, 80, 116), (x-16, 82, 32, 13))
        pygame.draw.rect(surface, (187, 176, 207), (x-18, 81, 2, 15))
        pygame.draw.rect(surface, (187, 176, 207), (x+16, 81, 2, 15))
    if world.parcel_visible:
        # The bay's front wall hides the box as it drops all the way inside.
        surface.set_clip(pygame.Rect(0, 34, WIDTH, 114).clip(belt_clip))
        x, y = round(world.parcel_x), round(world.parcel_y)
        colour = PARCEL_COLOURS[world.parcel_colour()]
        pygame.draw.rect(surface, (128, 109, 145), (x-15, y-11, 30, 22))
        pygame.draw.rect(surface, colour, (x-13, y-10, 26, 19))
        pygame.draw.rect(surface, (247, 228, 191), (x-4, y-10, 7, 19))
        pygame.draw.rect(surface, (255, 242, 214), (x-4, y-10, 7, 3))
        surface.set_clip(belt_clip)
    for bay, name in zip(BAY_CENTRES, ('red', 'blue', 'yellow')):
        x = BAY_CENTRES[bay]
        pygame.draw.rect(surface, PARCEL_COLOURS[name], (x-28, 127, 56, 19))
        pygame.draw.rect(surface, (146, 131, 169), (x-31, 146, 62, 3))
        label(surface, small, name.upper(), x-11, 135)
        label(surface, small, str(world.deposited[bay]), x+20, 135)
    label(surface, small, f'{world.sorted} / 6 DELIVERED', 112, 157)
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
