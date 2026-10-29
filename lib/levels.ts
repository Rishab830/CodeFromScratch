export type Level = {
  number: number; id: string; title: string; world: string; coins: readonly string[];
  source: string; runtime: string; storage: string; missionTitle: string;
  mission: string; intro: string; death: string; log: string;
  goal?: string; reference?: string; actions?: readonly (readonly [string,string])[];
  controls?: readonly (readonly [string,string])[];
  codeVersion?: number;
};
export const LEVELS: readonly Level[] = [
  {
    number: 1, id: 'jumping-girl', title: 'The Jumping Girl', world: 'Pastel Meadow', coins: ['below'],
    source: '/levels/jumping-girl.py', runtime: '/runner/', storage: 'cfs:jumping-girl:v2',
    missionTitle: 'Blue shouldn’t mean “boing!”',
    mission: 'Maya should move left when she touches blue. Instead, she jumps straight toward the spikes. Something in her code is a little mixed up. Reach the flag and jump across the gap along the way.',
    intro: 'Get Maya to the flag. Mind the spikes and jump across the gap.',
    death: 'Mind the spikes and the gap in the floor.',
    log: 'Watch the spikes above blue!',
  },
  {
    number: 2, id: 'blue-leap', title: 'The Blue Leap', world: 'Pastel Meadow', coins: ['above', 'below'],
    source: '/levels/blue-leap.py', runtime: '/runner-2/', storage: 'cfs:blue-leap:v2',
    missionTitle: 'This time, blue WILL make Maya jump.',
    mission: 'Get her to the flag. Explore the game, read the code, and find your own way past the spikes. There is also a small gap to jump across before the flag.',
    intro: 'This time, blue WILL make Maya jump. Reach the flag and jump across the gap.',
    death: 'Mind the spikes and the gap in the floor.',
    log: 'This time, blue WILL make Maya jump.',
  },
  {
    number: 3, id: 'confused-traffic-signal', title: 'The Confused Traffic Signal', world: 'Apricot Avenue', coins: ['first','second'],
    source: '/levels/confused-traffic-signal.py', runtime: '/runner-3/', storage: 'cfs:traffic:v1', codeVersion: 2,
    missionTitle: 'Red. Yellow. Red. Wait a minute…',
    mission: 'The signal keeps switching between red and yellow. Fix its sequence, then drive your car through the crossing to the flag.',
    intro: 'Watch the signal. Drive through the crossing when it turns green.',
    goal: 'Drive through the crossing', death: 'The crossing needs a working signal.', log: 'Use Left / Right to drive. The car waits at red and yellow.',
    reference: 'Use if, elif, and else to decide what happens for each light. Set next_color in the matching branch. The game handles the rest; the car is yours to drive.',
    actions: [['current','The current light: red, yellow, or green.'],['next_color','The colour chosen by your conditions.'],['Left / Right','Drive the car.']],
    controls: [['ArrowLeft','Drive left'],['ArrowRight','Drive right']],
  },
  {
    number: 4, id: 'lost-robot', title: 'The Lost Robot', world: 'Lavender Depot', coins: ['loop','route'],
    source: '/levels/lost-robot.py', runtime: '/runner-4/', storage: 'cfs:robot:v1',
    missionTitle: 'A busy robot, going nowhere.',
    mission: 'Your robot repeats its instructions, but they lead in circles. Trace a route through the depot to the green dock. Compile your program, then step the robot along it yourself.',
    intro: 'Press or hold Space to run the next instruction. Reach the green dock.',
    goal: 'Guide the robot to its dock', death: 'That instruction ran the robot into a crate.', log: 'Press or hold Space to step through your program.',
    reference: 'robot_program() returns a list of directions. Space executes one instruction at a time. The sequence repeats when it ends.',
    actions: [['right / left','One tile sideways.'],['up / down','One tile vertically.'],['Space','Execute the next instruction.']],
    controls: [[' ','Step robot']],
  },
  {
    number: 5, id: 'endless-coin-collector', title: 'The Endless Coin Collector', world: 'Honey Workshop', coins: ['coin-1','coin-2','coin-3','coin-4','coin-5'],
    source: '/levels/endless-coin-collector.py', runtime: '/runner-5/', storage: 'cfs:collector:v1',
    missionTitle: 'Five coins. Why is it still counting?',
    mission: 'The collector must stop after exactly five coins to unlock the exit. It keeps going instead. Fix its condition, start the machine, and walk through the unlocked door.',
    intro: 'Walk to the collector and press Space. Watch its count, then reach the exit.',
    goal: 'Stop at five and unlock the exit', death: 'The collector needs another try.', log: 'Move with Left / Right. Press Space beside the collector to start it.',
    reference: 'should_collect(count) decides whether the machine collects another coin. Starting the machine commits it to that condition until it stops. Restart clears the machine count; your coin badges stay saved.',
    actions: [['count','Coins collected by the machine this attempt.'],['True / False','Continue collecting, or stop.'],['Space','Start the collector when nearby.']],
    controls: [['ArrowLeft','Move left'],['ArrowRight','Move right'],[' ','Interact']],
  },
  {
    number: 6, id: 'wrong-door', title: 'The Wrong Door', world: 'Rosewood Hall', coins: ['first','second'],
    source: '/levels/wrong-door.py', runtime: '/runner-6/', storage: 'cfs:doors:v1',
    missionTitle: 'The password fits. The door doesn’t.',
    mission: 'Three doors, one way out. Read the terminal note and enter the password below the game. The program opens the wrong door. Fix its logic, use the terminal, and walk through the correct exit.',
    intro: 'Enter the password below, then press Space beside the terminal. Watch which door opens.',
    goal: 'Open the correct door', death: 'That door leads to a dead end.', log: 'Enter a password, press Space near the terminal, then walk to the door.',
    reference: 'choose_door(password) returns a door index, or None to deny entry. Doors are numbered from left to right starting at 0. The symbols and password note are in the room.',
    actions: [['password','The text you enter below the game.'],['0 / 1 / 2','The left, middle, and right doors.'],['None','Do not open a door.'],['Space','Submit at the terminal.']],
    controls: [['ArrowLeft','Move left'],['ArrowRight','Move right'],[' ','Use terminal']],
  },
  {
    number: 7, id: 'final-escape', title: 'The Final Escape', world: 'Moonlit Observatory', coins: ['first','second'],
    source: '/levels/final-escape.py', runtime: '/runner-7/', storage: 'cfs:escape:v1',
    missionTitle: 'One room. Everything you’ve learned.',
    mission: 'The exit has no power and a locked latch. Repair the console program using sequences, loops, and conditions. Activate it, watch the room respond, and make your final escape.',
    intro: 'Press Space beside the console to run your sequence. Power the room and escape.',
    goal: 'Power the room and escape', death: 'The exit is still locked.', log: 'Press Space near the console. Watch the power cells, latch, and exit.',
    reference: 'escape_plan() builds a sequence of commands. The console executes them in order after you activate it. Observe what each command changes.',
    actions: [['power','Charge one power cell.'],['unlock','Try the exit latch.'],['open','Try opening the exit.'],['Space','Activate the console.']],
    controls: [['ArrowLeft','Move left'],['ArrowRight','Move right'],[' ','Activate console']],
  },
];
