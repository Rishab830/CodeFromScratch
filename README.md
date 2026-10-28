# Code From Scratch

A Next.js website for learning Python through playable Pygame levels. The project lives directly in `CodeFromScratch/`; **The Jumping Girl** is the first lesson, not the application name.

## Run

```powershell
npm install
npm run dev
```

Open http://localhost:3000. The generated Pygame assets are included in `public/runner`, so Python is not required to serve the site. The first game load downloads its CPython WebAssembly runtime and Pygame from pygame-web's CDN.

## Play, edit, compile

- Click **Play level**, then use Left / Right or A / D to move and Space / Up / W to jump. Touch controls are below the game.
- Landing on blue calls `on_blue(player)`. The starter's `player.jump()` launches Maya into overhead spikes.
- A spike collision ends the attempt and shows **Game over** with **Restart level**.
- Read the entire Python file; only the green function body is editable. **Compile** validates and compiles that Python, applies it, and restarts the playable level. It does not run an automated attempt or grade a solution.
- **Restart** reuses the last successfully compiled code. **Reset code** restores the starter in the editor; Compile is still required to apply those changes.
- Reach the flag yourself to complete the level, earn 100 XP, and unlock the next-level placeholder. Any valid solution, route, or number of jumps is accepted. `player.move_left()` and `pass` both work with manual controls.
- Edits and completed levels persist locally in this browser. The new manual-play level uses a separate progress key from the old automatic demo.

## Project structure

`lib/levels.ts` registers the current lesson and its source, runtime, and storage keys. `game/main.py` owns the complete Pygame world, sprite art, physics, keyboard controls, collisions, and flag trigger. It draws a 320×180 pixel canvas and scales it up without smoothing. The same complete file is published as `public/levels/jumping-girl.py` for the protected editor.

`game/lesson_bridge.py` compiles the editable Python function and limits this introductory lesson to the player API, simple conditionals, and `pass`. It rejects loops, arbitrary imports, and attribute writes. This is a bounded lesson runner, not a general-purpose Python sandbox. Client-side progress is suitable for this prototype, not authoritative grading.

## Rebuild the game

```powershell
python -m pip install -r requirements.txt
npm run build:game
```

Rebuild after changing Python or the runner template. Pygbag uses its own CPython inside the browser.

## Verify and build

```powershell
npm run test:lesson
npm run typecheck
npm run build
```

The production static site is exported to `out/`. To run the actual WASM end-to-end checks, serve the app, then set `TEST_URL` to that URL and run `npm run test:browser`. The checks use installed Google Chrome through Playwright and verify manual play, spike death/restart, Python compilation/errors, protected editing, multiple valid solutions, physical flag completion, touch controls, and mobile layout.
