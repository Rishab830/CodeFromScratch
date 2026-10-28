"""Regression checks for the actual Pygame physics, hazards, and win trigger."""
import ast
from collections import defaultdict
import os
from pathlib import Path
import sys
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "game"))
import lesson_bridge
import pygame

tree = ast.parse((ROOT / "game" / "main.py").read_text(encoding="utf-8"))
tree.body.pop()  # Import definitions without starting the browser's event loop.
game = {}
exec(compile(tree, "main.py", "exec"), game)


class LessonTests(unittest.TestCase):
    def simulate(self, body, keys=(), seconds=10):
        game["on_blue"] = lesson_bridge.compile_solution(body)
        girl = game["Girl"]()
        controls = defaultdict(bool, {key: True for key in keys})
        for _ in range(int(seconds * 60)):
            result = game["update"](girl, 1 / 60, controls)
            if result:
                return girl, result
        return girl, None

    def test_compiling_without_playing_never_wins(self):
        for body in ["    player.jump()\n", "    player.move_left()\n", "    pass\n"]:
            with self.subTest(body=body):
                girl, result = self.simulate(body)
                self.assertIsNone(result)
                self.assertEqual(girl.x, game["SPAWN_X"])

    def test_starter_walks_into_blue_then_hits_spikes(self):
        girl, result = self.simulate("    player.jump()\n", [pygame.K_LEFT])
        self.assertEqual(result, "dead")
        self.assertGreater(girl.x, game["BLUE"].left)

    def test_move_left_solution_wins_by_manual_play(self):
        _, result = self.simulate("    player.move_left()\n", [pygame.K_LEFT])
        self.assertEqual(result, "won")

    def test_alternative_pass_solution_is_accepted(self):
        _, result = self.simulate("    pass\n", [pygame.K_LEFT])
        self.assertEqual(result, "won")

    def test_jump_on_safe_ground_does_not_disqualify_win(self):
        game["on_blue"] = lesson_bridge.compile_solution("    pass\n")
        girl = game["Girl"]()
        girl.x = 110
        girl.jump()
        keys = defaultdict(bool, {pygame.K_LEFT: True})
        result = None
        for _ in range(300):
            result = game["update"](girl, 1 / 60, keys)
            if result:
                break
        self.assertEqual(result, "won")

    def test_empty_corners_of_spikes_are_safe(self):
        triangle = [(0, 0), (8, 0), (4, 17)]
        self.assertFalse(game["triangle_hits_rect"](triangle, pygame.Rect(0, 13, 1, 2)))
        self.assertTrue(game["triangle_hits_rect"](triangle, pygame.Rect(3, 10, 2, 4)))

    def test_python_errors_and_unbounded_code_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Python syntax error"):
            lesson_bridge.compile_solution("    player.move_left(\n")
        for source in ["    while True: pass\n", "    import os\n", "    player.__class__()\n", "    player.x = 0\n"]:
            with self.subTest(source=source), self.assertRaises(ValueError):
                lesson_bridge.compile_solution(source)


if __name__ == "__main__":
    unittest.main()
