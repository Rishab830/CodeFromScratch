"""Read the code, compile your change, then play your way to the exit."""
import asyncio
import pygame
import lesson_bridge
LEVEL_NUMBER = 7
WIDTH, HEIGHT, FLOOR = (320, 180, 145)
PUZZLE_NAME = 'escape_plan'
PUZZLE_ARGUMENTS = ''
COLLECTED_COINS = set()


def escape_plan():
    # EDIT START
    steps = []
    for cell in range(2):
        steps.append("power")
    if len(steps) == 3:
        steps.append("open")
        steps.append("unlock")
    return steps
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
        lesson_bridge.save_coins(LEVEL_NUMBER, COLLECTED_COINS)

def checked_steps(value, allowed):
    if not isinstance(value, (list, tuple)) or not 1 <= len(value) <= 64:
        raise ValueError('Return a sequence of 1 to 64 instruction strings.')
    if any((not isinstance(step, str) or step not in allowed for step in value)):
        raise ValueError('Use these instructions: ' + ', '.join(sorted(allowed)))
    return list(value)

class World:

    def __init__(self, puzzle=None):
        self.puzzle = puzzle or escape_plan
        self.x, self.y = (28.0, float(FLOOR))
        self.elapsed = self.action_time = 0.0
        self.processing = False
        self.power, self.unlocked, self.exit_open = (0, False, False)
        self.sequence, self.sequence_index, self.sequence_time = ([], 0, 0.0)
        self.message = 'Play to explore. Compile to apply your changes.'
        self.coins = {'first': pygame.Rect(126, 130, 8, 10), 'second': pygame.Rect(234, 130, 8, 10)}
        self.sequence = checked_steps(self.puzzle(), {'power', 'unlock', 'open'})

    def update(self, dt, left=False, right=False, action=False):
        self.elapsed += dt
        self.action_time = max(0.0, self.action_time - dt)
        pressed = action and self.action_time <= 0
        if pressed:
            self.action_time = 0.25
        self.x = max(12.0, min(309.0, self.x + (int(right) - int(left)) * 65 * dt))
        bounds = pygame.Rect(round(self.x) - 5, FLOOR - 20, 10, 20)
        if pressed and abs(self.x - 64) < 24 and (not self.processing):
            self.power, self.unlocked, self.exit_open = (0, False, False)
            self.processing, self.sequence_index, self.sequence_time = (True, 0, 0.0)
        if self.processing:
            self.sequence_time += dt
            if self.sequence_time >= 0.4:
                self.sequence_time -= 0.4
                instruction = self.sequence[self.sequence_index]
                self.sequence_index += 1
                if instruction == 'power':
                    self.power = min(3, self.power + 1)
                    self.message = f'Power cells: {self.power} / 3.'
                elif instruction == 'unlock':
                    self.unlocked = self.power == 3
                    self.message = 'Latch unlocked.' if self.unlocked else 'The latch needs all three power cells.'
                elif instruction == 'open':
                    self.exit_open = self.unlocked
                    self.message = 'Exit open. Walk through it!' if self.exit_open else 'The exit latch is still locked.'
                if self.sequence_index >= len(self.sequence):
                    self.processing = False
        bounds.x = round(self.x) - 5
        for name, coin in self.coins.items():
            if bounds.colliderect(coin):
                remember(name)
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
    pygame.draw.rect(surface, (143, 131, 173), (49, 111, 30, 34))
    pygame.draw.rect(surface, (190, 222, 211), (53, 115, 22, 14))
    label(surface, small, 'SPACE', 52, 154)
    for index in range(3):
        pygame.draw.rect(surface, (157, 206, 175) if world.power > index else (176, 163, 196), (110 + index * 35, 86, 22, 30))
        pygame.draw.rect(surface, (211, 237, 201) if world.power > index else (205, 191, 220), (115 + index * 35, 90, 12, 19))
    label(surface, small, 'POWER     LATCH     EXIT', 101, 60)
    draw_door(surface, 288, world.exit_open, 'EXIT', small, True)
    label(surface, small, 'UNLOCKED' if world.unlocked else 'LOCKED', 244, 155)
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
