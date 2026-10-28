"""Build both real Pygame runtimes and publish their complete Python sources."""
from pathlib import Path
import shutil
import subprocess
import sys
from puzzles import PUZZLES

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "public" / "levels").mkdir(exist_ok=True)
source = (ROOT / "game" / "main.py").read_text(encoding="utf-8")

pixel_art = source[source.index("# Each character"):source.index("def draw_scene(")]
for number, slug, runner in [(1, "jumping-girl", "runner"), (2, "blue-leap", "runner-2")] + [(number, data[0], f"runner-{number}") for number, data in PUZZLES.items()]:
    folder = ROOT / "game" if number == 1 else ROOT / "game" / "build" / f"level{number}-source"
    lesson_source = source
    if number == 2:
        folder.mkdir(parents=True, exist_ok=True)
        lesson_source = source.replace("LEVEL_NUMBER = 1", "LEVEL_NUMBER = 2", 1)
        # Lock the blue action and make the entire Girl class editable.
        lesson_source = lesson_source.replace("    # EDIT START\n    player.jump()\n    # EDIT END", "    player.jump()")
        start = lesson_source.index("class Girl:")
        end = lesson_source.index("\ndef on_blue(player):", start)
        girl_class = lesson_source[start:end].rstrip() + "\n"
        lesson_source = lesson_source[:start] + "# EDIT START\n" + girl_class + "# EDIT END\n\n" + lesson_source[end:]
        (folder / "main.py").write_text(lesson_source, encoding="utf-8", newline="\n")
        shutil.copy2(ROOT / "game" / "lesson_bridge.py", folder / "lesson_bridge.py")
    elif number >= 3:
        folder.mkdir(parents=True, exist_ok=True)
        _, name, arguments, body = PUZZLES[number]
        function = f"def {name}({arguments}):\n    # EDIT START\n{body}    # EDIT END"
        lesson_source = (ROOT / "game" / "adventure.py").read_text(encoding="utf-8")
        lesson_source = lesson_source.replace("LEVEL_NUMBER = 3", f"LEVEL_NUMBER = {number}", 1).replace("__PUZZLE_NAME__", name).replace("__PUZZLE_ARGUMENTS__", arguments).replace("__LESSON_FUNCTION__", function).replace("__PIXEL_ART__", pixel_art)
        if number != 4:
            start, end = lesson_source.index("ROBOT_PATH ="), lesson_source.index(f"def {name}(")
            lesson_source = lesson_source[:start] + lesson_source[end:]
        (folder / "main.py").write_text(lesson_source, encoding="utf-8", newline="\n")
        shutil.copy2(ROOT / "game" / "lesson_bridge.py", folder / "lesson_bridge.py")
    subprocess.run([sys.executable, "-m", "pygbag", "--build", "--ume_block", "0", "--template", str(ROOT / "game" / "runner.tmpl"), str(folder)], check=True, cwd=ROOT)
    target = ROOT / "public" / runner
    shutil.copytree(folder / "build" / "web", target, dirs_exist_ok=True)
    # Vercel can serve /runner/index.html at /runner. Keep relative archive
    # requests inside the runner directory even after that canonicalization.
    index = target / "index.html"
    html = index.read_text(encoding="utf-8")
    if html.count('__RUNNER_BASE__') != 1:
        raise ValueError(f"Missing runner base placeholder in {index}")
    index.write_text(html.replace('__RUNNER_BASE__', f'/{runner}/'), encoding="utf-8", newline="\n")
    (ROOT / "public" / "levels" / f"{slug}.py").write_text(lesson_source, encoding="utf-8", newline="\n")
    print(f"Level {number} built into {target}")
