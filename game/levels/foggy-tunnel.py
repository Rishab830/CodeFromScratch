"""A Code From Scratch mission. Compile, then play with Space."""
import asyncio
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 6
COIN_STORAGE_ID = 11
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'escape'
CONCEPT = 'while'
LOOP_COMMANDS = ('move_forward',)
COIN_NAMES = ('tunnel-1', 'tunnel-2', 'tunnel-3')
COLLECTED_COINS = set()


def escape():
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
    def __init__(self,lengths=None):
        self.program = self.generator = None
        self.elapsed = self.cooldown = 0.0
        self.actions = self.round = self.position = 0
        self.lengths = lengths or random.sample(range(4,10),3)
        self.message = 'Three hidden tunnels. Read the exit sensor, not a fixed step count.'
    def commands(self): return {'move_forward':self.move_forward,'open_exit':self.open_exit}
    def sensors(self): return {'exit_detected':self.exit_detected}
    def move_forward(self): return 'move'
    def open_exit(self): return 'open'
    def exit_detected(self): return self.position == self.lengths[min(self.round,2)]
    def perform(self,command):
        if command == 'move':
            if self.exit_detected():
                self.message = 'You walked past the exit. Check your stopping condition.'
                return 'dead'
            self.position += 1
            if self.position == self.lengths[min(self.round,2)]-1: remember(f'tunnel-{self.round+1}')
            self.message = 'Exit detected! Your program should open it now.' if self.exit_detected() else 'No exit detected. Keep exploring the fog.'
        elif command == 'open':
            if not self.exit_detected():
                self.message = 'No exit here. Use the sensor before opening the door.'
                return 'dead'
            self.round += 1
            if self.round == 3: return 'won'
            self.position = 0
            self.generator = None
            self.message = f'Tunnel {self.round+1}/3. Same program, a different hidden distance.'
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
    surface.fill((58,53,82))
    label(surface,title,'THE FOGGY TUNNEL',77,23,(222,211,242))
    pygame.draw.rect(surface,(105,96,131),(0,74,320,75))
    position = world.position
    length = world.lengths[min(world.round,2)]
    for step in range(max(0,position-2),min(length+1,position+3)):
        x = 74+(step-position)*35
        pygame.draw.rect(surface,(185,172,196),(x-13,139,30,8))
        pygame.draw.rect(surface,(132,117,153),(x-13,147,30,23))
        if step == length-1:
            draw_coin(surface,pygame.Rect(x-3,122,8,10),f'tunnel-{min(world.round+1,3)}' in COLLECTED_COINS)
        if step == length and length-position<=1:
            pygame.draw.rect(surface,(161,200,180),(x-10,96,22,43))
            pygame.draw.rect(surface,(206,233,199),(x-7,99,16,40))
            label(surface,small,'EXIT',x-7,85,(225,233,213))
    pygame.draw.rect(surface,(104,96,131),(151,75,169,65))
    pygame.draw.rect(surface,(79,72,106),(184,75,136,96))
    pygame.draw.rect(surface,(64,58,89),(219,75,101,96))
    pygame.draw.rect(surface,(183,216,230),(68,120,15,14))
    pygame.draw.rect(surface,(110,129,163),(70,134,11,7))
    for dx in (0,7): pygame.draw.rect(surface,(72,83,116),(69+dx,141,4,4))
    label(surface,small,f'TUNNEL {min(world.round+1,3)}/3',12,8,(216,207,235))
    label(surface,small,'EXIT SENSOR: '+('YES' if world.position==length else 'NO'),12,157,(216,207,235))
    for index,name in enumerate(COIN_NAMES): draw_coin(surface,pygame.Rect(274+index*13,9,8,10),name in COLLECTED_COINS)
    label(surface,small,world.message[:68],5,174,(216,207,235))



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
