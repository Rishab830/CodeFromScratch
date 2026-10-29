export type Level = {
  number: number; runtimeId: number; id: string; title: string; world: string; coins: readonly string[];
  group: 'workshop' | 'bonus'; concept: string; exercise: 'debug' | 'build' | 'arcade';
  kind: 'program' | 'reactive' | 'arcade'; spaceLabel: string;
  hints: readonly [string, string, string];
  source: string; runtime: string; storage: string; missionTitle: string;
  mission: string; intro: string; death: string; log: string;
  goal?: string; reference?: string; actions?: readonly (readonly [string,string])[];
  controls?: readonly (readonly [string,string])[]; codeVersion?: number;
};
export const LEVELS: readonly Level[] = [
  {
    "number": 1,
    "id": "confused-traffic-signal",
    "hints": [
      "Watch the lights for a full cycle. Which colour never appears, and which branch chooses the colour after red?",
      "Each branch should describe one step of the cycle: red to green, green to yellow, and yellow back to red. Use == to check current and = to set next_color.",
      "When current is red, set next_color to green. Use elif for green and set yellow there; let else set red. Compile, then drive right through the crossing."
    ],
    "title": "The Confused Traffic Signal",
    "world": "Apricot Avenue",
    "coins": [
      "first",
      "second"
    ],
    "source": "/levels/confused-traffic-signal.py",
    "runtime": "/runner-3/",
    "storage": "cfs:traffic:v1",
    "codeVersion": 2,
    "missionTitle": "Red. Yellow. Red. Wait a minute\u2026",
    "mission": "The signal keeps switching between red and yellow. Fix its sequence, then drive your car through the crossing to the flag.",
    "intro": "Watch the signal. Drive through the crossing when it turns green.",
    "goal": "Drive through the crossing",
    "death": "The crossing needs a working signal.",
    "log": "Use Left / Right to drive. The car waits at red and yellow.",
    "reference": "Use if, elif, and else to decide what happens for each light. Set next_color in the matching branch. The game handles the rest; the car is yours to drive.",
    "actions": [
      [
        "current",
        "The current light: red, yellow, or green."
      ],
      [
        "next_color",
        "The colour chosen by your conditions."
      ],
      [
        "Left / Right",
        "Drive the car."
      ]
    ],
    "controls": [
      [
        "ArrowLeft",
        "Drive left"
      ],
      [
        "ArrowRight",
        "Drive right"
      ]
    ],
    "runtimeId": 3,
    "concept": "if",
    "exercise": "debug",
    "group": "workshop",
    "kind": "reactive",
    "spaceLabel": ""
  },
  {
    "number": 2,
    "runtimeId": 8,
    "id": "parcel-sorter",
    "hints": [
      "Look at the colour of the parcel on the belt and the labels on the three delivery bays. Each parcel needs just one matching action.",
      "Call parcel_colour() in an if condition. Use elif for a second colour and else for the remaining colour, with one send action indented under each branch.",
      "Try if parcel_colour() == \"red\": with send_left() inside it. Follow with elif for \"blue\" and send_middle(), then else with send_right(). Compile and press Space to deliver all six."
    ],
    "title": "The Parcel Sorter",
    "world": "Peach Post Office",
    "concept": "if",
    "exercise": "build",
    "group": "workshop",
    "kind": "program",
    "coins": [
      "first",
      "second"
    ],
    "source": "/levels/parcel-sorter.py",
    "runtime": "/runner-8/",
    "storage": "cfs:workshop:parcel:v1",
    "missionTitle": "A blank sorter. Three delivery bays.",
    "mission": "Write your own if / elif / else decisions. Red parcels belong in the left bay, blue in the middle, and yellow on the right. Deliver all six parcels using the same function.",
    "intro": "Read the parcel colour, write your decisions, then press Space to sort.",
    "goal": "Parcel Sorter",
    "death": "Check your program and try again.",
    "log": "Press or hold Space to advance one action at a time.",
    "reference": "Use if, elif, and else. Loops are not enabled in this mission. The function header and game code are locked. Use the supplied functions in the green area. Compile, then press Space to play.",
    "actions": [
      [
        "parcel_colour()",
        "Reports red, blue, or yellow."
      ],
      [
        "send_left()",
        "Send this parcel to the red bay."
      ],
      [
        "send_middle()",
        "Send it to the blue bay."
      ],
      [
        "send_right()",
        "Send it to the yellow bay."
      ]
    ],
    "controls": [
      [
        " ",
        "Next action"
      ]
    ],
    "spaceLabel": "Step"
  },
  {
    "number": 3,
    "runtimeId": 9,
    "id": "bridge-builder",
    "hints": [
      "Tap Space once and watch the whole starter loop run. Count the planks it builds and compare the bridge length with the river gap.",
      "range(n) repeats place_plank() n times. The starter repeats five times, so it builds only half the required bridge. Maya still moves independently with Left and Right.",
      "Change the loop to for plank in range(10): and keep place_plank() indented inside it. Compile, tap Space once to build all ten planks, then walk across to the flag with Right."
    ],
    "title": "The Bridge Builder",
    "world": "Apricot River",
    "concept": "for",
    "exercise": "debug",
    "group": "workshop",
    "kind": "program",
    "coins": [
      "first",
      "second"
    ],
    "source": "/levels/bridge-builder.py",
    "runtime": "/runner-9/",
    "storage": "cfs:workshop:bridge:v1",
    "codeVersion": 3,
    "missionTitle": "Half a bridge won't get you across.",
    "mission": "The river gap is ten planks long, but the starter loop builds only five. Tap Space once to run the whole building loop. Its repetition count determines the bridge's length. Fix the code, build your bridge, then walk across with Left / Right. Missing planks leave gaps you can fall through.",
    "intro": "Tap Space once to build the whole bridge. Left / Right moves Maya at any time.",
    "goal": "Bridge Builder",
    "death": "Watch for missing planks in the bridge.",
    "log": "One Space press runs the entire building loop. Each repetition adds a plank. Use Left / Right to walk to the flag yourself.",
    "reference": "Use a for loop with place_plank() inside it. One Space press starts the whole loop, and its planks appear in sequence. The gap needs ten planks. Left / Right moves Maya independently, before, during, and after building. Restart or Compile resets the bridge so you can try again.",
    "actions": [
      [
        "range(n)",
        "Repeat the loop n times."
      ],
      [
        "place_plank()",
        "Add one plank to the bridge's length."
      ],
      [
        "Left / Right",
        "Move Maya yourself, before or after building."
      ]
    ],
    "controls": [
      [
        "ArrowLeft",
        "Move left"
      ],
      [
        "ArrowRight",
        "Move right"
      ],
      [
        " ",
        "Build bridge"
      ]
    ],
    "spaceLabel": "Build bridge"
  },
  {
    "number": 4,
    "runtimeId": 4,
    "id": "lost-robot",
    "hints": [
      "Trace the path from the robot to the green dock. Split it into straight sections and count moves between tiles, rather than counting the starting tile.",
      "Write a separate for loop for each straight section. Put the matching movement function inside that loop, then start the next loop at the same indentation as the first.",
      "One route is three moves left, two up, then three left. Use range(3) with move_left(), range(2) with move_up(), then range(3) with move_left(). Compile and step through to the dock; press Space once more to finish."
    ],
    "title": "The Lost Robot",
    "world": "Lavender Depot",
    "concept": "for",
    "exercise": "build",
    "group": "workshop",
    "kind": "program",
    "coins": [
      "loop",
      "route"
    ],
    "source": "/levels/lost-robot.py",
    "runtime": "/runner-4/",
    "storage": "cfs:workshop:robot:v1",
    "missionTitle": "Count the tiles. Write the route.",
    "mission": "Your robot is waiting for instructions. Follow the visible path to the green dock. Write your own for loops to repeat moves along each straight part of the route.",
    "intro": "Write your movement loops. Press or hold Space to step through them.",
    "goal": "Lost Robot",
    "death": "Check your program and try again.",
    "log": "Press or hold Space to advance one action at a time.",
    "reference": "Use for loops for movement. No instruction lists or while loops are needed. The function header and game code are locked. Use the supplied functions in the green area. Compile, then press Space to play.",
    "actions": [
      [
        "range(n)",
        "Repeat a movement n times."
      ],
      [
        "move_left()",
        "Move one tile left."
      ],
      [
        "move_right()",
        "Move one tile right."
      ],
      [
        "move_up()",
        "Move one tile up."
      ],
      [
        "move_down()",
        "Move one tile down."
      ]
    ],
    "controls": [
      [
        " ",
        "Next action"
      ]
    ],
    "spaceLabel": "Step"
  },
  {
    "number": 5,
    "runtimeId": 10,
    "id": "space-patrol",
    "hints": [
      "There are exactly enough bullets for ten enemies with three hits each. Watch the TARGET sensor between waves. What happens to shots fired when it says NO?",
      "Let enemy_visible() decide whether to shoot. You can replace the fixed loop with while enemy_visible(), or put an if enemy_visible() check inside a for loop. The weapon routine runs again as the world changes.",
      "One option is while enemy_visible(): with shoot() indented inside it. Another is for bullet in range(30): with if enemy_visible(): inside the loop and shoot() inside that if. Compile, tap Space to arm, dodge with the arrows, then fly to the exit beacon."
    ],
    "title": "Space Patrol",
    "world": "Starlight Sector",
    "concept": "while / for + if",
    "exercise": "debug",
    "group": "workshop",
    "kind": "arcade",
    "coins": [
      "wave-five",
      "sector-clear"
    ],
    "source": "/levels/space-patrol.py",
    "runtime": "/runner-10/",
    "storage": "cfs:workshop:space-patrol:v1",
    "missionTitle": "Thirty bullets. Ten enemies. No wasted shots.",
    "mission": "Pilot your ship in all four directions and dodge enemy fire. Each of ten enemies needs three hits, and you have only thirty bullets. The starter shoots through empty gaps between waves. Fix when it fires, clear the sector, and fly to the green exit beacon.",
    "intro": "Arrows or WASD fly. Tap Space once to arm your automatic weapon code.",
    "goal": "Clear ten enemies and reach the beacon",
    "death": "Watch your ammunition and shields. Keep moving and fire only when a target is visible.",
    "log": "Tap Space once to arm the weapon. Your code decides when to fire; arrows or WASD control the ship. Auto-aim handles targeting.",
    "reference": "Use while, or a for loop containing an if check. shoot() auto-aims at the current enemy, but consumes a bullet even when no enemy is present. The weapon routine is checked repeatedly after you arm it, and loops can wait for the live sensor without freezing the game. Fly with the arrows or WASD; Space is only needed once.",
    "actions": [
      [
        "enemy_visible()",
        "True while there is a live enemy to target."
      ],
      [
        "shoot()",
        "Use one bullet. Auto-aim hits the visible enemy."
      ],
      [
        "bullets_left()",
        "Reports the remaining ammunition."
      ],
      [
        "range(30)",
        "Repeat a check thirty times; the weapon routine runs again."
      ]
    ],
    "controls": [
      ["ArrowLeft", "Move left"],
      ["ArrowRight", "Move right"],
      ["ArrowUp", "Move up"],
      ["ArrowDown", "Move down"],
      [
        " ",
        "Arm weapon"
      ]
    ],
    "spaceLabel": "Arm weapon"
  },
  {
    "number": 6,
    "runtimeId": 11,
    "id": "foggy-tunnel",
    "hints": [
      "The remote works outside, but loses signal when the RC car enters. Watch its exit-check animation. Which sensor tells the onboard program when to stop driving?",
      "Use a while loop to move while the exit has not been detected. Put open_exit() after the loop so it is attempted only once. Each new tunnel resets that allowance.",
      "Write while not exit_detected(): with move_forward() indented inside it. Put open_exit() after the loop, at the same indentation as while. Compile, then drive right into each tunnel. The car runs your program automatically after losing signal."
    ],
    "title": "The Foggy Tunnel",
    "world": "Mistwood Passage",
    "concept": "while",
    "exercise": "build",
    "group": "workshop",
    "kind": "arcade",
    "coins": [
      "tunnel-1",
      "tunnel-2",
      "tunnel-3"
    ],
    "source": "/levels/foggy-tunnel.py",
    "runtime": "/runner-11/",
    "storage": "cfs:workshop:foggy:v1",
    "missionTitle": "No signal. The car needs your code.",
    "mission": "Maya's RC car loses its remote signal inside the tunnel. Drive it with Left / Right outside, then let your onboard while loop take over. Watch the car through the see-through tunnel as it checks for the exit. Open the gate only once per crossing. The same code must clear all three tunnels.",
    "intro": "Left / Right controls the RC car outside. Enter the tunnel to run your onboard program.",
    "goal": "Guide the RC car through three tunnels",
    "death": "Check the exit sensor and your single open-exit attempt before trying again.",
    "log": "Drive right to enter. NO SIGNAL means the remote is disconnected and your code is in control. Watch each exit check and the gate-opening animation.",
    "reference": "Use while, with move_forward() inside the loop. For loops are not enabled. exit_detected() plays a sensor-check animation and reports whether the gate is within reach. open_exit() may be attempted only once per tunnel run, even if the first attempt is too early. The allowance resets for the next tunnel or Restart. Inside, the code runs automatically; outside, use Left / Right or A / D.",
    "actions": [
      [
        "exit_detected()",
        "Animate a sensor check. True when the gate is within reach."
      ],
      [
        "move_forward()",
        "Drive the RC car one step inside the tunnel."
      ],
      [
        "open_exit()",
        "Try opening the gate. Only one attempt per tunnel run."
      ]
    ],
    "controls": [
      [
        "ArrowLeft",
        "Move left"
      ],
      [
        "ArrowRight",
        "Move right"
      ]
    ],
    "spaceLabel": ""
  },
  {
    "number": 7,
    "id": "wrong-door",
    "hints": [
      "Read the terminal's password note and compare it with the symbols above the doors. Which door opens when you submit that password?",
      "The inner if checks the password, but its return value chooses the door. Door indexes start at 0 on the left, so the third door has index 2.",
      "Keep the outer check for a non-empty password. Inside the password == \"STAR\" branch, return 2 instead of 0; return None for other passwords. Compile, enter STAR, click inside the game, use Space beside the terminal, and walk to the rightmost door."
    ],
    "title": "The Wrong Door",
    "world": "Rosewood Hall",
    "coins": [
      "first",
      "second"
    ],
    "source": "/levels/wrong-door.py",
    "runtime": "/runner-6/",
    "storage": "cfs:doors:v1",
    "missionTitle": "The password fits. The door doesn\u2019t.",
    "mission": "Three doors, one way out. Read the terminal note and enter the password below the game. The program opens the wrong door. Fix its logic, use the terminal, and walk through the correct exit.",
    "intro": "Enter the password below, then press Space beside the terminal. Watch which door opens.",
    "goal": "Open the correct door",
    "death": "That door leads to a dead end.",
    "log": "Enter a password, press Space near the terminal, then walk to the door.",
    "reference": "choose_door(password) returns a door index, or None to deny entry. Doors are numbered from left to right starting at 0. The symbols and password note are in the room.",
    "actions": [
      [
        "password",
        "The text you enter below the game."
      ],
      [
        "0 / 1 / 2",
        "The left, middle, and right doors."
      ],
      [
        "None",
        "Do not open a door."
      ],
      [
        "Space",
        "Submit at the terminal."
      ]
    ],
    "controls": [
      [
        "ArrowLeft",
        "Move left"
      ],
      [
        "ArrowRight",
        "Move right"
      ],
      [
        " ",
        "Use terminal"
      ]
    ],
    "runtimeId": 6,
    "concept": "nested-if",
    "exercise": "debug",
    "group": "bonus",
    "kind": "arcade",
    "spaceLabel": "Interact",
    "codeVersion": 2
  },
  {
    "number": 8,
    "runtimeId": 12,
    "id": "rocket-launch",
    "hints": [
      "The rocket needs power before fuel, and both before launch. Watch which sensor is still false at each step.",
      "Use an outer if to check power_on(). Inside its true branch, use another if to check fuel_ready(). Give each false branch the action that makes its own sensor ready.",
      "If power_on() is true, check fuel_ready() inside it: launch() when true, otherwise refuel(). The outer else should call wait_for_power(). Compile and press Space repeatedly so the same checks run after each state change."
    ],
    "title": "The Rocket Launch",
    "world": "Starlight Launch Pad",
    "concept": "nested-if",
    "exercise": "build",
    "group": "bonus",
    "kind": "program",
    "coins": [
      "fuel",
      "launch"
    ],
    "source": "/levels/rocket-launch.py",
    "runtime": "/runner-12/",
    "storage": "cfs:bonus:rocket:v1",
    "missionTitle": "Power first. Fuel second. Then launch.",
    "mission": "Build nested if statements for the launch checks. If power is off, wait for power. Once it is on, check the fuel: refuel when needed and launch when ready. Run the same function again as the state changes.",
    "intro": "Write your nested checks. Press Space to run one action, then check again.",
    "goal": "Rocket Launch",
    "death": "Check your program and try again.",
    "log": "Press or hold Space to advance one action at a time.",
    "reference": "Use one if inside another if. Loops are not enabled. The function header and game code are locked. Use the supplied functions in the green area. Compile, then press Space to play.",
    "actions": [
      [
        "power_on()",
        "Reports whether the launch pad has power."
      ],
      [
        "fuel_ready()",
        "Reports whether the rocket is fuelled."
      ],
      [
        "wait_for_power()",
        "Switch on the power."
      ],
      [
        "refuel()",
        "Fuel the rocket after power is on."
      ],
      [
        "launch()",
        "Launch when power and fuel are ready."
      ]
    ],
    "controls": [
      [
        " ",
        "Next action"
      ]
    ],
    "spaceLabel": "Step"
  },
  {
    "number": 9,
    "runtimeId": 13,
    "id": "greenhouse-grid",
    "hints": [
      "Step through the starter. Is it missing a whole row, or a plant from every row? Count the rows and columns in the greenhouse.",
      "The outer loop chooses a row and the inner loop visits its columns. range(3) gives the indexes 0, 1, and 2. Both dimensions have three cells.",
      "Change the outer loop to for row in range(3): and keep the inner for column in range(3):. Leave water_cell(row, column) inside both loops and open_exit() outside them. Compile and step through all nine plants."
    ],
    "title": "The Greenhouse Grid",
    "world": "Sage Garden",
    "concept": "nested-loops",
    "exercise": "debug",
    "group": "bonus",
    "kind": "program",
    "coins": [
      "row",
      "garden"
    ],
    "source": "/levels/greenhouse-grid.py",
    "runtime": "/runner-13/",
    "storage": "cfs:bonus:greenhouse:v1",
    "missionTitle": "Every row. Every plant.",
    "mission": "The greenhouse has three rows and three columns. The starter nested loops leave some plants dry. Step through the row and column values, fix the counts, then open the exit.",
    "intro": "Step the nested loops and water every plant.",
    "goal": "Greenhouse Grid",
    "death": "Check your program and try again.",
    "log": "Press or hold Space to advance one action at a time.",
    "reference": "Use a for loop inside another for loop. The function header and game code are locked. Use the supplied functions in the green area. Compile, then press Space to play.",
    "actions": [
      [
        "range(n)",
        "Repeat a loop n times."
      ],
      [
        "water_cell(row, column)",
        "Water one cell using its row and column."
      ],
      [
        "open_exit()",
        "Leave once all nine plants have been watered."
      ]
    ],
    "controls": [
      [
        " ",
        "Next action"
      ]
    ],
    "spaceLabel": "Step"
  },
  {
    "number": 10,
    "runtimeId": 7,
    "id": "final-escape",
    "hints": [
      "The exit has two separate requirements: power every cell, then release the latch. Opening the door before unlocking it will not work.",
      "Use nested for loops for two rows and three columns, with power_cell(row, column) inside both. After the loops finish, check all_powered() before trying the latch.",
      "Use range(2) for row and range(3) for column, calling power_cell(row, column) in the inner loop. After both loops, write if all_powered(): and put unlock_exit() followed by open_exit() inside it. Compile, then press Space through your escape."
    ],
    "title": "The Final Escape",
    "world": "Moonlit Observatory",
    "concept": "nested-loops",
    "exercise": "build",
    "group": "bonus",
    "kind": "program",
    "coins": [
      "first",
      "second"
    ],
    "source": "/levels/final-escape.py",
    "runtime": "/runner-7/",
    "storage": "cfs:escape:v1",
    "missionTitle": "One room. Build your own escape.",
    "mission": "Two rows of three power cells keep the exit locked. Write nested loops to charge the cells. Then check the power, unlock the latch, and open the exit in the right order.",
    "intro": "Write your escape program. Press Space to step through it.",
    "goal": "Final Escape",
    "death": "Check your program and try again.",
    "log": "Press or hold Space to advance one action at a time.",
    "reference": "Use nested for loops. Conditions can help you check when to unlock the latch. The function header and game code are locked. Use the supplied functions in the green area. Compile, then press Space to play.",
    "actions": [
      [
        "range(n)",
        "Repeat a loop n times."
      ],
      [
        "power_cell(row, column)",
        "Power one cell. Rows start at 0; columns start at 0."
      ],
      [
        "all_powered()",
        "Reports whether all six cells are powered."
      ],
      [
        "unlock_exit()",
        "Unlock the latch after powering the room."
      ],
      [
        "open_exit()",
        "Open the unlocked exit."
      ]
    ],
    "controls": [
      [
        " ",
        "Next action"
      ]
    ],
    "spaceLabel": "Step",
    "codeVersion": 3
  },
  {
    "number": 11,
    "id": "jumping-girl",
    "hints": [
      "Watch what happens when Maya lands on blue. Which action sends her toward those spikes?",
      "The game already handles your arrow keys. You can change the blue action, or remove that automatic action.",
      "Try player.move_left() instead of player.jump(). Or try pass to leave movement entirely to your controls. Compile, then play!"
    ],
    "title": "The Jumping Girl",
    "world": "Pastel Meadow",
    "coins": [
      "below"
    ],
    "source": "/levels/jumping-girl.py",
    "runtime": "/runner/",
    "storage": "cfs:jumping-girl:v2",
    "missionTitle": "Blue shouldn\u2019t mean \u201cboing!\u201d",
    "mission": "Maya should move left when she touches blue. Instead, she jumps straight toward the spikes. Something in her code is a little mixed up. Reach the flag and jump across the gap along the way.",
    "intro": "Get Maya to the flag. Mind the spikes and jump across the gap.",
    "death": "Mind the spikes and the gap in the floor.",
    "log": "Watch the spikes above blue!",
    "runtimeId": 1,
    "concept": "arcade",
    "exercise": "arcade",
    "group": "bonus",
    "kind": "arcade",
    "spaceLabel": "Jump"
  },
  {
    "number": 12,
    "id": "blue-leap",
    "hints": [
      "Blue always calls jump(), and that action is locked. Read the editable Girl class to find what decides how Maya moves when she jumps.",
      "In jump(), self.vy sets the initial upward speed. A smaller negative magnitude gives a lower jump; a larger one gives a higher jump. Think about a route below or above the spikes.",
      "One option is changing self.vy = -178 to self.vy = -80 for small jumps beneath the spikes, then jumping the floor gap. Another is -420 for a high manual jump over the spikes. Compile and time your jumps with Left and Space."
    ],
    "title": "The Blue Leap",
    "world": "Pastel Meadow",
    "coins": [
      "above",
      "below"
    ],
    "source": "/levels/blue-leap.py",
    "runtime": "/runner-2/",
    "storage": "cfs:blue-leap:v2",
    "missionTitle": "This time, blue WILL make Maya jump.",
    "mission": "Get her to the flag. Explore the game, read the code, and find your own way past the spikes. There is also a small gap to jump across before the flag.",
    "intro": "This time, blue WILL make Maya jump. Reach the flag and jump across the gap.",
    "death": "Mind the spikes and the gap in the floor.",
    "log": "This time, blue WILL make Maya jump.",
    "runtimeId": 2,
    "concept": "arcade",
    "exercise": "arcade",
    "group": "bonus",
    "kind": "arcade",
    "spaceLabel": "Jump"
  },
  {
    "number": 13,
    "id": "endless-coin-collector",
    "hints": [
      "Start the collector and watch what happens when its count reaches five. What does the starter condition return at that point?",
      "should_collect(count) should be true only while more coins are needed. At five it must become false so the machine stops and unlocks the exit.",
      "Try return count < 5 instead of return count >= 0. Compile, walk to the collector, press Space to start it, and walk to the exit once it stops at five."
    ],
    "title": "The Endless Coin Collector",
    "world": "Honey Workshop",
    "coins": [
      "coin-1",
      "coin-2",
      "coin-3",
      "coin-4",
      "coin-5"
    ],
    "source": "/levels/endless-coin-collector.py",
    "runtime": "/runner-5/",
    "storage": "cfs:collector:v1",
    "missionTitle": "Five coins. Why is it still counting?",
    "mission": "The collector must stop after exactly five coins to unlock the exit. It keeps going instead. Fix its condition, start the machine, and walk through the unlocked door.",
    "intro": "Walk to the collector and press Space. Watch its count, then reach the exit.",
    "goal": "Stop at five and unlock the exit",
    "death": "The collector needs another try.",
    "log": "Move with Left / Right. Press Space beside the collector to start it.",
    "reference": "should_collect(count) decides whether the machine collects another coin. Starting the machine commits it to that condition until it stops. Restart clears the machine count; your coin badges stay saved.",
    "actions": [
      [
        "count",
        "Coins collected by the machine this attempt."
      ],
      [
        "True / False",
        "Continue collecting, or stop."
      ],
      [
        "Space",
        "Start the collector when nearby."
      ]
    ],
    "controls": [
      [
        "ArrowLeft",
        "Move left"
      ],
      [
        "ArrowRight",
        "Move right"
      ],
      [
        " ",
        "Interact"
      ]
    ],
    "runtimeId": 5,
    "concept": "arcade",
    "exercise": "arcade",
    "group": "bonus",
    "kind": "arcade",
    "spaceLabel": "Interact"
  }
];
export const CORE_LEVELS = LEVELS.filter(level => level.group === 'workshop');
export const BONUS_LEVELS = LEVELS.filter(level => level.group === 'bonus');
export function canPlay(level: Level, cleared: readonly number[]) {
  if (cleared.includes(level.number)) return true;
  if (level.group === 'bonus') return CORE_LEVELS.every(core => cleared.includes(core.number));
  const index = CORE_LEVELS.findIndex(core => core.id === level.id);
  return index === 0 || (index > 0 && cleared.includes(CORE_LEVELS[index-1].number));
}
