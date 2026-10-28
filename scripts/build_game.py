"""Build both real Pygame runtimes and publish their complete Python sources."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "public" / "levels").mkdir(exist_ok=True)
source = (ROOT / "game" / "main.py").read_text(encoding="utf-8")

for number, slug, runner in [(1, "jumping-girl", "runner"), (2, "blue-leap", "runner-2")]:
    folder = ROOT / "game" if number == 1 else ROOT / "game" / "build" / "level2-source"
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
