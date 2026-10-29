"""Package each independent Pygame file and publish that exact source."""
from pathlib import Path
from html import escape
import json
import re
import shutil
import subprocess
import sys
from levels import LEVELS

ROOT = Path(__file__).resolve().parents[1]
metadata = {level["runtimeId"]: level for level in json.loads(subprocess.check_output(
    ["node", str(ROOT / "scripts" / "level-metadata.cjs")], cwd=ROOT, encoding="utf-8"))}
(ROOT / "public" / "levels").mkdir(exist_ok=True)

for number, slug in LEVELS.items():
    if metadata[number]["source"] != f"/levels/{slug}.py":
        raise ValueError(f"Lesson metadata does not match runtime {number}: {slug}")
    source_file = ROOT / "game" / "levels" / f"{slug}.py"
    source = source_file.read_text(encoding="utf-8")
    if len(re.findall(r"^[ \t]*# EDIT START$", source, re.M)) != 1 or len(re.findall(r"^[ \t]*# EDIT END$", source, re.M)) != 1:
        raise ValueError(f"{source_file} must have exactly one editable region")
    compile(source, str(source_file), "exec")
    # main.py is only Pygbag's packaging entrypoint. No lesson code is generated.
    folder = ROOT / "game" / "build" / ("game" if number == 1 else f"level{number}-source")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "main.py").write_text(source, encoding="utf-8", newline="\n")
    shutil.copy2(ROOT / "game" / "lesson_bridge.py", folder / "lesson_bridge.py")
    subprocess.run([sys.executable, "-m", "pygbag", "--build", "--ume_block", "0", "--template", str(ROOT / "game" / "runner.tmpl"), str(folder)], check=True, cwd=ROOT)
    runner = "runner" if number == 1 else f"runner-{number}"
    target = ROOT / "public" / runner
    shutil.copytree(folder / "build" / "web", target, dirs_exist_ok=True)
    index = target / "index.html"
    html = index.read_text(encoding="utf-8")
    if html.count("__RUNNER_BASE__") != 1 or html.count("__RUNNER_TITLE__") != 1:
        raise ValueError(f"Missing runner metadata placeholder in {index}")
    title = escape(metadata[number]["title"] + " · Pygame runner")
    index.write_text(html.replace("__RUNNER_BASE__", f"/{runner}/").replace("__RUNNER_TITLE__", title), encoding="utf-8", newline="\n")
    (ROOT / "public" / "levels" / f"{slug}.py").write_text(source, encoding="utf-8", newline="\n")
    print(f"Level {number}: {source_file.name} -> {target}")
