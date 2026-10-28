# CodeQuest — The Jumping Girl

A Next.js application with a real Pygame game running in the browser through Pygbag / CPython WebAssembly. Students see the entire `main.py` file but can edit only the highlighted body of `on_blue(player)`.

## Run locally

```powershell
npm install
npm run dev
```

Open http://localhost:3000. The generated Pygame assets are included in `public/runner`; Python is not needed to serve the application. The first game load downloads the CPython and Pygame runtime from pygame-web's CDN, so an internet connection is required.

## The lesson

- The starter calls `player.jump()` every time Maya lands on blue, causing repeated jumps.
- Students change it to `player.move_left()`.
- **Play yourself:** click the game, then use Left / Right (or A / D) and Space. On-screen controls work on touch devices.
- **Test my fix:** resets Maya on blue and runs an automatic attempt with keyboard input disabled. Success requires reaching the left flag within six seconds with no jumps.
- Next-level access and 100 XP unlock after a successful automatic test. Level 2 is explicitly a placeholder in this one-level demo.
- Edits and completion are stored locally in the browser. Reset restores the starter code; Reload game restarts the runtime.

## Implementation

`game/main.py` owns all physics, rendering, controls, and win conditions. It is also copied verbatim to `public/lesson.py` for the editor. CodeMirror transaction filtering protects everything outside the edit markers. Changes are sent by `postMessage` to the Pygame runner and compiled by Python immediately; there is no server-side build per attempt. `game/lesson_bridge.py` validates the solution AST before execution, limiting this introductory lesson to the player API, simple conditionals, and `pass`; loops, arbitrary imports, attribute writes, and unrelated calls are rejected. This is a bounded lesson runner, not a general-purpose Python sandbox. Client-side progress is suitable for a demo, not authoritative grading.

## Change the Pygame source

```powershell
python -m pip install -r requirements.txt
npm run build:game
```

Rebuild after changing Python or the runner template. Python 3.12+ is recommended for build tooling. The browser uses Pygbag's own bundled CPython runtime.

## Validate and build

```powershell
npm run test:lesson
npm run typecheck
npm run build
```

For end-to-end checks, start `npm run dev` in another terminal, then run `npm run test:browser`. This uses an installed Google Chrome through Playwright and verifies the actual WASM game, keyboard and touch controls, protected editing, syntax errors, win conditions, reset, and mobile layout. Set `TEST_URL` to check a different serving URL.

The app exports static files to `out/`, compatible with static hosting. There is no Python backend and no database.
