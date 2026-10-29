"""Read the code, compile your change, then play your way to the exit."""
import asyncio
import pygame
import lesson_bridge
LEVEL_NUMBER = 13
COIN_STORAGE_ID = 5
WIDTH, HEIGHT, FLOOR = (320, 180, 145)
PUZZLE_NAME = 'should_collect'
PUZZLE_ARGUMENTS = 'count'
COLLECTED_COINS = set()


def should_collect(count):
    # EDIT START
    return count >= 0
    # EDIT END


GIRL_SPRITE = ['...hhhh....', '..hhhhhh.pp', '.hhhhhhhhpp', '.hhsssshhh.', '.hssessesh.', '..ssssssh..', '...ssss....', '....ss.....', '..dddddd...', '.sdddddds..', '.sdddddds..', '.sdddddds..', '..dddddd...', '..dddddd...', '.dddddddd..', '...s..s....', '...s..s....', '...s..s....', '..bb..bb...', '.bbb..bbb..']
PALETTE = {'h': (88, 66, 99), 's': (255, 207, 173), 'e': (65, 56, 85), 'd': (237, 160, 185), 'p': (255, 223, 144), 'b': (101, 85, 121)}
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
        self.x, self.y = (28.0, float(FLOOR))
        self.elapsed = self.action_time = 0.0
        self.count, self.processing, self.finished = (0, False, False)
        self.exit_open = False
        self.sequence_time = 0.0
        self.message = 'Play to explore. Compile to apply your changes.'
        self.coins = {f'coin-{i}': pygame.Rect(104 + i * 23, 58, 8, 10) for i in range(1, 6)}

    def update(self, dt, left=False, right=False, action=False):
        self.elapsed += dt
        self.action_time = max(0.0, self.action_time - dt)
        pressed = action and self.action_time <= 0
        if pressed:
            self.action_time = 0.25
        self.x = max(12.0, min(309.0, self.x + (int(right) - int(left)) * 65 * dt))
        if pressed and abs(self.x - 72) < 24 and (not self.processing) and (not self.finished):
            self.processing = True
            self.sequence_time = 0.0
            self.message = 'Collector running. Watch its count.'
        if self.processing:
            self.sequence_time += dt
            if self.sequence_time >= 0.32:
                self.sequence_time -= 0.32
                decision = self.puzzle(self.count)
                if type(decision) is not bool:
                    raise ValueError('Return True or False from should_collect(count).')
                if decision:
                    self.count = min(99, self.count + 1)
                    if self.count <= 5:
                        remember(f'coin-{self.count}')
                    self.message = f'Collector: {self.count} / 5. ' + ('Too many! It is still running.' if self.count > 5 else 'Still collecting...')
                else:
                    self.processing, self.finished = (False, True)
                    self.exit_open = self.count == 5
                    self.message = 'Exactly five. The door is unlocked!' if self.exit_open else 'The collector stopped at the wrong number. Restart to try again.'
        if self.exit_open and self.x >= 287:
            return 'won'
        return None

def label(surface, font, text, x, y, color=(91, 79, 119)):
    surface.blit(font.render(text, False, color), (x, y))

def draw_girl(surface, x, y, moving):
    for row, line in enumerate(GIRL_SPRITE):
        for col, pixel in enumerate(line):
            if pixel in PALETTE:
                offset = int(pygame.time.get_ticks() / 110) % 2 if moving and row >= 15 else 0
                surface.set_at((round(x) - 5 + col, round(y) - 20 + row - offset), PALETTE[pixel])

def draw_door(surface, x, opened, symbol, font, correct=False):
    pygame.draw.rect(surface, (145, 133, 167), (x - 15, 87, 30, 58))
    pygame.draw.rect(surface, (116, 105, 144) if opened else (218, 189, 211), (x - 12, 90, 24, 55))
    if not opened:
        pygame.draw.rect(surface, (240, 219, 226), (x - 9, 94, 18, 3))
        pygame.draw.rect(surface, (242, 219, 147), (x + 7, 118, 3, 3))
    else:
        pygame.draw.rect(surface, (173, 222, 185) if correct else (182, 162, 198), (x - 10, 94, 20, 49))
    label(surface, font, symbol, x - 12, 76)

def draw_scene(surface, world, small, title):
    surface.fill((225, 219, 244))
    pixel_cloud(surface, 19, 23)
    pixel_cloud(surface, 185, 18)
    pygame.draw.rect(surface, (211, 205, 228), (0, 65, WIDTH, 80))
    for x in range(8, WIDTH, 32):
        pygame.draw.rect(surface, (228, 217, 235), (x, 71, 23, 3))
    pygame.draw.rect(surface, (185, 212, 184), (0, FLOOR, WIDTH, 6))
    pygame.draw.rect(surface, (232, 199, 187), (0, FLOOR + 6, WIDTH, HEIGHT - FLOOR))
    for x in range(0, WIDTH, 16):
        pygame.draw.rect(surface, (245, 219, 197), (x + 4, 163, 3, 2))
    pygame.draw.rect(surface, (146, 130, 179), (53, 105, 38, 40))
    pygame.draw.rect(surface, (187, 219, 207), (57, 110, 30, 16))
    label(surface, small, f'{world.count:02} / 5', 60, 115)
    pygame.draw.rect(surface, (238, 176, 184), (64, 133, 15, 4))
    label(surface, small, 'COLLECTOR', 50, 94)
    label(surface, small, 'SPACE', 60, 154)
    label(surface, title, 'FIVE, THEN STOP.', 110, 35)
    draw_door(surface, 288, world.exit_open, 'EXIT', small, True)
    draw_girl(surface, world.x, world.y, False)
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
                left = bool(keys[pygame.K_LEFT] or keys[pygame.K_a])
                right = bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])
                action = bool(keys[pygame.K_SPACE])
                has_input = has_input or left or right or action
                result = world.update(dt, left, right, action)
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
