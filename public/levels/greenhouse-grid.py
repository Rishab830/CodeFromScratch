"""A Code From Scratch mission. Compile, then play with Space."""
import asyncio
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 9
COIN_STORAGE_ID = 13
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'water_grid'
CONCEPT = 'nested-loops'
LOOP_COMMANDS = ('water_cell',)
COIN_NAMES = ('row', 'garden')
COLLECTED_COINS = set()


def water_grid():
    # EDIT START
    for row in range(2):
        for column in range(3):
            water_cell(row, column)
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
        self.actions = 0
        self.watered = set()
        self.cursor = None
        self.message = 'Three rows, three columns. Step the nested loops.'
    def commands(self): return {'water_cell':self.water_cell,'open_exit':self.open_exit}
    def sensors(self): return {}
    def water_cell(self,row,column): return ('water',row,column)
    def open_exit(self): return ('open',)
    def perform(self,command):
        if command[0] == 'water':
            row,column = command[1:]
            if type(row) is not int or type(column) is not int or not (0<=row<3 and 0<=column<3):
                self.message = 'That cell is outside the garden. Check both loop counts.'
                return 'dead'
            self.cursor = row,column
            self.watered.add((row,column))
            if all((0,col) in self.watered for col in range(3)): remember('row')
            if len(self.watered)==9: remember('garden')
            self.message = f'Row {row}, column {column}. Watered {len(self.watered)}/9.'
        elif command[0] == 'open':
            if len(self.watered)!=9:
                self.message = 'Some plants are still dry. Check the outer and inner loops.'
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
    surface.fill((224,229,216))
    label(surface,title,'EVERY ROW. EVERY PLANT.',61,17)
    for row in range(3):
        for column in range(3):
            x,y = 94+column*47,43+row*36
            pygame.draw.rect(surface,(194,158,148),(x,y,37,28))
            pygame.draw.rect(surface,(169,209,179) if (row,column) in world.watered else (218,193,169),(x+2,y+2,33,24))
            pygame.draw.rect(surface,(119,164,132),(x+18,y+10,2,12))
            pygame.draw.rect(surface,(144,185,143),(x+12,y+7,14,7))
            if world.cursor==(row,column): pygame.draw.rect(surface,(132,154,191),(x-2,y-2,41,32),2)
    label(surface,small,f'{len(world.watered)}/9 PLANTS WATERED',113,157)
    for index,name in enumerate(COIN_NAMES): draw_coin(surface,pygame.Rect(281+index*13,9,8,10),name in COLLECTED_COINS)
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
