"""Read the code, compile your change, then play your way to the exit."""
import asyncio
import pygame
import lesson_bridge
LEVEL_NUMBER = 4
WIDTH, HEIGHT, FLOOR = (320, 180, 145)
PUZZLE_NAME = 'robot_program'
PUZZLE_ARGUMENTS = ''
COLLECTED_COINS = set()
ROBOT_PATH = {(1, 4), (2, 4), (2, 5), (1, 5), (3, 4), (3, 3), (3, 2), (4, 2), (5, 2), (5, 3), (6, 3), (7, 3), (7, 4), (8, 4), (9, 4)}
DIRECTIONS = {'right': (1, 0), 'down': (0, 1), 'left': (-1, 0), 'up': (0, -1)}


def robot_program():
    # EDIT START
    return ["right", "down", "left", "up"]
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
        lesson_bridge.save_coins(LEVEL_NUMBER, COLLECTED_COINS)

def robot_point(cell):
    return (28 + cell[0] * 24 + 12, 8 + cell[1] * 22 + 11)

def checked_steps(value, allowed):
    if not isinstance(value, (list, tuple)) or not 1 <= len(value) <= 64:
        raise ValueError('Return a sequence of 1 to 64 instruction strings.')
    if any((not isinstance(step, str) or step not in allowed for step in value)):
        raise ValueError('Use these instructions: ' + ', '.join(sorted(allowed)))
    return list(value)

class World:

    def __init__(self, puzzle=None):
        self.puzzle = puzzle or robot_program
        self.elapsed = self.action_time = 0.0
        self.cell, self.step = ((1, 4), 0)
        self.sequence = []
        self.message = 'Play to explore. Compile to apply your changes.'
        self.sequence = checked_steps(self.puzzle(), set(DIRECTIONS))
        self.coins = {'loop': self.cell_coin((2, 5)), 'route': self.cell_coin((5, 2))}

    @staticmethod
    def cell_coin(cell):
        x, y = robot_point(cell)
        return pygame.Rect(x - 4, y - 5, 8, 10)

    def update(self, dt, action=False):
        self.elapsed += dt
        self.action_time = max(0.0, self.action_time - dt)
        pressed = action and self.action_time <= 0
        if pressed:
            self.action_time = 0.25
        if pressed:
            direction = self.sequence[self.step % len(self.sequence)]
            dx, dy = DIRECTIONS[direction]
            destination = (self.cell[0] + dx, self.cell[1] + dy)
            self.step += 1
            if destination not in ROBOT_PATH:
                self.message = 'That instruction leads into a crate. Restart and try another route.'
                return 'dead'
            self.cell = destination
            self.message = f'Step {self.step}: {direction}. Keep going to the green dock.'
        cx, cy = robot_point(self.cell)
        bounds = pygame.Rect(cx - 7, cy - 8, 14, 16)
        for name, coin in self.coins.items():
            if bounds.colliderect(coin):
                remember(name)
        if self.cell == (9, 4):
            return 'won'
        return None

def label(surface, font, text, x, y, color=(91, 79, 119)):
    surface.blit(font.render(text, False, color), (x, y))

def draw_scene(surface, world, small, title):
    surface.fill((225, 219, 244))
    surface.fill((208, 218, 230))
    for row in range(1, 7):
        for col in range(11):
            x, y = (28 + col * 24, 8 + row * 22)
            walkable = (col, row) in ROBOT_PATH
            pygame.draw.rect(surface, (244, 231, 211) if walkable else (178, 168, 194), (x, y, 23, 21))
            if not walkable:
                pygame.draw.rect(surface, (201, 187, 212), (x + 3, y + 3, 17, 3))
    gx, gy = robot_point((9, 4))
    pygame.draw.rect(surface, (156, 204, 177), (gx - 10, gy - 9, 20, 18))
    label(surface, small, 'DOCK', gx - 9, gy - 2)
    for name, coin in world.coins.items():
        draw_coin(surface, coin, name in COLLECTED_COINS)
    x, y = robot_point(world.cell)
    pygame.draw.rect(surface, (113, 129, 163), (x - 6, y - 8, 12, 15))
    pygame.draw.rect(surface, (183, 217, 230), (x - 7, y - 9, 14, 9))
    pygame.draw.rect(surface, (76, 90, 124), (x - 4, y - 6, 2, 2))
    pygame.draw.rect(surface, (76, 90, 124), (x + 2, y - 6, 2, 2))
    pygame.draw.rect(surface, (255, 220, 148), (x, y - 13, 2, 4))
    label(surface, small, f'STEP {world.step}   HOLD SPACE TO STEP', 31, 163)
    label(surface, small, f'COINS {len(COLLECTED_COINS)}/{len(world.coins)}', 8, 6)

async def main():
    lesson_bridge.emit('loading', phase=4, label='Starting your game', fraction=None, loaded=0, total=0)
    pygame.init()
    screen = pygame.display.set_mode((800, 450))
    surface = pygame.Surface((WIDTH, HEIGHT))
    small, title = (pygame.font.Font(None, 10), pygame.font.Font(None, 15))
    clock = pygame.time.Clock()
    world = World()
    COLLECTED_COINS.update((name for name in lesson_bridge.load_coins(LEVEL_NUMBER) if name in world.coins))
    state, attempt, has_input, previous_message = ('idle', 0, False, '')
    lesson_bridge.ready()
    while True:
        dt = min(clock.tick(60) / 1000, 0.04)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        command = lesson_bridge.poll()
        if command:
            try:
                puzzle = lesson_bridge.compile_puzzle(command['body'], PUZZLE_NAME, PUZZLE_ARGUMENTS)
                candidate = World(puzzle)
                world = candidate
                state, has_input, previous_message = ('playing', False, '')
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
