"""Play the later worlds with their broken programs and real compiled fixes."""
import ast
import os
from pathlib import Path
import sys
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "game"))
sys.path.insert(0, str(ROOT / "scripts"))
import lesson_bridge
import pygame
from puzzles import PUZZLES

ROUTE = ["right", "right", "up", "up", "right", "right", "down", "right", "right", "down", "right", "right"]
FIXES = {
    3: '    return {"red": "green", "green": "yellow", "yellow": "red"}[current]\n',
    4: f'    return {ROUTE!r}\n',
    5: '    return count < 5\n',
    6: '    if password == "STAR":\n        return 2\n    return None\n',
    7: '    steps = []\n    for cell in range(3):\n        steps.append("power")\n    if len(steps) == 3:\n        steps.append("unlock")\n        steps.append("open")\n    return steps\n',
}


class PuzzleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds = {}
        for number, (slug, _, _, _) in PUZZLES.items():
            source = (ROOT / "public" / "levels" / f"{slug}.py").read_text(encoding="utf-8")
            tree = ast.parse(source)
            tree.body.pop()
            namespace = {}
            exec(compile(tree, slug, "exec"), namespace)
            cls.worlds[number] = namespace
        pygame.init()

    def world(self, number, fixed=False):
        namespace = self.worlds[number]
        namespace["COLLECTED_COINS"].clear()
        if fixed:
            _, name, arguments, _ = PUZZLES[number]
            return namespace["World"](lesson_bridge.compile_puzzle(FIXES[number], name, arguments))
        return namespace["World"]()

    def run_for(self, world, seconds, **controls):
        for _ in range(round(seconds * 60)):
            result = world.update(1 / 60, **controls)
            if result:
                return result
        return None

    def test_all_starters_have_exactly_one_editable_body_and_draw(self):
        for number, (slug, _, _, _) in PUZZLES.items():
            with self.subTest(level=number):
                source = (ROOT / "public" / "levels" / f"{slug}.py").read_text(encoding="utf-8")
                self.assertEqual(source.count("# EDIT START"), 1)
                self.assertEqual(source.count("# EDIT END"), 1)
                namespace = self.worlds[number]
                world = self.world(number)
                surface = pygame.Surface((320, 180))
                namespace["draw_scene"](surface, world, pygame.font.Font(None, 10), pygame.font.Font(None, 15))

    def test_compile_and_wait_cannot_clear_any_world(self):
        for number in PUZZLES:
            with self.subTest(level=number):
                world = self.world(number, True)
                self.assertIsNone(self.run_for(world, 12))

    def test_broken_signal_never_allows_car_past_stop_line(self):
        world = self.world(3)
        self.assertIsNone(self.run_for(world, 10, right=True))
        self.assertEqual(world.x, 119)
        self.assertNotEqual(world.light, "green")

    def test_correct_signal_and_alternative_sequence_both_allow_manual_finish(self):
        world = self.world(3, True)
        self.assertEqual(self.run_for(world, 8, right=True), "won")
        world = self.worlds[3]["World"](lesson_bridge.compile_puzzle('    return "green"\n', "next_light", "current"))
        self.assertEqual(self.run_for(world, 8, right=True), "won")

    def test_robot_starter_repeats_a_circle(self):
        world = self.world(4)
        for _ in range(4):
            self.assertIsNone(world.update(0.25, action=True))
        self.assertEqual(world.cell, (1, 4))

    def test_robot_follows_fixed_route_and_accepts_optional_detour(self):
        world = self.world(4, True)
        self.assertEqual(self.run_for(world, 5, action=True), "won")
        route = ["right", "down", "left", "up"] + ROUTE
        world = self.worlds[4]["World"](lesson_bridge.compile_puzzle(f'    return {route!r}\n', "robot_program", ""))
        self.assertEqual(self.run_for(world, 7, action=True), "won")
        self.assertEqual(self.worlds[4]["COLLECTED_COINS"], {"loop", "route"})

    def test_robot_crate_collision_ends_attempt(self):
        world = self.worlds[4]["World"](lambda: ["up"])
        self.assertEqual(world.update(0.25, action=True), "dead")

    def test_broken_collector_runs_past_five_and_door_stays_locked(self):
        world = self.world(5)
        world.x = 72
        world.update(0.01, action=True)
        self.assertIsNone(self.run_for(world, 4))
        self.assertGreater(world.count, 5)
        self.assertTrue(world.processing)
        self.assertFalse(world.exit_open)
        self.assertIsNone(self.run_for(world, 5, right=True))

    def test_fixed_collector_stops_at_five_but_requires_walking_to_exit(self):
        world = self.world(5, True)
        world.x = 72
        world.update(0.01, action=True)
        self.assertIsNone(self.run_for(world, 4))
        self.assertEqual(world.count, 5)
        self.assertFalse(world.processing)
        self.assertTrue(world.exit_open)
        self.assertEqual(self.run_for(world, 5, right=True), "won")

    def test_door_starter_opens_wrong_door_and_correct_password_cannot_win(self):
        world = self.world(6)
        world.update(0.01, action=True, password="STAR")
        self.assertEqual(world.opened, 0)
        self.assertEqual(self.run_for(world, 4, right=True), "dead")

    def test_fixed_door_rejects_bad_password_then_opens_correct_exit(self):
        world = self.world(6, True)
        world.update(0.01, action=True, password="WRONG")
        self.assertIsNone(world.opened)
        world.update(0.3, action=True, password="STAR")
        self.assertEqual(world.opened, 2)
        self.assertEqual(self.run_for(world, 5, right=True), "won")

    def test_escape_starter_and_wrong_order_both_leave_exit_locked(self):
        for fixed_order in (False, True):
            world = self.world(7)
            if fixed_order:
                world.sequence = ["power", "power", "power", "open", "unlock"]
            world.x = 64
            world.update(0.01, action=True)
            self.assertIsNone(self.run_for(world, 3))
            self.assertFalse(world.exit_open)
            self.assertIsNone(self.run_for(world, 5, right=True))

    def test_escape_loop_condition_sequence_and_manual_exit(self):
        world = self.world(7, True)
        world.x = 64
        world.update(0.01, action=True)
        self.assertIsNone(self.run_for(world, 3))
        self.assertEqual(world.power, 3)
        self.assertTrue(world.unlocked)
        self.assertTrue(world.exit_open)
        self.assertEqual(self.run_for(world, 5, right=True), "won")

    def test_unbounded_loops_and_runtime_access_are_rejected(self):
        previous = sys.gettrace()
        for source in ['    while True:\n        pass\n', '    return list(range(999))\n', '    import os\n', '    return ().__class__\n']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                lesson_bridge.compile_puzzle(source, "escape_plan", "")()
            self.assertIs(sys.gettrace(), previous)


if __name__ == "__main__":
    unittest.main()
