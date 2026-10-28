"""Exercise actual Pygame physics and dynamically compiled student Python."""
import ast
import os
from pathlib import Path
import sys
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "game"))
import lesson_bridge

tree = ast.parse((ROOT / "game" / "main.py").read_text())
# Import the same game definitions without starting its perpetual browser loop.
tree.body.pop()
game = {}
exec(compile(tree, "main.py", "exec"), game)


class LessonTests(unittest.TestCase):
    def simulate(self, body, seconds=6):
        game["on_blue"] = lesson_bridge.compile_solution(body)
        girl = game["Girl"]()
        for _ in range(int(seconds * 60)):
            game["update"](girl, 1 / 60, {}, "test")
            if girl.x <= game["GOAL_X"] + 18:
                break
        return girl

    def test_starter_reproduces_repeated_jumping(self):
        girl = self.simulate("    player.jump()\n")
        self.assertGreater(girl.jumps, 2)
        self.assertEqual(girl.x, 570)

    def test_real_fix_reaches_flag_without_jumping(self):
        girl = self.simulate("    player.move_left()\n")
        self.assertLessEqual(girl.x, game["GOAL_X"] + 18)
        self.assertEqual(girl.jumps, 0)

    def test_stop_alone_does_not_solve_level(self):
        girl = self.simulate("    player.stop()\n")
        self.assertEqual(girl.x, 570)

    def test_moving_right_does_not_solve_level(self):
        girl = self.simulate("    player.move_right()\n")
        self.assertGreater(girl.x, 570)

    def test_syntax_errors_are_readable(self):
        with self.assertRaisesRegex(ValueError, "Python syntax error"):
            lesson_bridge.compile_solution("    player.move_left(\n")

    def test_unbounded_and_out_of_scope_code_is_rejected(self):
        for source in ["    while True: pass\n", "    import os\n", "    player.__class__()\n", "    player.x = 0\n", "    print('hello')\n", "    pass\nx = 1\n"]:
            with self.subTest(source=source), self.assertRaises(ValueError):
                lesson_bridge.compile_solution(source)


if __name__ == "__main__":
    unittest.main()
