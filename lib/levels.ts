export type Level = {
  number: number; runtimeId: number; id: string; title: string; world: string; coins: readonly string[];
  group: 'workshop' | 'bonus'; concept: string; exercise: 'debug' | 'build' | 'arcade';
  kind: 'program' | 'reactive' | 'arcade'; spaceLabel: string;
  source: string; runtime: string; storage: string; missionTitle: string;
  mission: string; intro: string; death: string; log: string;
  goal?: string; reference?: string; actions?: readonly (readonly [string,string])[];
  controls?: readonly (readonly [string,string])[]; codeVersion?: number;
};
export const LEVELS: readonly Level[] = [
  {
    "number": 1,
    "id": "confused-traffic-signal",
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
    "missionTitle": "A loop that stops one plank too soon.",
    "mission": "The river has three bridge spaces. Step the starter program, watch how often its action repeats, and fix the for loop before crossing.",
    "intro": "Step the starter loop. Complete the bridge and cross to the flag.",
    "goal": "Bridge Builder",
    "death": "Check your program and try again.",
    "log": "Press or hold Space to advance one action at a time.",
    "reference": "Use a for loop. Put place_plank() inside the loop; cross after it ends. The function header and game code are locked. Use the supplied functions in the green area. Compile, then press Space to play.",
    "actions": [
      [
        "range(n)",
        "Repeat the loop n times."
      ],
      [
        "place_plank()",
        "Fill the next bridge space."
      ],
      [
        "cross_bridge()",
        "Walk across a completed bridge."
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
    "number": 4,
    "runtimeId": 4,
    "id": "lost-robot",
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
    "id": "charging-station",
    "title": "The Charging Station",
    "world": "Mint Power House",
    "concept": "while",
    "exercise": "debug",
    "group": "workshop",
    "kind": "program",
    "coins": [
      "half",
      "full"
    ],
    "source": "/levels/charging-station.py",
    "runtime": "/runner-10/",
    "storage": "cfs:workshop:charge:v1",
    "missionTitle": "Keep charging until the sensor changes.",
    "mission": "The battery starts empty, but the starter program tries to open the exit immediately. Fix its while condition. Stop charging when the full sensor becomes true.",
    "intro": "Step the program, observe the battery sensor, and fix the while condition.",
    "goal": "Charging Station",
    "death": "Check your program and try again.",
    "log": "Press or hold Space to advance one action at a time.",
    "reference": "Use while. For loops are not enabled. Put charge() inside your while loop. The function header and game code are locked. Use the supplied functions in the green area. Compile, then press Space to play.",
    "actions": [
      [
        "battery_full()",
        "True when all four battery cells are charged."
      ],
      [
        "charge()",
        "Charge one cell."
      ],
      [
        "open_exit()",
        "Open the exit after the battery is full."
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
    "number": 6,
    "runtimeId": 11,
    "id": "foggy-tunnel",
    "title": "The Foggy Tunnel",
    "world": "Mistwood Passage",
    "concept": "while",
    "exercise": "build",
    "group": "workshop",
    "kind": "program",
    "coins": [
      "tunnel-1",
      "tunnel-2",
      "tunnel-3"
    ],
    "source": "/levels/foggy-tunnel.py",
    "runtime": "/runner-11/",
    "storage": "cfs:workshop:foggy:v1",
    "missionTitle": "No step count. Trust your sensor.",
    "mission": "Three tunnels have different hidden lengths. Write one program that works in all three. Move until the exit sensor detects a door, then open it. Walking past an exit ends the attempt.",
    "intro": "Write a while loop using the exit sensor. Play the same program through three tunnels.",
    "goal": "Foggy Tunnel",
    "death": "Check your program and try again.",
    "log": "Press or hold Space to advance one action at a time.",
    "reference": "Use while. For loops and fixed repetition counts are not enabled here. Put move_forward() inside the while loop. The function header and game code are locked. Use the supplied functions in the green area. Compile, then press Space to play.",
    "actions": [
      [
        "exit_detected()",
        "Reports whether you have reached this tunnel's exit."
      ],
      [
        "move_forward()",
        "Move one step through the fog."
      ],
      [
        "open_exit()",
        "Open the door when the exit is detected."
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
    "number": 7,
    "id": "wrong-door",
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
