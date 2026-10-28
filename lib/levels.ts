export const LEVELS = [
  {
    number: 1, id: 'jumping-girl', title: 'The Jumping Girl', world: 'Pastel Meadow',
    source: '/levels/jumping-girl.py', runtime: '/runner/', storage: 'cfs:jumping-girl:v2',
    missionTitle: 'Blue shouldn’t mean “boing!”',
    mission: 'Maya should move left when she touches blue. Instead, she jumps straight toward the spikes. Something in her code is a little mixed up.',
    intro: 'Get Maya to the flag. Mind the spikes.',
    death: 'Those spikes are a little too pointy.',
    log: 'Watch the spikes above blue!',
  },
  {
    number: 2, id: 'blue-leap', title: 'The Blue Leap', world: 'Pastel Meadow',
    source: '/levels/blue-leap.py', runtime: '/runner-2/', storage: 'cfs:blue-leap:v2',
    missionTitle: 'This time, blue WILL make Maya jump.',
    mission: 'Get her to the flag. Explore the game, read the code, and find your own way past the spikes.',
    intro: 'This time, blue WILL make Maya jump. Reach the flag.',
    death: 'Those spikes are a little too pointy.',
    log: 'This time, blue WILL make Maya jump.',
  },
] as const;
export type Level = typeof LEVELS[number];
