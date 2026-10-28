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
    def simulate(self, body, keys=(), seconds=10, jump_gap=False):
        game["on_blue"] = lesson_bridge.compile_solution(body)
        girl = game["Girl"]()
        controls = defaultdict(bool, {key: True for key in keys})
        jumped = False
        for _ in range(int(seconds * 60)):
            controls[pygame.K_SPACE] = False
            if jump_gap and not jumped and girl.x <= game["GAP"].right - 1:
                controls[pygame.K_SPACE] = True
                jumped = True
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
        _, result = self.simulate("    player.move_left()\n", [pygame.K_LEFT], jump_gap=True)
        self.assertEqual(result, "won")

    def test_alternative_pass_solution_is_accepted(self):
        _, result = self.simulate("    pass\n", [pygame.K_LEFT], jump_gap=True)
        self.assertEqual(result, "won")

    def test_walking_into_gap_falls_instead_of_winning(self):
        girl, result = self.simulate("    pass\n", [pygame.K_LEFT])
        self.assertEqual(result, "dead")
        self.assertGreater(girl.y, game["HEIGHT"])

    def test_falling_cannot_jump_or_snap_back_onto_floor(self):
        game["on_blue"] = lesson_bridge.compile_solution("    pass\n")
        girl = game["Girl"]()
        girl.x = game["GAP"].centerx
        no_keys = defaultdict(bool)
        game["update"](girl, 1 / 60, no_keys)
        self.assertFalse(girl.grounded)
        self.assertGreater(girl.y, game["FLOOR"])
        girl.jump()
        self.assertGreater(girl.vy, 0)
        # Even leaving the hole horizontally cannot pull her up through dirt.
        girl.x = game["GAP"].left - 5
        game["update"](girl, 1 / 60, no_keys)
        self.assertGreater(girl.y, game["FLOOR"])
        self.assertFalse(girl.grounded)

    def test_gap_can_be_jumped_in_both_directions(self):
        game["on_blue"] = lesson_bridge.compile_solution("    pass\n")
        for direction in (-1, 1):
            with self.subTest(direction=direction):
                girl = game["Girl"]()
                girl.x = game["GAP"].right + 2 if direction == -1 else game["GAP"].left - 2
                girl.jump()
                key = pygame.K_LEFT if direction == -1 else pygame.K_RIGHT
                controls = defaultdict(bool, {key: True})
                for _ in range(50):
                    self.assertIsNone(game["update"](girl, 1 / 60, controls))
                self.assertTrue(girl.grounded)
                self.assertEqual(girl.y, game["FLOOR"])
                self.assertTrue(girl.x < game["GAP"].left if direction == -1 else girl.x > game["GAP"].right)

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
        cls.source = (ROOT / "public" / "levels" / "blue-leap.py").read_text(encoding="utf-8")
        tree = ast.parse(cls.source)
        tree.body.pop()
        cls.game = {}
        exec(compile(tree, "blue-leap.py", "exec"), cls.game)
        cls.body = cls.source.split(lesson_bridge.EDIT_START)[1].split(lesson_bridge.EDIT_END)[0]

    def simulate(self, velocity, moving=True, early_jump=False, jump_gap=True):
        source = self.body.replace("self.vy = -178", f"self.vy = {velocity}")
        self.game["Girl"] = lesson_bridge.compile_girl(source, self.game["SPAWN_X"], self.game["FLOOR"])
        girl = self.game["Girl"]()
        minimum_y, jumped, crossed = girl.y, False, False
        for _ in range(700):
            controls = defaultdict(bool, {pygame.K_LEFT: moving})
            if early_jump and not jumped and girl.x <= 279:
                controls[pygame.K_SPACE] = True
                jumped = True
            if jump_gap and not crossed and girl.grounded and girl.x <= self.game["GAP"].right - 1:
                controls[pygame.K_SPACE] = True
                crossed = True
            result = self.game["update"](girl, 1 / 60, controls)
            minimum_y = min(minimum_y, girl.y)
            if result:
                return girl, result, minimum_y
        return girl, None, minimum_y

    def test_whole_class_is_editable_and_configure_is_gone(self):
        self.assertTrue(self.body.startswith("class Girl:"))
        tree = ast.parse(self.body)
        self.assertEqual(len(tree.body), 1)
        self.assertIsInstance(tree.body[0], ast.ClassDef)
        self.assertIn("def __init__", self.body)
        self.assertIn("def stop", self.body)
        self.assertNotIn("configure", self.source)
        self.assertIn("def on_blue(player):\n    player.jump()", self.source)
        self.assertNotIn("def on_blue", self.body)

    def test_map_is_identical_to_level_one(self):
        for name in ("WIDTH", "HEIGHT", "FLOOR", "BLUE", "SPIKES", "GAP", "GOAL", "SPAWN_X"):
            self.assertEqual(self.game[name], game[name], name)
        self.assertLess(self.game["GAP"].right, self.game["BLUE"].left)
        self.assertGreater(self.game["GAP"].left, self.game["GOAL"].right)

    def test_starter_hits_original_overhead_spikes(self):
        _, result, _ = self.simulate(-178)
        self.assertEqual(result, "dead")

    def test_small_jumps_can_pass_under_spikes(self):
        for velocity in (-40, -80):
            with self.subTest(velocity=velocity):
                _, result, minimum_y = self.simulate(velocity)
                self.assertEqual(result, "won")
                self.assertLess(minimum_y, self.game["FLOOR"])
                self.assertGreater(minimum_y - 20, 100)

    def test_high_jumps_can_clear_over_spikes(self):
        for velocity in (-420, -450):
            with self.subTest(velocity=velocity):
                _, result, minimum_y = self.simulate(velocity, early_jump=True)
                self.assertEqual(result, "won")
                self.assertLess(minimum_y, 76)

    def test_small_jump_solution_still_needs_to_jump_the_gap(self):
        girl, result, _ = self.simulate(-40, jump_gap=False)
        self.assertEqual(result, "dead")
        self.assertGreater(girl.y, self.game["HEIGHT"])

    def test_other_class_methods_and_constructor_are_editable(self):
        body = self.body.replace("float(SPAWN_X)", "float(SPAWN_X - 1)").replace("self.vx = -55", "self.vx = -70").replace("self.vx = 55", "self.vx = 75")
        girl = lesson_bridge.compile_girl(body, 289, 141)()
        self.assertEqual(girl.x, 288)
        girl.move_left()
        self.assertEqual(girl.vx, -70)
        girl.move_right()
        self.assertEqual(girl.vx, 75)
        girl.stop()
        self.assertEqual(girl.vx, 0)

    def test_compile_still_requires_manual_movement(self):
        girl, result, _ = self.simulate(-40, moving=False)
        self.assertIsNone(result)
        self.assertEqual(girl.x, self.game["SPAWN_X"])

    def test_invalid_class_and_world_mutations_are_rejected(self):
        for source in ["pass\n", self.body + "\ndef on_blue(player): pass\n", self.body.replace("self.vy = -178", "while True: pass"), self.body.replace("self.vy = -178", "self.vy = __import__('os')")]:
            with self.subTest(source=source), self.assertRaises(ValueError):
                lesson_bridge.compile_girl(source, 289, 141)

    def test_recursive_method_is_bounded_and_restores_tracing(self):
        source = self.body.replace("self.vy = -178", "self.jump()")
        girl = lesson_bridge.compile_girl(source, 289, 141)()
        previous_trace = sys.gettrace()
        with self.assertRaises((ValueError, RecursionError)):
            girl.jump()
        self.assertIs(sys.gettrace(), previous_trace)


if __name__ == "__main__":
    unittest.main()
