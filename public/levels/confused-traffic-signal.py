"""Read the code, compile your change, then play your way to the exit."""
import asyncio
import pygame
import lesson_bridge
LEVEL_NUMBER = 1
COIN_STORAGE_ID = 3
WIDTH, HEIGHT, FLOOR = (320, 180, 145)
PUZZLE_NAME = 'next_light'
PUZZLE_ARGUMENTS = 'current'
COLLECTED_COINS = set()


def next_light(current):
    # EDIT START
    if current == "red":
        next_color = "yellow"
    elif current == "yellow":
        next_color = "red"
    else:
        next_color = "red"
    # EDIT END
    return next_color


COIN_SPRITE = ['..oooo..', '.offffo.', 'offffffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offffffo', '.offffo.', '..oooo..']

def draw_coin(surface, coin, collected):
    colors = {'o': (174, 146, 98) if collected else (188, 132, 59), 'f': (255, 207, 100), 'h': (255, 242, 179)}
    for y, row in enumerate(COIN_SPRITE):
        for x, pixel in enumerate(row):
            if pixel in colors and (not collected or pixel == 'o'):
                surface.set_at((coin.x + x, coin.y + y), colors[pixel])

def pixel_cloud(surface, x, y):
    for dx, dy, w, h in [(6, 0, 20, 4), (2, 4, 33, 5), (0, 9, 39, 5), (5, 14, 29, 3)]:
        pygame.draw.rect(surface, (255, 247, 242), (x + dx, y + dy, w, h))

def remember(name):
    if name not in COLLECTED_COINS:
        COLLECTED_COINS.add(name)
        lesson_bridge.save_coins(COIN_STORAGE_ID, COLLECTED_COINS)

class World:

    def __init__(self, puzzle=None):
        self.puzzle = puzzle or globals()[PUZZLE_NAME]
        self.x = 28.0
        self.elapsed = self.light_time = 0.0
        self.light = 'red'
        self.message = 'Play to explore. Compile to apply your changes.'
        self.coins = {'first': pygame.Rect(86, 130, 8, 10), 'second': pygame.Rect(234, 130, 8, 10)}

    def update(self, dt, left=False, right=False):
        self.elapsed += dt
        previous_x = self.x
        self.x = max(12.0, min(309.0, self.x + (int(right) - int(left)) * 70 * dt))
        bounds = pygame.Rect(round(self.x) - 5, FLOOR - 20, 10, 20)
        self.light_time += dt
        if self.light_time >= 1.6:
            self.light_time -= 1.6
            next_color = self.puzzle(self.light)
            if next_color not in ('red', 'yellow', 'green'):
                raise ValueError('Set next_color to red, yellow, or green.')
            self.light = next_color
            self.message = 'Signal: ' + self.light + '. Drive through when it is green.'
        if previous_x <= 119 < self.x and self.light != 'green':
            self.x = 119.0
            self.message = 'Waiting at the stop line. The signal needs to turn green.'
        bounds.x = round(self.x) - 5
        for name, coin in self.coins.items():
            if bounds.colliderect(coin):
                remember(name)
        if self.x >= 294:
            return 'won'
        return None

def label(surface, font, text, x, y, color=(91, 79, 119)):
    surface.blit(font.render(text, False, color), (x, y))

def draw_scene(surface, world, small, title):
    surface.fill((225, 219, 244))
    pixel_cloud(surface, 19, 23)
    pixel_cloud(surface, 185, 18)
    for x, height in [(2, 40), (35, 63), (76, 48), (213, 52), (266, 70)]:
        pygame.draw.rect(surface, (188, 183, 213), (x, 111 - height, 32, height))
        for wy in range(116 - height, 103, 10):
            pygame.draw.rect(surface, (246, 224, 176), (x + 5, wy, 5, 5))
    pygame.draw.rect(surface, (179, 172, 192), (0, 110, WIDTH, 58))
    pygame.draw.rect(surface, (242, 231, 216), (0, 110, WIDTH, 6))
    for x in range(0, WIDTH, 28):
        pygame.draw.rect(surface, (239, 220, 194), (x, 153, 14, 2))
    for x in range(132, 193, 10):
        pygame.draw.rect(surface, (237, 225, 218), (x, 119, 5, 28))
    pygame.draw.rect(surface, (248, 231, 219), (120, 118, 3, 30))
    pygame.draw.rect(surface, (123, 111, 151), (143, 51, 3, 62))
    pygame.draw.rect(surface, (115, 104, 139), (135, 40, 19, 42))
    for index, (name, color) in enumerate([('red', (240, 150, 164)), ('yellow', (255, 224, 132)), ('green', (156, 220, 172))]):
        pygame.draw.rect(surface, color if world.light == name else (143, 130, 157), (140, 45 + index * 12, 9, 9))
    pygame.draw.rect(surface, (139, 187, 170), (292, 107, 2, 39))
    pygame.draw.rect(surface, (187, 229, 185), (294, 108, 15, 10))
    label(surface, small, world.light.upper(), 132, 88)
    x = round(world.x)
    pygame.draw.rect(surface, (129, 171, 205), (x - 12, 131, 25, 12))
    pygame.draw.rect(surface, (183, 214, 231), (x - 6, 122, 15, 10))
    pygame.draw.rect(surface, (247, 222, 193), (x - 3, 124, 7, 6))
    for dx in (-7, 7):
        pygame.draw.rect(surface, (100, 86, 125), (x + dx - 2, 140, 5, 6))
    for name, coin in world.coins.items():
        draw_coin(surface, coin, name in COLLECTED_COINS)
    label(surface, small, f'COINS {len(COLLECTED_COINS)}/{len(world.coins)}', 8, 6)
    label(surface, small, world.message[:67], 7, 172)

async def main():
    lesson_bridge.emit('loading', phase=4, label='Starting your game', fraction=None, loaded=0, total=0)
    pygame.init()
    screen = pygame.display.set_mode((800, 450))
    surface = pygame.Surface((WIDTH, HEIGHT))
    small, title = (pygame.font.Font(None, 10), pygame.font.Font(None, 15))
    clock = pygame.time.Clock()
    world = World()
    COLLECTED_COINS.update((name for name in lesson_bridge.load_coins(COIN_STORAGE_ID) if name in world.coins))
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
                puzzle = lesson_bridge.compile_puzzle(command['body'], PUZZLE_NAME, PUZZLE_ARGUMENTS, result_name='next_color')
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
                left = bool(keys[pygame.K_LEFT] or keys[pygame.K_a])
                right = bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])
                has_input = has_input or left or right
                result = world.update(dt, left, right)
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
