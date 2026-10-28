"""Build the real Pygame runtime, then copy its web assets to Next public/."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, "-m", "pygbag", "--build", "--ume_block", "0", "--template", str(ROOT / "game" / "runner.tmpl"), str(ROOT / "game")], check=True, cwd=ROOT)
target = ROOT / "public" / "runner"
shutil.copytree(ROOT / "game" / "build" / "web", target, dirs_exist_ok=True)
(ROOT / "public" / "levels").mkdir(exist_ok=True)
shutil.copy2(ROOT / "game" / "main.py", ROOT / "public" / "levels" / "jumping-girl.py")
print(f"Game built into {target}")
