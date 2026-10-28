# Code From Scratch

A Next.js website for learning Python through playable Pygame levels. The project lives directly in `CodeFromScratch/`, with **The Jumping Girl** and **The Blue Leap** as its first two lessons.

## Run

```powershell
npm install
npm run dev
```

Open http://localhost:3000. The generated Pygame assets are included in `public/runner`, so Python is not required to serve the site. The first game load downloads its CPython WebAssembly runtime and Pygame from pygame-web's CDN.

The loading bar follows four startup stages: Python, level files, Pygame, and game startup. It observes actual Fetch streams and XMLHttpRequest progress without changing the runtime responses. It shows transferred bytes and percentages when sizes are available; unknown-size downloads and initialization remain animated rather than using a timer-based percentage. A failed download or a long wait exposes **Retry loading**, which restarts the engine and resets the bar.

## Vercel hosting

Deploy the project root with the Next.js preset and `npm run build`. The app uses `/runner/` and `/runner-2/` for its iframe pages. Vercel can serve directory indexes at `/runner` and `/runner-2` while returning 404 for the explicit `/runner/index.html` URLs. Each generated runner includes its own absolute `<base>` so game archives still load from the correct directory when trailing slashes are removed. No additional CORS or cross-origin isolation headers are needed for this runtime.

After updating the source, redeploy on Vercel. Both the application URL change and the regenerated `public/runner*/index.html` files must be included. Do not fix only the iframe URL: without the explicit base, a slashless page can incorrectly request its archive from `/game.apk` instead of `/runner/game.apk`.

To reproduce production-style URL canonicalization during browser checks:

```powershell
$env:EMULATE_CLEAN_URLS='1'
npm run test:browser
```

## Play, edit, compile

The **Site** control in the header switches between the default dark palette and the white-and-orange light palette. The **Code** control in the editor header changes only the editor and its surrounding controls. Both default to dark, save their preferences independently on this device, and preserve edits and undo history when switched.

- Click **Play level**, then use Left / Right or A / D to move and Space / Up / W to jump. Touch controls are below the game.
- Landing on blue calls `on_blue(player)`. The starter's `player.jump()` launches Maya into overhead spikes.
- A spike collision ends the attempt and shows **Game over** with **Restart level**.
- Read the entire Python file; only the green function body is editable. **Compile** validates and compiles that Python, applies it, and restarts the playable level. It does not run an automated attempt or grade a solution.
- **Restart** reuses the last successfully compiled code. **Reset code** restores the starter in the editor; Compile is still required to apply those changes.
- Reach the flag yourself to complete a level and earn 100 XP. Clearing Level 1 unlocks Level 2 in the adventure map and through **Next adventure**. Any valid solution, route, or number of jumps is accepted.
- In Level 2, the blue action always calls `player.jump()` and is locked. A different section is editable. Its mission and reference state that blue makes Maya jump, without explaining the adjustment students need to discover. Level 2 has no solution hints.
- Each level keeps its own edits and completion. Revisit either unlocked lesson from the map.
- Edits and completed levels persist locally in this browser. The new manual-play level uses a separate progress key from the old automatic demo.

## Project structure

`lib/levels.ts` registers the lessons and their source, runtime, and storage keys. `game/main.py` owns the complete Pygame world, sprite art, physics, keyboard controls, collisions, and flag trigger. It draws a 320×180 pixel canvas and scales it up without smoothing. The build generates complete per-level sources in `public/levels/` and separate runtimes in `public/runner/` and `public/runner-2/`. Each source contains exactly one editable region.

`game/lesson_bridge.py` compiles the editable Python function. Level 1 permits the player API, simple conditionals, and `pass`. Level 2 permits a bounded numeric return from `configure()` while preserving the jump action. Both reject unrelated executable code. This is a bounded lesson runner, not a general-purpose Python sandbox. Client-side progress is suitable for this prototype, not authoritative grading.

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

With a local server running, `npm run test:themes` checks the independent defaults, all theme combinations, saved preferences, editor history, level navigation, and mobile layout.

The production static site is exported to `out/`. To run the actual WASM end-to-end checks, serve the app, then set `TEST_URL` to that URL and run `npm run test:browser`. The checks use installed Google Chrome through Playwright and verify manual play, spike death/restart, Python compilation/errors, protected editing, multiple valid solutions, physical flag completion, touch controls, and mobile layout.
