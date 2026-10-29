"""Keep each student's file independent and identical to its playable runtime."""
import ast
from pathlib import Path
import sys
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from levels import LEVELS


class LevelSourceTests(unittest.TestCase):
    def test_editor_and_archive_use_the_exact_dedicated_file(self):
        for number, slug in LEVELS.items():
            with self.subTest(level=number):
                # Windows Git checkouts may use CRLF; Python/CodeMirror normalize
                # line endings when reading. Compare the exact normalized text.
                source = (ROOT / "game" / "levels" / f"{slug}.py").read_text(encoding="utf-8")
                self.assertEqual((ROOT / "public" / "levels" / f"{slug}.py").read_text(encoding="utf-8"), source)
                runner = "runner" if number == 1 else f"runner-{number}"
                archive = "game.apk" if number == 1 else f"level{number}-source.apk"
                with zipfile.ZipFile(ROOT / "public" / runner / archive) as packed:
                    self.assertEqual(packed.read("assets/main.py").decode("utf-8"), source)
                    self.assertEqual(packed.read("assets/lesson_bridge.py").decode("utf-8"),
                                     (ROOT / "game" / "lesson_bridge.py").read_text(encoding="utf-8"))
                    python_files = {name for name in packed.namelist() if name.endswith(".py")}
                    self.assertEqual(python_files, {"assets/main.py", "assets/lesson_bridge.py"})

    def test_sources_have_no_other_level_branches(self):
        for number, slug in LEVELS.items():
            with self.subTest(level=number):
                source = (ROOT / "game" / "levels" / f"{slug}.py").read_text(encoding="utf-8")
                self.assertEqual(source.count("# EDIT START"), 1)
                self.assertEqual(source.count("# EDIT END"), 1)
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.IfExp)):
                        self.assertFalse(any(isinstance(child, ast.Name) and child.id == "LEVEL_NUMBER" for child in ast.walk(node.test)))
                names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
                if number != 4:
                    self.assertNotIn("ROBOT_PATH", names)
                    self.assertNotIn("DIRECTIONS", names)
                if number >= 3:
                    self.assertNotIn("Girl", names)
                    self.assertNotIn("SPIKES", names)
                if number in (3, 4):
                    self.assertNotIn("GIRL_SPRITE", names)
                self.assertNotIn("password", names)


if __name__ == "__main__":
    unittest.main()
