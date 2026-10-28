"""Level 1: The Jumping Girl. Explore the game, then fix on_blue()."""
import asyncio
import math
import pygame
import lesson_bridge

WIDTH, HEIGHT = 800, 440
FLOOR = 340
BLUE = pygame.Rect(490, FLOOR, 160, 16)
GOAL_X = 145


class Girl:
    def __init__(self, x=570):
        self.x, self.y = float(x), float(FLOOR)
        self.vx, self.vy = 0.0, 0.0
        self.grounded = True
        self.jumps = 0

    def jump(self):
        if self.grounded:
            self.vy = -360
            self.grounded = False
            self.jumps += 1

    def move_left(self):
        self.vx = -150

    def move_right(self):
        self.vx = 150

    def stop(self):
        self.vx = 0


def on_blue(player):
    # EDIT START: fix the action below
    player.jump()
    # EDIT END


def touching_blue(player):
    return BLUE.left <= player.x <= BLUE.right and player.grounded


def update(player, dt, keys, mode):
    # You can explore with the keyboard. Tests run without keyboard input.
    if mode == "play":
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.move_left()
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.move_right()
        else:
            player.stop()
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            player.jump()

    if touching_blue(player):
        on_blue(player)

    player.vy += 980 * dt
    player.x = max(30, min(WIDTH - 30, player.x + player.vx * dt))
    player.y += player.vy * dt
    if player.y >= FLOOR:
        player.y, player.vy, player.grounded = float(FLOOR), 0.0, True


def cloud(screen, x, y, scale=1):
    color = (255, 254, 245)
    for dx, dy, radius in [(-25, 8, 19), (0, -2, 28), (28, 8, 20)]:
        pygame.draw.circle(screen, color, (int(x + dx * scale), int(y + dy * scale)), int(radius * scale))
    pygame.draw.rect(screen, color, (x - 26 * scale, y + 7 * scale, 55 * scale, 20 * scale))


def draw_girl(screen, player, time):
    x, y = int(player.x), int(player.y)
    walking = abs(player.vx) > 0 and player.grounded
    swing = int(math.sin(time * 14) * 6) if walking else 0
    # Shadow, shoes, legs, dress, arms, hair, face, and a tiny hair ribbon.
    pygame.draw.ellipse(screen, (175, 181, 125), (x - 18, FLOOR - 3, 36, 8))
    pygame.draw.line(screen, (228, 170, 132), (x - 5, y - 18), (x - 7 - swing, y - 3), 6)
    pygame.draw.line(screen, (228, 170, 132), (x + 5, y - 18), (x + 7 + swing, y - 3), 6)
    pygame.draw.ellipse(screen, (62, 52, 64), (x - 14 - swing, y - 6, 12, 7))
    pygame.draw.ellipse(screen, (62, 52, 64), (x + 3 + swing, y - 6, 12, 7))
    pygame.draw.polygon(screen, (228, 109, 84), [(x - 9, y - 45), (x + 9, y - 45), (x + 17, y - 16), (x - 17, y - 16)])
    pygame.draw.line(screen, (228, 170, 132), (x - 10, y - 40), (x - 19, y - 26 - swing), 5)
    pygame.draw.line(screen, (228, 170, 132), (x + 10, y - 40), (x + 19, y - 26 + swing), 5)
    pygame.draw.ellipse(screen, (71, 54, 53), (x - 15, y - 78, 31, 38))
    pygame.draw.circle(screen, (239, 186, 145), (x, y - 59), 13)
    pygame.draw.ellipse(screen, (71, 54, 53), (x - 14, y - 77, 28, 16))
    pygame.draw.circle(screen, (71, 54, 53), (x + 18, y - 66), 8)
    pygame.draw.polygon(screen, (235, 161, 64), [(x + 10, y - 72), (x + 20, y - 78), (x + 20, y - 65)])
    pygame.draw.circle(screen, (54, 47, 52), (x - 5, y - 59), 2)
    pygame.draw.circle(screen, (54, 47, 52), (x + 4, y - 59), 2)
    pygame.draw.arc(screen, (150, 89, 78), (x - 4, y - 56, 8, 5), 3.3, 6.0, 1)


def draw_scene(screen, player, time, font, small):
    screen.fill((232, 241, 227))
    pygame.draw.circle(screen, (249, 215, 126), (663, 74), 33)
    cloud(screen, 150, 72)
    cloud(screen, 415, 109, .7)
    pygame.draw.ellipse(screen, (208, 223, 186), (-140, 182, 680, 340))
    pygame.draw.ellipse(screen, (194, 215, 176), (330, 186, 680, 340))
    pygame.draw.ellipse(screen, (174, 201, 153), (-240, 260, 740, 260))
    # A little forest on the horizon.
    for tx, ty in [(68, 247), (740, 242), (780, 270)]:
        pygame.draw.rect(screen, (135, 136, 99), (tx - 4, ty, 8, 60))
        pygame.draw.circle(screen, (135, 169, 125), (tx, ty), 24)
        pygame.draw.circle(screen, (151, 184, 137), (tx - 8, ty - 12), 20)
    pygame.draw.rect(screen, (219, 202, 164), (0, FLOOR + 12, WIDTH, HEIGHT - FLOOR))
    pygame.draw.rect(screen, (143, 165, 106), (0, FLOOR, WIDTH, 13))
    pygame.draw.rect(screen, (100, 169, 218), BLUE, border_radius=4)
    for i in range(8):
        pygame.draw.circle(screen, (169, 208, 234), (503 + i * 19, FLOOR + 7), 2)
    # The destination flag is left of the blue platform.
    pygame.draw.ellipse(screen, (169, 177, 119), (GOAL_X - 30, FLOOR - 3, 60, 9))
    pygame.draw.line(screen, (95, 111, 83), (GOAL_X, FLOOR), (GOAL_X, FLOOR - 112), 4)
    wave = int(math.sin(time * 3) * 3)
    pygame.draw.polygon(screen, (224, 117, 82), [(GOAL_X + 2, FLOOR - 111), (GOAL_X + 49, FLOOR - 104 + wave), (GOAL_X + 40, FLOOR - 79 + wave), (GOAL_X + 2, FLOOR - 84)])
    pygame.draw.circle(screen, (250, 226, 183), (GOAL_X, FLOOR - 114), 4)
    # Hand-painted flowers and pebbles along the path.
    for fx in [35, 85, 236, 315, 378, 704, 766]:
        pygame.draw.line(screen, (119, 145, 92), (fx, FLOOR), (fx, FLOOR - 10), 2)
        pygame.draw.circle(screen, (247, 231, 173), (fx, FLOOR - 12), 4)
    for px in [56, 200, 260, 410, 680, 750]:
        pygame.draw.ellipse(screen, (204, 187, 150), (px, FLOOR + 44, 10, 4))
    draw_girl(screen, player, time)
    goal_label = small.render("THE GOAL", True, (84, 106, 75))
    screen.blit(goal_label, (GOAL_X - goal_label.get_width() // 2, FLOOR + 25))
    tile_label = small.render("BLUE PLATFORM", True, (71, 119, 153))
    screen.blit(tile_label, (570 - tile_label.get_width() // 2, FLOOR + 25))


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Jumping Girl")
    font = pygame.font.Font(None, 28)
    small = pygame.font.Font(None, 19)
    clock = pygame.time.Clock()
    player = Girl()
    mode, elapsed, outcome = "play", 0.0, None
    lesson_bridge.ready()

    while True:
        dt = min(clock.tick(60) / 1000, 0.04)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        command = lesson_bridge.poll()
        if command:
            try:
                handler = lesson_bridge.compile_solution(command["body"])
                globals()["on_blue"] = handler
                mode = command.get("mode", "test")
                player = Girl(710 if mode == "play" else 570)
                elapsed, outcome = 0.0, None
                lesson_bridge.emit("started", mode=mode)
            except Exception as error:
                lesson_bridge.emit("error", message=str(error))
                mode = "paused"

        if mode != "paused":
            try:
                update(player, dt, pygame.key.get_pressed(), mode)
                elapsed += dt
                if outcome is None and player.x <= GOAL_X + 18:
                    if mode == "test" and player.jumps == 0:
                        outcome = "won"
                        lesson_bridge.emit("won", seconds=round(elapsed, 1))
                        mode = "paused"
                    elif mode == "test":
                        outcome = "failed"
                        lesson_bridge.emit("failed", message="She reached the flag, but still jumped. Make her move left without jumping on blue.")
                        mode = "paused"
                    else:
                        outcome = "explored"
                        lesson_bridge.emit("explored")
                if mode == "test" and elapsed >= 6 and outcome is None:
                    outcome = "failed"
                    lesson_bridge.emit("failed", message="She is still jumping!" if player.jumps else "She did not reach the flag. Which action moves her left?")
                    mode = "paused"
            except Exception as error:
                lesson_bridge.emit("error", message=str(error))
                mode = "paused"

        draw_scene(screen, player, pygame.time.get_ticks() / 1000, font, small)
        pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())
