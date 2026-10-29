"""A Code From Scratch mission. Compile, then play with Space."""
import asyncio
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 5
COIN_STORAGE_ID = 10
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'charge_battery'
CONCEPT = 'while'
LOOP_COMMANDS = ('charge',)
COIN_NAMES = ('half', 'full')
COLLECTED_COINS = set()


def charge_battery():
    # EDIT START
    while battery_full():
        charge()
    open_exit()
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
        self.actions = self.battery = 0
        self.message = 'The battery is empty. Step the program and watch its condition.'
    def commands(self): return {'charge':self.charge,'open_exit':self.open_exit}
    def sensors(self): return {'battery_full':self.battery_full}
    def charge(self): return 'charge'
    def open_exit(self): return 'open'
    def battery_full(self): return self.battery >= 4
    def perform(self,command):
        if command == 'charge':
            self.battery += 1
            if self.battery > 4:
                self.message = 'Overcharged! Stop charging when the sensor says full.'
                return 'dead'
            if self.battery >= 2: remember('half')
            if self.battery == 4: remember('full')
            self.message = f'Battery: {self.battery}/4. Full sensor: {self.battery_full()}.'
        elif command == 'open':
            if not self.battery_full():
                self.message = 'The exit has no power. Check when the while loop should run.'
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
    surface.fill((224,221,241))
    label(surface,title,'CHARGE, THEN GO.',86,25)
    pygame.draw.rect(surface,(148,136,174),(62,82,198,52))
    pygame.draw.rect(surface,(184,174,202),(66,86,190,44))
    for index in range(4):
        pygame.draw.rect(surface,(173,220,180) if world.battery>index else (132,124,155),(73+index*45,92,39,32))
    pygame.draw.rect(surface,(148,136,174),(260,97,8,22))
    label(surface,small,f'BATTERY {world.battery}/4',127,143)
    label(surface,small,f'FULL SENSOR: {world.battery_full()}',113,155)
    for index,name in enumerate(COIN_NAMES): draw_coin(surface,pygame.Rect(278+index*14,9,8,10),name in COLLECTED_COINS)
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
