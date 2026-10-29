"""A Code From Scratch mission. Compile, then play with Space."""
import asyncio
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 5
COIN_STORAGE_ID = 4
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'guide_robot'
CONCEPT = 'for'
LOOP_COMMANDS = ('move_left', 'move_right', 'move_up', 'move_down')
COIN_NAMES = ('loop', 'route')
COLLECTED_COINS = set()


def guide_robot():
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




ROBOT_PATH = {(8, 5), (7, 5), (6, 5), (5, 5), (5, 4), (5, 3), (4, 3), (3, 3), (2, 3)}
DIRECTIONS = {'left':(-1,0), 'right':(1,0), 'up':(0,-1), 'down':(0,1)}
WALLS = tuple(pygame.Rect(28+col*24, 8+row*22, 23, 21)
              for row in range(1,7) for col in range(11) if (col,row) not in ROBOT_PATH)
MOVE_SPEED = 48
def robot_point(cell): return 28+cell[0]*24+12, 8+cell[1]*22+11

class World:
    def __init__(self):
        self.program = self.generator = None
        self.elapsed = self.cooldown = 0.0
        self.actions = 0
        self.cell = (8, 5)
        self.x, self.y = robot_point(self.cell)
        self.moving = self.crashed = False
        self.direction = (0, 0)
        self.target_cell = self.cell
        self.message = 'Count the tiles. Write your loops, then press Space to step.'
    def commands(self):
        return {'move_left':self.move_left,'move_right':self.move_right,'move_up':self.move_up,'move_down':self.move_down}
    def sensors(self): return {}
    def move_left(self): return 'left'
    def move_right(self): return 'right'
    def move_up(self): return 'up'
    def move_down(self): return 'down'
    def perform(self, command):
        self.direction = DIRECTIONS[command]
        dx,dy = self.direction
        self.target_cell = self.cell[0]+dx, self.cell[1]+dy
        self.moving = True
        self.message = f'Moving {command}...'
        return None

    def animate_move(self, dt):
        target_x,target_y = robot_point(self.target_cell)
        remaining = abs(target_x-self.x) + abs(target_y-self.y)
        distance = min(MOVE_SPEED*dt, remaining)
        dx,dy = self.direction
        left,right,top,bottom = self.x-7, self.x+7, self.y-9, self.y+7
        hit_wall = False
        # Sweep the robot's body to the nearest wall, even on a slow frame.
        # Never reject a destination in advance or let the sprite enter a wall.
        for wall in WALLS:
            if dx and top < wall.bottom and bottom > wall.top:
                gap = wall.left-right if dx > 0 else left-wall.right
            elif dy and left < wall.right and right > wall.left:
                gap = wall.top-bottom if dy > 0 else top-wall.bottom
            else:
                continue
            if 0 <= gap <= distance:
                distance,hit_wall = gap,True
        self.x += dx*distance
        self.y += dy*distance
        if hit_wall:
            self.moving = False
            self.crashed = True
            self.message = 'That step hit a crate. Check the direction and repetition count.'
            return 'dead'
        if distance == remaining:
            self.x,self.y = target_x,target_y
            self.cell = self.target_cell
            self.moving = False
            if self.cell == (6,5): remember('loop')
            if self.cell == (5,3): remember('route')
            self.message = 'Dock reached. Press Space to finish your program.' if self.cell == (2,3) else f'Step {self.actions}. Keep following the path.'
        return None
    def program_finished(self):
        if self.cell == (2,3): return 'won'
        self.message = 'Your program ended before the dock. Add your movement loops and Compile.'
        return None

    def update(self, dt, action=False):
        self.elapsed += dt
        self.cooldown = max(0.0, self.cooldown - dt)
        if self.crashed:
            return None
        if self.moving:
            return self.animate_move(dt)
        if action and self.cooldown == 0:
            self.cooldown = 0.24
            return advance_program(self)
        return None




def draw_scene(surface, world, small, title):
    surface.fill((208, 218, 230))
    for row in range(1,7):
        for col in range(11):
            x,y = 28+col*24,8+row*22
            walkable = (col,row) in ROBOT_PATH
            pygame.draw.rect(surface,(244,231,211) if walkable else (178,168,194),(x,y,23,21))
            if not walkable: pygame.draw.rect(surface,(201,187,212),(x+3,y+3,17,3))
    gx,gy = robot_point((2,3))
    pygame.draw.rect(surface,(156,204,177),(gx-10,gy-9,20,18))
    label(surface,small,'DOCK',gx-9,gy-2)
    for cell,name in [((6,5),'loop'),((5,3),'route')]:
        x,y=robot_point(cell)
        draw_coin(surface,pygame.Rect(x-4,y-5,8,10),name in COLLECTED_COINS)
    x,y=round(world.x),round(world.y)
    pygame.draw.rect(surface,(113,129,163),(x-6,y-8,12,15))
    pygame.draw.rect(surface,(183,217,230),(x-7,y-9,14,9))
    for dx in (-4,2): pygame.draw.rect(surface,(76,90,124),(x+dx,y-6,2,2))
    pygame.draw.rect(surface,(255,220,148),(x,y-13,2,4))
    label(surface,small,'SPACE: NEXT STEP',32,163)
    label(surface,small,world.message[:65],5,174)



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
