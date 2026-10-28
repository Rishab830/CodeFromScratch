"""Read the code, compile your change, then play your way to the exit."""
import asyncio
import pygame
import lesson_bridge

LEVEL_NUMBER = 6
WIDTH, HEIGHT, FLOOR = 320, 180, 145
PUZZLE_NAME = "choose_door"
PUZZLE_ARGUMENTS = "password"
COLLECTED_COINS = set()
def choose_door(password):
    # EDIT START
    if password == "STAR":
        return 0
    return 2
    # EDIT END

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
COIN_SPRITE = [
    "..oooo..", ".offffo.", "offffffo", "offhhffo", "offhhffo",
    "offhhffo", "offhhffo", "offffffo", ".offffo.", "..oooo..",
]


def draw_coin(surface, coin, collected):
    colors = {"o": (174, 146, 98) if collected else (188, 132, 59),
              "f": (255, 207, 100), "h": (255, 242, 179)}
    for y, row in enumerate(COIN_SPRITE):
        for x, pixel in enumerate(row):
            if pixel in colors and (not collected or pixel == "o"):
                surface.set_at((coin.x + x, coin.y + y), colors[pixel])


def pixel_cloud(surface, x, y):
    for dx, dy, w, h in [(6, 0, 20, 4), (2, 4, 33, 5), (0, 9, 39, 5), (5, 14, 29, 3)]:
        pygame.draw.rect(surface, (255, 247, 242), (x + dx, y + dy, w, h))





def remember(name):
    if name not in COLLECTED_COINS:
        COLLECTED_COINS.add(name)
        lesson_bridge.save_coins(LEVEL_NUMBER, COLLECTED_COINS)


def robot_point(cell):
    return 28 + cell[0] * 24 + 12, 8 + cell[1] * 22 + 11


def checked_steps(value, allowed):
    if not isinstance(value, (list, tuple)) or not 1 <= len(value) <= 64:
        raise ValueError("Return a sequence of 1 to 64 instruction strings.")
    if any(not isinstance(step, str) or step not in allowed for step in value):
        raise ValueError("Use these instructions: " + ", ".join(sorted(allowed)))
    return list(value)


class World:
    def __init__(self, puzzle=None):
        self.puzzle = puzzle or globals()[PUZZLE_NAME]
        self.x, self.y = 28.0, float(FLOOR)
        self.elapsed = self.light_time = self.action_time = 0.0
        self.light = "red"
        self.cell, self.step = (1, 4), 0
        self.count, self.processing, self.finished = 0, False, False
        self.authorized, self.opened = False, None
        self.power, self.unlocked, self.exit_open = 0, False, False
        self.sequence, self.sequence_index, self.sequence_time = [], 0, 0.0
        self.message = "Play to explore. Compile to apply your changes."
        if LEVEL_NUMBER == 4:
            self.sequence = checked_steps(self.puzzle(), set(DIRECTIONS))
            self.coins = {"loop": self.cell_coin((2, 5)), "route": self.cell_coin((5, 2))}
        elif LEVEL_NUMBER == 5:
            self.coins = {f"coin-{i}": pygame.Rect(104 + i * 23, 58, 8, 10) for i in range(1, 6)}
        else:
            self.coins = {"first": pygame.Rect(86 if LEVEL_NUMBER == 3 else 126, 130, 8, 10),
                          "second": pygame.Rect(234, 130, 8, 10)}
        if LEVEL_NUMBER == 7:
            self.sequence = checked_steps(self.puzzle(), {"power", "unlock", "open"})

    @staticmethod
    def cell_coin(cell):
        x, y = robot_point(cell)
        return pygame.Rect(x - 4, y - 5, 8, 10)

    def update(self, dt, left=False, right=False, action=False, password=""):
        self.elapsed += dt
        self.action_time = max(0.0, self.action_time - dt)
        pressed = action and self.action_time <= 0
        if pressed:
            self.action_time = 0.25
        if LEVEL_NUMBER == 4:
            if pressed:
                direction = self.sequence[self.step % len(self.sequence)]
                dx, dy = DIRECTIONS[direction]
                destination = self.cell[0] + dx, self.cell[1] + dy
                self.step += 1
                if destination not in ROBOT_PATH:
                    self.message = "That instruction leads into a crate. Restart and try another route."
                    return "dead"
                self.cell = destination
                self.message = f"Step {self.step}: {direction}. Keep going to the green dock."
            cx, cy = robot_point(self.cell)
            bounds = pygame.Rect(cx - 7, cy - 8, 14, 16)
        else:
            previous_x = self.x
            self.x = max(12.0, min(309.0, self.x + (int(right) - int(left)) * (70 if LEVEL_NUMBER == 3 else 65) * dt))
            bounds = pygame.Rect(round(self.x) - 5, FLOOR - 20, 10, 20)
            if LEVEL_NUMBER == 3:
                self.light_time += dt
                if self.light_time >= 1.6:
                    self.light_time -= 1.6
                    next_color = self.puzzle(self.light)
                    if next_color not in ("red", "yellow", "green"):
                        raise ValueError("Return red, yellow, or green for the next light.")
                    self.light = next_color
                    self.message = "Signal: " + self.light + ". Drive through when it is green."
                if previous_x <= 119 < self.x and self.light != "green":
                    self.x = 119.0
                    self.message = "Waiting at the stop line. The signal needs to turn green."
            elif LEVEL_NUMBER == 5:
                if pressed and abs(self.x - 72) < 24 and not self.processing and not self.finished:
                    self.processing = True
                    self.sequence_time = 0.0
                    self.message = "Collector running. Watch its count."
                if self.processing:
                    self.sequence_time += dt
                    if self.sequence_time >= 0.32:
                        self.sequence_time -= 0.32
                        decision = self.puzzle(self.count)
                        if type(decision) is not bool:
                            raise ValueError("Return True or False from should_collect(count).")
                        if decision:
                            self.count = min(99, self.count + 1)
                            if self.count <= 5:
                                remember(f"coin-{self.count}")
                            self.message = f"Collector: {self.count} / 5. " + ("Too many! It is still running." if self.count > 5 else "Still collecting...")
                        else:
                            self.processing, self.finished = False, True
                            self.exit_open = self.count == 5
                            self.message = "Exactly five. The door is unlocked!" if self.exit_open else "The collector stopped at the wrong number. Restart to try again."
            elif LEVEL_NUMBER == 6:
                if pressed and abs(self.x - 48) < 24:
                    choice = self.puzzle(password)
                    if choice is not None and (type(choice) is not int or choice not in (0, 1, 2)):
                        raise ValueError("Return door 0, 1, 2, or None.")
                    self.opened = choice
                    self.authorized = password == "STAR"
                    self.message = "Access denied. Check the terminal note." if choice is None else f"Door {choice + 1} opened. Walk to the door."
                if self.opened is not None and abs(self.x - (92 + 80 * self.opened)) < 9:
                    if self.opened == 2 and self.authorized:
                        return "won"
                    self.message = "That door leads to a dead end. Read its symbol and try again."
                    return "dead"
            elif LEVEL_NUMBER == 7:
                if pressed and abs(self.x - 64) < 24 and not self.processing:
                    self.power, self.unlocked, self.exit_open = 0, False, False
                    self.processing, self.sequence_index, self.sequence_time = True, 0, 0.0
                if self.processing:
                    self.sequence_time += dt
                    if self.sequence_time >= 0.4:
                        self.sequence_time -= 0.4
                        instruction = self.sequence[self.sequence_index]
                        self.sequence_index += 1
                        if instruction == "power":
                            self.power = min(3, self.power + 1)
                            self.message = f"Power cells: {self.power} / 3."
                        elif instruction == "unlock":
                            self.unlocked = self.power == 3
                            self.message = "Latch unlocked." if self.unlocked else "The latch needs all three power cells."
                        elif instruction == "open":
                            self.exit_open = self.unlocked
                            self.message = "Exit open. Walk through it!" if self.exit_open else "The exit latch is still locked."
                        if self.sequence_index >= len(self.sequence):
                            self.processing = False
            bounds.x = round(self.x) - 5
        if LEVEL_NUMBER != 5:
            for name, coin in self.coins.items():
                if bounds.colliderect(coin):
                    remember(name)
        if LEVEL_NUMBER == 4 and self.cell == (9, 4):
            return "won"
        if LEVEL_NUMBER == 3 and self.x >= 294:
            return "won"
        if LEVEL_NUMBER in (5, 7) and self.exit_open and self.x >= 287:
            return "won"
        return None


def label(surface, font, text, x, y, color=(91, 79, 119)):
    surface.blit(font.render(text, False, color), (x, y))


def draw_girl(surface, x, y, moving):
    for row, line in enumerate(GIRL_SPRITE):
        for col, pixel in enumerate(line):
            if pixel in PALETTE:
                offset = (int(pygame.time.get_ticks() / 110) % 2) if moving and row >= 15 else 0
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
    if LEVEL_NUMBER == 4:
        surface.fill((208, 218, 230))
        for row in range(1, 7):
            for col in range(11):
                x, y = 28 + col * 24, 8 + row * 22
                walkable = (col, row) in ROBOT_PATH
                pygame.draw.rect(surface, (244, 231, 211) if walkable else (178, 168, 194), (x, y, 23, 21))
                if not walkable:
                    pygame.draw.rect(surface, (201, 187, 212), (x + 3, y + 3, 17, 3))
        gx, gy = robot_point((9, 4))
        pygame.draw.rect(surface, (156, 204, 177), (gx - 10, gy - 9, 20, 18))
        label(surface, small, "DOCK", gx - 9, gy - 2)
        for name, coin in world.coins.items():
            draw_coin(surface, coin, name in COLLECTED_COINS)
        x, y = robot_point(world.cell)
        pygame.draw.rect(surface, (113, 129, 163), (x - 6, y - 8, 12, 15))
        pygame.draw.rect(surface, (183, 217, 230), (x - 7, y - 9, 14, 9))
        pygame.draw.rect(surface, (76, 90, 124), (x - 4, y - 6, 2, 2))
        pygame.draw.rect(surface, (76, 90, 124), (x + 2, y - 6, 2, 2))
        pygame.draw.rect(surface, (255, 220, 148), (x, y - 13, 2, 4))
        label(surface, small, f"STEP {world.step}   HOLD SPACE TO STEP", 31, 163)
    else:
        pixel_cloud(surface, 19, 23)
        pixel_cloud(surface, 185, 18)
        if LEVEL_NUMBER == 3:
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
            for index, (name, color) in enumerate([("red", (240, 150, 164)), ("yellow", (255, 224, 132)), ("green", (156, 220, 172))]):
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
        else:
            pygame.draw.rect(surface, (211, 205, 228), (0, 65, WIDTH, 80))
            for x in range(8, WIDTH, 32):
                pygame.draw.rect(surface, (228, 217, 235), (x, 71, 23, 3))
            pygame.draw.rect(surface, (185, 212, 184), (0, FLOOR, WIDTH, 6))
            pygame.draw.rect(surface, (232, 199, 187), (0, FLOOR + 6, WIDTH, HEIGHT - FLOOR))
            for x in range(0, WIDTH, 16):
                pygame.draw.rect(surface, (245, 219, 197), (x + 4, 163, 3, 2))
            if LEVEL_NUMBER == 5:
                pygame.draw.rect(surface, (146, 130, 179), (53, 105, 38, 40))
                pygame.draw.rect(surface, (187, 219, 207), (57, 110, 30, 16))
                label(surface, small, f"{world.count:02} / 5", 60, 115)
                pygame.draw.rect(surface, (238, 176, 184), (64, 133, 15, 4))
                label(surface, small, "COLLECTOR", 50, 94)
                label(surface, small, "SPACE", 60, 154)
                label(surface, title, "FIVE, THEN STOP.", 110, 35)
                draw_door(surface, 288, world.exit_open, "EXIT", small, True)
            elif LEVEL_NUMBER == 6:
                pygame.draw.rect(surface, (145, 137, 172), (34, 115, 25, 30))
                pygame.draw.rect(surface, (183, 220, 201), (37, 119, 19, 12))
                label(surface, small, "STAR", 39, 121)
                label(surface, small, "PASS: STAR", 25, 99)
                for index, name in enumerate(("MOON", "LEAF", "STAR")):
                    draw_door(surface, 92 + 80 * index, world.opened == index, name, small, index == 2)
            else:
                pygame.draw.rect(surface, (143, 131, 173), (49, 111, 30, 34))
                pygame.draw.rect(surface, (190, 222, 211), (53, 115, 22, 14))
                label(surface, small, "SPACE", 52, 154)
                for index in range(3):
                    pygame.draw.rect(surface, (157, 206, 175) if world.power > index else (176, 163, 196), (110 + index * 35, 86, 22, 30))
                    pygame.draw.rect(surface, (211, 237, 201) if world.power > index else (205, 191, 220), (115 + index * 35, 90, 12, 19))
                label(surface, small, "POWER     LATCH     EXIT", 101, 60)
                draw_door(surface, 288, world.exit_open, "EXIT", small, True)
                label(surface, small, "UNLOCKED" if world.unlocked else "LOCKED", 244, 155)
            draw_girl(surface, world.x, world.y, False)
        for name, coin in world.coins.items():
            draw_coin(surface, coin, name in COLLECTED_COINS)
    label(surface, small, f"COINS {len(COLLECTED_COINS)}/{len(world.coins)}", 8, 6)
    if LEVEL_NUMBER != 4:
        label(surface, small, world.message[:67], 7, 172)


async def main():
    lesson_bridge.emit("loading", phase=4, label="Starting your game", fraction=None, loaded=0, total=0)
    pygame.init()
    screen = pygame.display.set_mode((800, 450))
    surface = pygame.Surface((WIDTH, HEIGHT))
    small, title = pygame.font.Font(None, 10), pygame.font.Font(None, 15)
    clock = pygame.time.Clock()
    world = World()
    COLLECTED_COINS.update(name for name in lesson_bridge.load_coins(LEVEL_NUMBER) if name in world.coins)
    state, attempt, has_input, previous_message = "idle", 0, False, ""
    lesson_bridge.ready()
    while True:
        dt = min(clock.tick(60) / 1000, 0.04)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        command = lesson_bridge.poll()
        if command:
            try:
                puzzle = lesson_bridge.compile_puzzle(command["body"], PUZZLE_NAME, PUZZLE_ARGUMENTS)
                candidate = World(puzzle)
                world = candidate
                state, has_input, previous_message = "playing", False, ""
                attempt += 1
                lesson_bridge.emit("started", attempt=attempt)
            except Exception as error:
                state = "idle"
                lesson_bridge.emit("error", message=str(error))
        if state == "playing":
            try:
                keys = pygame.key.get_pressed()
                left = bool(keys[pygame.K_LEFT] or keys[pygame.K_a])
                right = bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])
                action = bool(keys[pygame.K_SPACE])
                has_input = has_input or left or right or action
                result = world.update(dt, left, right, action, lesson_bridge.read_input())
                if world.message != previous_message:
                    previous_message = world.message
                    lesson_bridge.emit("notice", message=world.message)
                if result and (result != "won" or has_input):
                    state = result
                    lesson_bridge.emit(result, seconds=round(world.elapsed, 1), coins=sorted(COLLECTED_COINS))
            except Exception as error:
                state = "idle"
                lesson_bridge.emit("error", message=str(error))
        draw_scene(surface, world, small, title)
        pygame.transform.scale(surface, (800, 450), screen)
        pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())
