export const LEVELS = [
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
] as const;
export type Level = typeof LEVELS[number];
