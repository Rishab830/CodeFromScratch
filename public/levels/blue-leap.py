"""Compile your changes, then PLAY to reach the flag."""
import asyncio
import math
import pygame
import lesson_bridge

# Low-resolution art scales up with crisp pixels, never smoothing.
LEVEL_NUMBER = 2
WIDTH, HEIGHT = 320, 180
FLOOR = 141
BLUE = pygame.Rect(194, FLOOR, 66, 7)
SPIKES = [pygame.Rect(x, 83, 8, 17) for x in range(192, 264, 8)]
SPIKE_PLATFORM = pygame.Rect(188, 76, 80, 7)
GAP = pygame.Rect(132, FLOOR, 12, HEIGHT - FLOOR)
GOAL = pygame.Rect(30, FLOOR - 30, 16, 32)
SPAWN_X = 289


# EDIT START
class Girl:
    def __init__(self):
        self.x, self.y = float(SPAWN_X), float(FLOOR)
        self.vx, self.vy = 0.0, 0.0
        self.grounded = True

    def jump(self):
        if self.grounded:
            self.vy = -178
            self.grounded = False

    def move_left(self):
        self.vx = -55

    def move_right(self):
        self.vx = 55

    def stop(self):
        self.vx = 0
# EDIT END


def on_blue(player):
    player.jump()


def touching_blue(player):
    return BLUE.left <= player.x <= BLUE.right and player.grounded and player.y == FLOOR


def player_bounds(player):
    return pygame.Rect(round(player.x) - 4, round(player.y) - 20, 8, 20)


def triangle_hits_rect(triangle, rect):
    # Clip the solid spike triangle to the character rectangle; its empty
    # corners remain safe. This checks actual geometry, not an oversized box.
    points = [(float(x), float(y)) for x, y in triangle]
    for axis, edge, above in [(0, rect.left, True), (0, rect.right, False),
                              (1, rect.top, True), (1, rect.bottom, False)]:
        clipped = []
        if not points:
            return False
        previous = points[-1]
        previous_in = previous[axis] >= edge if above else previous[axis] <= edge
        for current in points:
            current_in = current[axis] >= edge if above else current[axis] <= edge
            if current_in != previous_in:
                fraction = (edge - previous[axis]) / (current[axis] - previous[axis])
                clipped.append(tuple(previous[i] + fraction * (current[i] - previous[i]) for i in (0, 1)))
            if current_in:
                clipped.append(current)
            previous, previous_in = current, current_in
        points = clipped
    return len(points) >= 3


def outcome(player):
    bounds = player_bounds(player)
    if player.y > HEIGHT + 22:
        return "dead"
    for spike in SPIKES:
        triangle = [(spike.left, spike.top), (spike.right, spike.top), (spike.centerx, spike.bottom)]
        if bounds.colliderect(spike) and triangle_hits_rect(triangle, bounds):
            return "dead"
    # Any route, any valid solution, any number of jumps: the flag wins.
    return "won" if bounds.colliderect(GOAL) else None


def update(player, dt, keys):
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.move_left()
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.move_right()
    else:
        player.stop()
    if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
        player.jump()
    if touching_blue(player):
        on_blue(player)

    # Small physics steps prevent movement from skipping over a spike.
    steps = max(1, math.ceil(dt / (1 / 180)))
    for _ in range(steps):
        step = dt / steps
        previous_y = player.y
        player.vy += 460 * step
        player.x = max(7, min(WIDTH - 7, player.x + player.vx * step))
        player.y += player.vy * step
        # Either foot may land on an edge, but the open gap has no floor.
        supported = player.x - 4 < GAP.left or player.x + 4 > GAP.right
        above_platform = player.x + 4 > SPIKE_PLATFORM.left and player.x - 4 < SPIKE_PLATFORM.right
        # In Level 2, land on the top while descending; the spikes below stay lethal.
        if LEVEL_NUMBER == 2 and above_platform and previous_y <= SPIKE_PLATFORM.top <= player.y and player.vy >= 0:
            player.y, player.vy, player.grounded = float(SPIKE_PLATFORM.top), 0.0, True
        elif supported and previous_y <= FLOOR <= player.y and player.vy >= 0:
            player.y, player.vy, player.grounded = float(FLOOR), 0.0, True
        else:
            player.grounded = False
        result = outcome(player)
        if result:
            return result
    return None


# Each character is one pixel: hair, skin, eyes, dress, ribbon, boots.
GIRL_SPRITE = [
    "...hhhh....", "..hhhhhh.pp", ".hhhhhhhhpp", ".hhsssshhh.",
    ".hssessesh.", "..ssssssh..", "...ssss....", "....ss.....",
    "..dddddd...", ".sdddddds..", ".sdddddds..", ".sdddddds..",
    "..dddddd...", "..dddddd...", ".dddddddd..", "...s..s....",
    "...s..s....", "...s..s....", "..bb..bb...", ".bbb..bbb..",
]
PALETTE = {"h": (88, 66, 99), "s": (255, 207, 173), "e": (65, 56, 85),
           "d": (237, 160, 185), "p": (255, 223, 144), "b": (101, 85, 121)}


def pixel_cloud(surface, x, y):
    for dx, dy, w, h in [(6, 0, 20, 4), (2, 4, 33, 5), (0, 9, 39, 5), (5, 14, 29, 3)]:
        pygame.draw.rect(surface, (255, 247, 242), (x + dx, y + dy, w, h))


def draw_scene(surface, player, seconds, small):
    surface.fill((218, 217, 246))
    pygame.draw.rect(surface, (232, 226, 247), (0, 60, WIDTH, 80))
    pygame.draw.rect(surface, (255, 228, 165), (264, 20, 18, 24))
    pygame.draw.rect(surface, (255, 228, 165), (261, 24, 24, 16))
    pygame.draw.rect(surface, (255, 238, 194), (265, 22, 14, 3))
    pixel_cloud(surface, 27, 23)
    pixel_cloud(surface, 125, 45)
    for color, points in [
        ((192, 201, 226), [(0, 116), (0, 95), (24, 95), (24, 88), (54, 88), (54, 79), (88, 79), (88, 85), (112, 85), (112, 99), (146, 99), (146, 116)]),
        ((187, 214, 204), [(92, 141), (92, 119), (120, 119), (120, 109), (149, 109), (149, 101), (181, 101), (181, 107), (215, 107), (215, 118), (250, 118), (250, 141)]),
        ((173, 204, 187), [(0, 141), (0, 125), (32, 125), (32, 117), (65, 117), (65, 122), (97, 122), (97, 133), (132, 133), (132, 141)]),
    ]:
        pygame.draw.polygon(surface, color, points)
    for x, y in [(15, 111), (304, 108), (90, 116)]:
        pygame.draw.rect(surface, (164, 147, 173), (x - 2, y, 4, 29))
        pygame.draw.rect(surface, (150, 190, 171), (x - 9, y - 15, 18, 18))
        pygame.draw.rect(surface, (150, 190, 171), (x - 12, y - 11, 24, 11))
        pygame.draw.rect(surface, (181, 213, 184), (x - 8, y - 16, 14, 5))
    pygame.draw.rect(surface, (173, 208, 174), (0, FLOOR, WIDTH, 7))
    pygame.draw.rect(surface, (237, 196, 186), (0, FLOOR + 7, WIDTH, 40))
    pygame.draw.rect(surface, (202, 163, 164), (0, FLOOR + 8, WIDTH, 3))
    for x in range(0, WIDTH, 16):
        pygame.draw.rect(surface, (196, 225, 185), (x, FLOOR, 10, 2))
        pygame.draw.rect(surface, (247, 215, 198), (x + 4, FLOOR + 19, 3, 2))
        pygame.draw.rect(surface, (218, 176, 174), (x + 11, FLOOR + 28, 3, 2))
    # The same small pit follows blue and the spikes on the way to the flag.
    pygame.draw.rect(surface, (103, 91, 134), GAP)
    pygame.draw.rect(surface, (86, 76, 116), (GAP.x, FLOOR + 22, GAP.width, HEIGHT - FLOOR - 22))
    pygame.draw.rect(surface, (163, 130, 149), (GAP.left, FLOOR + 7, 1, HEIGHT - FLOOR - 7))
    pygame.draw.rect(surface, (163, 130, 149), (GAP.right - 1, FLOOR + 7, 1, HEIGHT - FLOOR - 7))
    pygame.draw.rect(surface, (131, 183, 231), BLUE)
    pygame.draw.rect(surface, (185, 222, 249), (BLUE.x, BLUE.y, BLUE.width, 2))
    for x in range(BLUE.left + 4, BLUE.right, 8):
        pygame.draw.rect(surface, (169, 207, 244), (x, BLUE.y + 4, 3, 2))
    # Overhead spikes leave a safe corridor for walking underneath.
    pygame.draw.rect(surface, (157, 143, 190), SPIKE_PLATFORM)
    pygame.draw.rect(surface, (195, 181, 219), (SPIKE_PLATFORM.x, SPIKE_PLATFORM.y, SPIKE_PLATFORM.width, 3))
    for spike in SPIKES:
        pygame.draw.polygon(surface, (170, 113, 148), [(spike.left, spike.top), (spike.right, spike.top), (spike.centerx, spike.bottom)])
        pygame.draw.polygon(surface, (242, 174, 193), [(spike.left + 1, spike.top), (spike.right - 2, spike.top), (spike.centerx, spike.bottom - 3)])
    pygame.draw.rect(surface, (119, 112, 150), (37, FLOOR - 35, 2, 35))
    pygame.draw.rect(surface, (248, 225, 160), (36, FLOOR - 38, 4, 4))
    wave = int(seconds * 3) % 2
    pygame.draw.polygon(surface, (130, 185, 161), [(39, FLOOR - 34), (57, FLOOR - 34 + wave), (53, FLOOR - 25), (39, FLOOR - 25)])
    pygame.draw.rect(surface, (186, 232, 191), (40, FLOOR - 32, 9, 2))
    for fx in [65, 106, 153, 174, 276]:
        pygame.draw.rect(surface, (142, 178, 153), (fx, FLOOR - 5, 1, 5))
        pygame.draw.rect(surface, (255, 238, 185), (fx - 1, FLOOR - 7, 3, 3))
    px, py = round(player.x) - 5, round(player.y) - 20
    stride = 1 if abs(player.vx) and player.grounded and int(seconds * 9) % 2 else 0
    for row, line in enumerate(GIRL_SPRITE):
        for col, pixel in enumerate(line):
            if pixel in PALETTE:
                offset = stride * (-1 if col < 5 else 1) if row >= 15 else 0
                sx, sy = px + col + offset, py + row
                if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
                    surface.set_at((sx, sy), PALETTE[pixel])
    # Follow very high jumps without smearing off-screen sprite pixels.
    if player.y < 20:
        x = max(5, min(WIDTH - 6, round(player.x)))
        pygame.draw.polygon(surface, (237, 160, 185), [(x, 3), (x - 4, 9), (x + 4, 9)])
    surface.blit(small.render("GOAL", False, (112, 112, 142)), (26, 154))
    surface.blit(small.render("BLUE = ?", False, (107, 134, 171)), (208, 154))


async def main():
    lesson_bridge.emit("loading", phase=4, label="Starting your game", fraction=None, loaded=0, total=0)
    pygame.init()
    screen = pygame.display.set_mode((800, 450))
    surface = pygame.Surface((WIDTH, HEIGHT))
    small = pygame.font.Font(None, 10)
    clock = pygame.time.Clock()
    player = Girl()
    state, elapsed, attempt, has_input = "idle", 0.0, 0, False
    lesson_bridge.ready()
    while True:
        dt = min(clock.tick(60) / 1000, 0.04)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        command = lesson_bridge.poll()
        if command:
            try:
                if LEVEL_NUMBER == 1:
                    globals()["on_blue"] = lesson_bridge.compile_solution(command["body"])
                else:
                    globals()["Girl"] = lesson_bridge.compile_girl(command["body"], SPAWN_X, FLOOR)
                player, state, elapsed = Girl(), "playing", 0.0
                has_input = False
                attempt += 1
                lesson_bridge.emit("started", attempt=attempt)
            except Exception as error:
                state = "idle"
                lesson_bridge.emit("error", message=str(error))
        if state == "playing":
            try:
                keys = pygame.key.get_pressed()
                has_input = has_input or any(keys[key] for key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d, pygame.K_SPACE, pygame.K_UP, pygame.K_w))
                result = update(player, dt, keys)
                if result == "won" and not has_input:
                    result = None
                elapsed += dt
                if result:
                    state = result
                    lesson_bridge.emit(result, seconds=round(elapsed, 1))
            except Exception as error:
                state = "idle"
                lesson_bridge.emit("error", message=str(error))
        draw_scene(surface, player, pygame.time.get_ticks() / 1000, small)
        pygame.transform.scale(surface, (800, 450), screen)
        pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())
