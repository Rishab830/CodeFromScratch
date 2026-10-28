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


class BlueLeapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = (ROOT / "public" / "levels" / "blue-leap.py").read_text(encoding="utf-8")
        cls.source = source
        tree = ast.parse(source)
        tree.body.pop()
        cls.game = {}
        exec(compile(tree, "blue-leap.py", "exec"), cls.game)

    def simulate(self, value, keys=(), seconds=12):
        self.game["configure"] = lesson_bridge.compile_settings(f"    return {value}\n")
        girl = self.game["Girl"]()
        controls = defaultdict(bool, {key: True for key in keys})
        for _ in range(int(seconds * 60)):
            result = self.game["update"](girl, 1 / 60, controls)
            if result:
                return girl, result
        return girl, None

    def test_blue_action_is_outside_the_only_editable_region(self):
        body = self.source.split(lesson_bridge.EDIT_START)[1].split(lesson_bridge.EDIT_END)[0]
        self.assertEqual(body, "    return -110\n")
        self.assertIn("def on_blue(player):\n    player.jump()", self.source)
        self.assertEqual(self.source.count(lesson_bridge.EDIT_START), 1)

    def test_starter_jumps_but_falls_into_gap(self):
        girl, result = self.simulate(-110, [pygame.K_LEFT])
        self.assertEqual(result, "dead")
        self.assertGreater(girl.y, self.game["FLOOR"])
        self.assertGreater(girl.x, self.game["GAP"][0])

    def test_multiple_adjustments_allow_manual_completion(self):
        for value in [-300, -320]:
            with self.subTest(value=value):
                _, result = self.simulate(value, [pygame.K_LEFT])
                self.assertEqual(result, "won")

    def test_adjusting_and_compiling_cannot_win_without_play(self):
        girl, result = self.simulate(-300)
        self.assertIsNone(result)
        self.assertEqual(girl.x, self.game["SPAWN_X"])

    def test_settings_cannot_disable_or_replace_locked_jump(self):
        for body in ["    pass\n", "    player.jump()\n", "    return 0\n", "    return -300\n\ndef on_blue(player): pass\n", "    return -1e999\n"]:
            with self.subTest(body=body), self.assertRaises(ValueError):
                lesson_bridge.compile_settings(body)


if __name__ == "__main__":
    unittest.main()
