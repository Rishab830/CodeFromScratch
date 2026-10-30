"""A Code From Scratch mission. Compile, then play with Space."""
import asyncio
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 9
COIN_STORAGE_ID = 12
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'launch_rocket'
CONCEPT = 'nested-if'
LOOP_COMMANDS = ()
COIN_NAMES = ('fuel', 'launch')
COLLECTED_COINS = set()


def launch_rocket():
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
    def __init__(self):
        self.program = self.generator = None
        self.elapsed = self.cooldown = 0.0
        self.actions = 0
        self.power = self.fuel = False
        self.message = 'Check power first, then fuel. Press Space to run your checks.'
    def commands(self): return {'wait_for_power':self.wait_for_power,'refuel':self.refuel,'launch':self.launch}
    def sensors(self): return {'power_on':self.power_on,'fuel_ready':self.fuel_ready}
    def wait_for_power(self): return 'power'
    def refuel(self): return 'fuel'
    def launch(self): return 'launch'
    def power_on(self): return self.power
    def fuel_ready(self): return self.fuel
    def perform(self,command):
        self.generator = None
        if command == 'power':
            self.power = True
            self.message = 'Power is on. Run your checks again.'
        elif command == 'fuel':
            if not self.power:
                self.message = 'The fuel pump needs power first.'
                return 'dead'
            self.fuel = True
            remember('fuel')
            self.message = 'Fuel ready. Run your checks again.'
        elif command == 'launch':
            if not self.power or not self.fuel:
                self.message = 'Launch aborted. Check power and fuel.'
                return 'dead'
            remember('launch')
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
        self.message = "No launch action ran. Check power and fuel, then Compile."
        return None



def draw_scene(surface,world,small,title):
    surface.fill((77,68,105))
    for x,y in [(18,24),(85,43),(230,18),(288,58),(57,81)]: pygame.draw.rect(surface,(246,227,188),(x,y,2,2))
    pygame.draw.rect(surface,(162,154,182),(0,148,320,32))
    pygame.draw.rect(surface,(228,206,219),(142,75,36,73))
    pygame.draw.polygon(surface,(225,166,182),[(142,75),(160,48),(178,75)])
    pygame.draw.rect(surface,(147,191,217),(151,85,18,16))
    for x in (132,178): pygame.draw.rect(surface,(225,166,182),(x,128,10,20))
    for x,ready,name in [(44,world.power,'POWER'),(234,world.fuel,'FUEL')]:
        pygame.draw.rect(surface,(170,216,181) if ready else (173,139,166),(x,104,40,26))
        label(surface,small,name,x+5,136,(233,221,237))
    label(surface,title,'CHECK. THEN LAUNCH.',83,21,(237,222,240))
    for index,name in enumerate(COIN_NAMES): draw_coin(surface,pygame.Rect(281+index*13,9,8,10),name in COLLECTED_COINS)
    label(surface,small,world.message[:66],5,174,(233,221,237))



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
