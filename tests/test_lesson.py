"""Regression checks for the actual Pygame physics, hazards, and win trigger."""
import ast
from collections import defaultdict
import json
import os
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

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

    def test_gap_is_half_the_default_running_jump(self):
        game["on_blue"] = lesson_bridge.compile_solution("    pass\n")
        girl = game["Girl"]()
        girl.x = 70.0
        start = girl.x
        girl.jump()
        controls = defaultdict(bool, {pygame.K_RIGHT: True})
        for _ in range(300):
            self.assertIsNone(game["update"](girl, 1 / 180, controls))
            if girl.grounded:
                break
        self.assertTrue(girl.grounded)
        self.assertAlmostEqual(game["GAP"].width, (girl.x - start) / 2, delta=0.5)

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

    def test_level_one_does_not_land_on_the_spike_platform(self):
        girl = game["Girl"]()
        girl.x, girl.y, girl.vy, girl.grounded = 220, 70, 120, False
        for _ in range(4):
            self.assertIsNone(game["update"](girl, 1 / 60, defaultdict(bool)))
        self.assertGreater(girl.y, game["SPIKE_PLATFORM"].top)
        self.assertFalse(girl.grounded)

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
        for name in ("WIDTH", "HEIGHT", "FLOOR", "BLUE", "SPIKES", "SPIKE_PLATFORM", "GAP", "GOAL", "SPAWN_X"):
            self.assertEqual(self.game[name], game[name], name)
        self.assertLess(self.game["GAP"].right, self.game["BLUE"].left)
        self.assertGreater(self.game["GAP"].left, self.game["GOAL"].right)

    def test_starter_hits_original_overhead_spikes(self):
        _, result, _ = self.simulate(-178)
        self.assertEqual(result, "dead")

    def test_small_jumps_can_pass_under_spikes(self):
        for velocity in (-70, -80):
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

    def platform_girl(self):
        girl = lesson_bridge.compile_girl(self.body, self.game["SPAWN_X"], self.game["FLOOR"])()
        girl.x, girl.y, girl.vy, girl.grounded = 228, float(self.game["SPIKE_PLATFORM"].top), 0.0, True
        return girl

    def test_lands_on_top_and_stays_still_above_blue(self):
        for velocity in (75, 10000):
            with self.subTest(velocity=velocity):
                girl = self.platform_girl()
                girl.y, girl.vy, girl.grounded = 60, velocity, False
                for _ in range(120):
                    self.assertIsNone(self.game["update"](girl, 1 / 60, defaultdict(bool)))
                self.assertEqual(girl.y, self.game["SPIKE_PLATFORM"].top)
                self.assertEqual(girl.vy, 0)
                self.assertTrue(girl.grounded)
                self.assertFalse(self.game["touching_blue"](girl))

    def test_can_walk_both_ways_on_the_platform(self):
        for key, direction in ((pygame.K_LEFT, -1), (pygame.K_RIGHT, 1)):
            with self.subTest(direction=direction):
                girl = self.platform_girl()
                initial_x = girl.x
                controls = defaultdict(bool, {key: True})
                for _ in range(20):
                    self.assertIsNone(self.game["update"](girl, 1 / 60, controls))
                    self.assertTrue(girl.grounded)
                    self.assertEqual(girl.y, self.game["SPIKE_PLATFORM"].top)
                self.assertGreater((girl.x - initial_x) * direction, 15)

    def test_manual_jump_from_spawn_can_land_on_the_platform(self):
        source = self.body.replace("self.vy = -178", "self.vy = -300")
        girl = lesson_bridge.compile_girl(source, self.game["SPAWN_X"], self.game["FLOOR"])()
        controls = defaultdict(bool, {pygame.K_LEFT: True, pygame.K_SPACE: True})
        for _ in range(90):
            self.assertIsNone(self.game["update"](girl, 1 / 60, controls))
            controls[pygame.K_SPACE] = False
        self.assertEqual(girl.y, self.game["SPIKE_PLATFORM"].top)
        self.assertTrue(girl.grounded)

    def test_can_jump_from_the_platform(self):
        girl = self.platform_girl()
        controls = defaultdict(bool, {pygame.K_SPACE: True})
        self.assertIsNone(self.game["update"](girl, 1 / 60, controls))
        self.assertLess(girl.y, self.game["SPIKE_PLATFORM"].top)
        self.assertLess(girl.vy, 0)
        self.assertFalse(girl.grounded)

    def test_walking_off_platform_falls_back_to_floor(self):
        girl = self.platform_girl()
        girl.x = self.game["SPIKE_PLATFORM"].left - 2
        controls = defaultdict(bool, {pygame.K_LEFT: True})
        for _ in range(6):
            self.assertIsNone(self.game["update"](girl, 1 / 60, controls))
        self.assertGreater(girl.y, self.game["SPIKE_PLATFORM"].top)
        self.assertFalse(girl.grounded)
        for _ in range(28):
            self.assertIsNone(self.game["update"](girl, 1 / 60, controls))
        self.assertEqual(girl.y, self.game["FLOOR"])
        self.assertTrue(girl.grounded)

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


class CoinTests(unittest.TestCase):
    def setUp(self):
        self.worlds = {}
        for number, slug in ((1, "jumping-girl"), (2, "blue-leap")):
            tree = ast.parse((ROOT / "public" / "levels" / f"{slug}.py").read_text(encoding="utf-8"))
            tree.body.pop()
            world = {}
            exec(compile(tree, slug, "exec"), world)
            self.worlds[number] = world

    def test_coins_are_above_and_below_the_spikes(self):
        self.assertEqual(set(self.worlds[1]["COINS"]), {"below"})
        self.assertEqual(set(self.worlds[2]["COINS"]), {"above", "below"})
        for world in self.worlds.values():
            coin = world["COINS"]["below"]
            self.assertGreater(coin.top, max(spike.bottom for spike in world["SPIKES"]))
            self.assertLess(coin.bottom, world["FLOOR"])
            self.assertTrue(world["BLUE"].left <= coin.centerx <= world["BLUE"].right)
        self.assertLess(self.worlds[2]["COINS"]["above"].bottom, self.worlds[2]["SPIKE_PLATFORM"].top)

    def test_only_touched_coins_are_collected_and_levels_are_independent(self):
        for world in self.worlds.values():
            girl = world["Girl"]()
            world["collect_coins"](girl)
            self.assertFalse(world["COLLECTED_COINS"])
        first, second = self.worlds[1], self.worlds[2]
        girl = first["Girl"]()
        girl.x = first["COINS"]["below"].centerx
        first["collect_coins"](girl)
        self.assertEqual(first["COLLECTED_COINS"], {"below"})
        self.assertFalse(second["COLLECTED_COINS"])
        girl = second["Girl"]()
        girl.x, girl.y = second["COINS"]["above"].centerx, second["SPIKE_PLATFORM"].top
        second["collect_coins"](girl)
        self.assertEqual(second["COLLECTED_COINS"], {"above"})
        girl.y = second["FLOOR"]
        second["collect_coins"](girl)
        self.assertEqual(second["COLLECTED_COINS"], {"above", "below"})

    def test_touching_an_outline_does_not_collect_it_twice(self):
        world = self.worlds[1]
        girl = world["Girl"]()
        girl.x = world["COINS"]["below"].centerx
        with patch.object(lesson_bridge, "save_coins") as save:
            world["collect_coins"](girl)
            world["collect_coins"](girl)
        save.assert_called_once_with(1, {"below"})

    def test_collected_coin_remains_after_falling_and_restarting(self):
        world = self.worlds[1]
        world["on_blue"] = lesson_bridge.compile_solution("    pass\n")
        girl = world["Girl"]()
        controls = defaultdict(bool, {pygame.K_LEFT: True})
        for _ in range(400):
            result = world["update"](girl, 1 / 60, controls)
            if result:
                break
        self.assertEqual(result, "dead")
        self.assertEqual(world["COLLECTED_COINS"], {"below"})
        girl = world["Girl"]()
        self.assertEqual(world["COLLECTED_COINS"], {"below"})

    def test_collected_sprite_has_an_empty_center_and_visible_outline(self):
        world = self.worlds[1]
        coin = world["COINS"]["below"]
        surface = pygame.Surface((world["WIDTH"], world["HEIGHT"]))
        background = (10, 20, 30)
        surface.fill(background)
        world["draw_coin"](surface, coin, False)
        self.assertEqual(tuple(surface.get_at((coin.x + 3, coin.y + 3)))[:3], (255, 242, 179))
        surface.fill(background)
        world["draw_coin"](surface, coin, True)
        self.assertEqual(tuple(surface.get_at((coin.x + 3, coin.y + 3)))[:3], background)
        self.assertEqual(tuple(surface.get_at((coin.x + 2, coin.y)))[:3], (174, 146, 98))

    def test_bridge_restores_saved_coins_and_saves_them_by_level(self):
        window = SimpleNamespace(lessonReadCoins=Mock(return_value='["below", "above", 42]'), lessonSaveCoins=Mock())
        with patch.object(lesson_bridge, "browser", return_value=window):
            self.assertEqual(lesson_bridge.load_coins(2), ["below", "above"])
            lesson_bridge.save_coins(2, {"below", "above"})
        window.lessonReadCoins.assert_called_once_with(2)
        level, saved = window.lessonSaveCoins.call_args.args
        self.assertEqual(level, 2)
        self.assertEqual(json.loads(saved), ["above", "below"])

    def test_missing_or_corrupt_coin_storage_does_not_break_loading(self):
        for raw in ("", "{broken", "null", '{"below": true}', "42"):
            with self.subTest(raw=raw), patch.object(lesson_bridge, "browser", return_value=SimpleNamespace(lessonReadCoins=lambda _: raw)):
                self.assertEqual(lesson_bridge.load_coins(1), [])
        with patch.object(lesson_bridge, "browser", return_value=SimpleNamespace(lessonReadCoins=Mock(side_effect=RuntimeError))):
            self.assertEqual(lesson_bridge.load_coins(1), [])


if __name__ == "__main__":
    unittest.main()
