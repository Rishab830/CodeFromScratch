export const LEVELS = [
  {
    number: 1, id: 'jumping-girl', title: 'The Jumping Girl', world: 'Pastel Meadow',
    source: '/levels/jumping-girl.py', runtime: '/runner/index.html', storage: 'cfs:jumping-girl:v2',
    missionTitle: 'Blue shouldn’t mean “boing!”',
    mission: 'Maya should move left when she touches blue. Instead, she jumps straight toward the spikes. Something in her code is a little mixed up.',
    intro: 'Get Maya to the flag. Mind the spikes.',
    goal: 'Blue should move Maya left. Avoid the spikes.',
    death: 'Those spikes are a little too pointy.',
    log: 'Watch the spikes above blue!',
  },
  {
    number: 2, id: 'blue-leap', title: 'The Blue Leap', world: 'Cloud Crossing',
    source: '/levels/blue-leap.py', runtime: '/runner-2/index.html', storage: 'cfs:blue-leap:v1',
    missionTitle: 'This time, blue WILL make Maya jump.',
    mission: 'Get her to the flag. Explore the game, read the code, and find your own way across.',
    intro: 'This time, blue WILL make Maya jump. Reach the flag.',
    goal: 'This time, blue WILL make Maya jump.',
    death: 'Maya didn’t make it to solid ground.',
    log: 'This time, blue WILL make Maya jump.',
  },
] as const;
export type Level = typeof LEVELS[number];
