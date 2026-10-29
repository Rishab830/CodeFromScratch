# Code From Scratch

A Next.js website for a one-hour Python workshop. Students read real Pygame code, edit the green section, compile it in the browser, and play to complete each challenge.

## Workshop path

| Lesson | Game | Concept | Starting point |
| --- | --- | --- | --- |
| 1 | The Confused Traffic Signal | `if` / `elif` / `else` | Debug the signal sequence, without dictionaries. |
| 2 | The Parcel Sorter | Conditions in a new setting | Blank function, supplied colour sensors and sorting actions. |
| 3 | The Gift Catcher | Nested `if` | Catch falling gifts; open each box, then drop a bomb or collect a safe gift. |
| 4 | The Bridge Builder | `for` and `range` | Debug how many planks are placed. |
| 5 | The Lost Robot | Counted movement | Blank function, supplied movement actions; no instruction lists. |
| 6 | Space Patrol | `while`, or `for` with `if` | Pilot a ship and fix a weapon that wastes its limited ammunition. |
| 7 | The Foggy Tunnel | Repeat until a live condition changes | Drive an RC car into three tunnels; its blank onboard function must take over when signal is lost. |

Lessons unlock sequentially. Conditions, for, and while have a debugging lesson followed by an editable body containing `pass`. Gift Catcher adds nested-if debugging after the two initial condition lessons. Supplied functions and sensors are visible above the editor. Allow five minutes for orientation, roughly six minutes per core lesson, and the remaining time for discussion or bonuses.

Space Patrol starts with an unconditional `for` loop. Space arms the weapon once, then the student pilots with all four arrows or WASD while their code chooses when to shoot. The ship starts in the center. Ten enemies spawn around the player in three simultaneous groups of four, three, and three; each needs three auto-aimed hits, and the magazine holds exactly thirty bullets. Auto-aim selects the nearest live enemy, and each projectile follows its own target. Empty shots waste ammunition. Enemies fire back; after clearing the sector, fly to the exit beacon. Either a live `while` condition or a `for` loop containing an `if` check works. Foggy Tunnel then requires `while` specifically.

Foggy Tunnel requires `while` and rejects `for`. Left / Right or A / D drives the RC car outside. Entering the tunnel loses signal and automatically starts its onboard function. The wall becomes translucent so students can watch the car, each exit-sensor check, and the rising gate. Maya stays outside holding a remote with an animated antenna. `open_exit()` has one attempt per tunnel run, including unsuccessful early attempts. A second call raises `open exit can only be attempted once`, even after a successful first opening. The allowance resets for the next tunnel or Restart. The same program must handle all three lengths.

## Optional bonuses

All six unlock together after the seven core lessons. Any bonus can be chosen without completing another bonus first.

| Bonus | Game | Focus |
| --- | --- | --- |
| 1 | The Rocket Launch | Build nested conditions using power and fuel sensors. |
| 2 | The Greenhouse Grid | Debug nested loops over rows and columns. |
| 3 | The Final Escape | Build nested loops and conditions to power, unlock, and open an exit. |
| 4 | The Jumping Girl | Fix the blue-tile action, then play to the flag. |
| 5 | The Blue Leap | Edit the entire `Girl` class and find a valid route. |
| 6 | The Endless Coin Collector | Stop the machine at five, then reach the exit. |

The original two platform maps retain overhead spikes, a 21-pixel floor gap (half the default running-jump distance), and the same blue tile. Blue Leap retains its walkable spike top and locked blue jump action. Small jumps under the spikes and high jumps over them are both valid. Coins leave outlines, persist per game, and appear filled or outlined on completion. Any coin count can clear these arcade levels.

Gift Catcher uses only nested `if` statements in its editable handler; `for` and `while` are disabled. Move the basket with Left / Right or A / D, then tap Space once per caught gift. The outer check guards opening a box. Its contents cannot be inspected until the opening animation finishes. The inner check then drops a bomb or collects an egg or coin. A bomb allows one further action, which must be `drop()`; sensor reads do not spend that action. A wrong next action or ending the handler without dropping it plays an explosion before game over. Collect five eggs to win. Coin gifts contribute to saved level coins, including their filled/outline result icons.

## Run and deploy

```powershell
npm install
npm run dev
```

Open http://localhost:3000. Generated game assets are committed, so Python is not needed to serve the site. The first game load downloads CPython WebAssembly and Pygame from pygame-web's CDN. The loader tracks Python, level files, Pygame, and startup, showing real byte counts when available and a retry action on failure or a long wait.

For Vercel, deploy the project root with the Next.js preset and `npm run build`. The app exports to `out/`. Runners live at `/runner/` and `/runner-2/` through `/runner-13/`. Each runner has an absolute base URL so its archive loads correctly when Vercel removes trailing slashes. Preserve both the iframe URL handling and generated runner HTML when updating this fix.

## Edit, compile, play

- The entire current game's Python file is visible; only the green section is editable. Blank challenges supply a locked function definition and an editable body.
- Every core and bonus level has three optional, progressively revealed hints: an observation, a concept clue, and an approach to try. Hints never change the student's code.
- **Compile** validates the edit, applies it, and restarts the game. Compilation or waiting alone cannot finish a level.
- Use each game's displayed controls. Traffic uses Left / Right or A / D; Space Patrol uses all four arrows or WASD. The two platformers also jump with Space, Up, or W. On a phone, use the labelled on-screen buttons.
- In Bridge Builder, one Space tap runs the whole building loop, adding its planks in sequence after the key is released. The river spans ten plank lengths; the starter uses `range(5)` and builds only halfway. Left / Right controls Maya before, during, and after building. Missing planks leave gaps she can fall through, and reaching the flag still requires a manual crossing.
- In Lost Robot, each Space action animates one tile move. Further actions wait until it finishes; a wrong move ends the attempt only when the robot's body reaches a wall.
- Space advances Parcel Sorter, Lost Robot, Rocket Launch, Greenhouse Grid, and Final Escape one action at a time; holding it repeats. In Gift Catcher, tap it once per caught box to run the whole handler. In Space Patrol, tap it once to arm the automatic weapon. Foggy Tunnel starts its code automatically on entering a tunnel and has no Space action. In Endless Coin Collector, Space starts the nearby machine.
- Sensors reflect the live world when the program checks them; the timing depends on the game.
- **Restart** uses the last compiled program. **Reset code** restores the starter in the editor; Compile applies it.
- Each game awards 100 XP. The seven core lessons earn 700 XP and open the optional section. Bonuses are not required for the workshop celebration.
- Edits, completions, coins, and theme preferences persist in this browser. Progress is client-side, not authoritative grading.
- Site and code themes have independent controls, both defaulting to dark. The site light palette is white and orange.

## Source and runtime

`lib/levels.ts` registers display order, concepts, exercises, supplied functions, and progress keys. Display numbers are separate from stable runtime IDs and coin-storage identities, so reordering lessons preserves coins for the correct game.

Each game has a complete independent source in `game/levels/<slug>.py`. `scripts/levels.py` maps stable runtime IDs to these files. `scripts/build_game.py` copies normalized source to `public/levels/<slug>.py` and packages it as `assets/main.py` in an isolated Pygbag archive. Each archive contains only its game and the shared `game/lesson_bridge.py`.

The bridge validates restricted Python syntax. Core program lessons permit the relevant conditions, assignments, arithmetic, loops, and supplied APIs without requiring lists, dictionaries, imports, or classes. Required constructs are checked; repeated lesson actions must occur inside the appropriate loop. Blank `pass` previews cannot win. Commands become generator steps resumed by player input or the game's clock, allowing sensors to change between loop iterations. Action and execution budgets report non-progressing loops without freezing the game.

The older arcade compilers remain available for their lessons, including editing the entire `Girl` class in Blue Leap. This is a bounded educational runner, not a general-purpose Python sandbox.

Space Patrol's weapon program resumes on a game clock after the player arms it. Its loop iterations yield to the game, including iterations where an `if` skips firing, so sensors can change during gaps between waves. Each lesson retains its own execution budget.

Foggy Tunnel also uses a game clock after the RC car enters. Its animated sensor calls suspend the student program until the scan animation finishes, then return the live result. After a successful opening, the program must finish before the car exits, so an extra opening call cannot escape validation.

After editing Python or the runner template, regenerate assets:

```powershell
python -m pip install -r requirements.txt
npm run build:game
```

## Verification

```powershell
npm run test:lesson
npm run typecheck
npm run build
```

Serve the exported `out/` directory on port 3001 (or set `TEST_URL`), then use installed Google Chrome for browser checks:

```powershell
python -m http.server 3001 --bind 127.0.0.1 --directory out
# In another terminal:
npm run test:workshop
npm run test:patrol
npm run test:browser
npm run test:bonuses
npm run test:sources
npm run test:themes
```

`test:workshop` plays the core path and three new nested challenges through actual WASM, checking blank starters, errors, concept constraints, independent bonuses, coins, and mobile layout. `test:adventures` aliases it. `test:patrol` checks the centered spawn, surrounding enemy groups, four-direction flight, both weapon solutions, and manual exit in the browser. `test:browser` covers both platformers; `test:bonuses` covers Gift Catcher and the retained collector game. Source checks cover all 13 editor files and isolated archives. Theme checks cover independent settings, persistence, editor history, and mobile controls.

To reproduce Vercel's slashless runner URLs during platformer checks:

```powershell
$env:EMULATE_CLEAN_URLS='1'
npm run test:browser
```
