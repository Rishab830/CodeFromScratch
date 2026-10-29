"""Execute learner programs one real game action at a time."""
import ast
import os
from pathlib import Path
import sys
import unittest

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'game'))
import lesson_bridge
import pygame

SOLUTIONS = {
 'parcel-sorter': '    if parcel_colour() == "red":\n        send_left()\n    elif parcel_colour() == "blue":\n        send_middle()\n    else:\n        send_right()\n',
 'bridge-builder': '    for i in range(3):\n        place_plank()\n    cross_bridge()\n',
 'lost-robot': '    for i in range(3):\n        move_left()\n    for i in range(2):\n        move_up()\n    for i in range(3):\n        move_left()\n',
 'charging-station': '    while not battery_full():\n        charge()\n    open_exit()\n',
 'foggy-tunnel': '    while not exit_detected():\n        move_forward()\n    open_exit()\n',
 'rocket-launch': '    if power_on():\n        if fuel_ready():\n            launch()\n        else:\n            refuel()\n    else:\n        wait_for_power()\n',
 'greenhouse-grid': '    for row in range(3):\n        for column in range(3):\n            water_cell(row, column)\n    open_exit()\n',
 'final-escape': '    for row in range(2):\n        for column in range(3):\n            power_cell(row, column)\n    if all_powered():\n        unlock_exit()\n        open_exit()\n',
}

class WorkshopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games={}
        for slug in SOLUTIONS:
            source=(ROOT/'game/levels'/f'{slug}.py').read_text(encoding='utf-8')
            tree=ast.parse(source);tree.body.pop()
            ns={};exec(compile(tree,slug,'exec'),ns)
            body=source.split('# EDIT START\n')[1].split('    # EDIT END')[0]
            cls.games[slug]=(ns,body)
        pygame.init()

    def make(self, slug, body=None, **kwargs):
        ns,starter=self.games[slug]
        ns['COLLECTED_COINS'].clear()
        world=ns['World'](**kwargs)
        world.program=lesson_bridge.compile_lesson(starter if body is None else body, ns['PROGRAM_NAME'], world.commands(), world.sensors(), ns['CONCEPT'], ns['LOOP_COMMANDS'])
        return world

    def finish(self, world, action=True):
        for _ in range(200):
            result=world.update(0.25,action)
            if result: return result
        return None

    def test_each_solution_wins_by_manual_steps_and_draws(self):
        for slug,body in SOLUTIONS.items():
            with self.subTest(slug=slug):
                world=self.make(slug,body)
                self.assertEqual(self.finish(world),'won')
                ns,_=self.games[slug]
                ns['draw_scene'](pygame.Surface((320,180)),world,pygame.font.Font(None,10),pygame.font.Font(None,16))

    def test_compiling_and_waiting_cannot_advance_or_win(self):
        for slug,body in SOLUTIONS.items():
            with self.subTest(slug=slug):
                world=self.make(slug,body)
                self.assertIsNone(self.finish(world,action=False))
                self.assertEqual(world.actions,0)

    def test_blank_independent_challenges_start_with_only_pass(self):
        for slug in ('parcel-sorter','lost-robot','foggy-tunnel','rocket-launch','final-escape'):
            with self.subTest(slug=slug):
                self.assertEqual(self.games[slug][1].strip(),'pass')
                world=self.make(slug)
                self.assertIsNone(self.finish(world))
                self.assertEqual(world.actions,0)

    def test_debugging_starters_fail_for_the_intended_reason(self):
        for slug in ('bridge-builder','charging-station','greenhouse-grid'):
            with self.subTest(slug=slug):
                world=self.make(slug)
                self.assertEqual(self.finish(world),'dead')

    def test_parcels_require_a_correct_decision_for_every_colour(self):
        world=self.make('parcel-sorter',SOLUTIONS['parcel-sorter'].replace('send_middle()','send_left()'),colours=['red','blue','yellow','yellow','red','blue'])
        self.assertEqual(self.finish(world),'dead')
        self.assertEqual(world.sorted,1)

    def test_for_challenge_does_not_accept_an_unrolled_or_while_solution(self):
        for body in ('    move_left()\n','    while True:\n        move_left()\n','    for i in range(1):\n        pass\n    move_left()\n'):
            with self.subTest(body=body),self.assertRaises(ValueError): self.make('lost-robot',body)

    def test_while_challenge_rejects_fixed_for_loops_and_unrolled_moves(self):
        for body in ('    for i in range(6):\n        move_forward()\n    open_exit()\n','    move_forward()\n    open_exit()\n','    while False:\n        pass\n    move_forward()\n'):
            with self.subTest(body=body),self.assertRaises(ValueError): self.make('foggy-tunnel',body)

    def test_foggy_program_adapts_to_three_different_hidden_distances(self):
        world=self.make('foggy-tunnel',SOLUTIONS['foggy-tunnel'],lengths=[4,8,6])
        self.assertEqual(self.finish(world),'won')
        self.assertEqual(world.round,3)
        self.assertEqual(world.actions,4+8+6+3)
        self.assertEqual(self.games['foggy-tunnel'][0]['COLLECTED_COINS'],{'tunnel-1','tunnel-2','tunnel-3'})

    def test_foggy_overshoot_or_premature_open_loses(self):
        for body in ('    while True:\n        move_forward()\n','    while not exit_detected():\n        open_exit()\n'):
            with self.subTest(body=body):
                self.assertEqual(self.finish(self.make('foggy-tunnel',body,lengths=[4,8,6])),'dead')

    def test_while_sensor_is_checked_again_after_each_player_action(self):
        world=self.make('charging-station',SOLUTIONS['charging-station'])
        self.assertIsNone(world.update(0.25,True));self.assertEqual(world.battery,1)
        self.assertIsNone(world.update(0.25,False));self.assertEqual(world.battery,1)
        self.assertEqual(self.finish(world),'won');self.assertEqual(world.battery,4)

    def test_endless_non_progress_loop_is_bounded_and_trace_restored(self):
        previous=sys.gettrace()
        world=self.make('foggy-tunnel','    while True:\n        pass\n')
        with self.assertRaisesRegex(ValueError,'not making progress'): world.update(0.25,True)
        self.assertIs(sys.gettrace(),previous)

    def test_nested_bonus_rules_are_explicit(self):
        with self.assertRaises(ValueError): self.make('rocket-launch','    if power_on() and fuel_ready():\n        launch()\n')
        with self.assertRaises(ValueError): self.make('greenhouse-grid','    for row in range(3):\n        water_cell(row,0)\n')

    def test_invalid_runtime_access_is_rejected(self):
        for body in ('    import os\n','    return []\n','    launch.__class__\n','    eval("1")\n'):
            with self.subTest(body=body),self.assertRaises(ValueError): self.make('rocket-launch',body)

if __name__=='__main__': unittest.main()
