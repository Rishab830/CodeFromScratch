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
 'bridge-builder': '    for i in range(10):\n        place_plank()\n',
 'lost-robot': '    for i in range(3):\n        move_left()\n    for i in range(2):\n        move_up()\n    for i in range(3):\n        move_left()\n',
 'foggy-tunnel': '    while not exit_detected():\n        move_forward()\n    open_exit()\n',
 'rocket-launch': '    if power_on():\n        if fuel_ready():\n            launch()\n        else:\n            refuel()\n    else:\n        wait_for_power()\n',
 'greenhouse-grid': '    for plant in range(3):\n        for stage in range(3):\n            water_plant(plant)\n',
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
        world.program=lesson_bridge.compile_lesson(starter if body is None else body, ns['PROGRAM_NAME'], world.commands(), world.sensors(), ns['CONCEPT'], ns['LOOP_COMMANDS'], ns.get('ANIMATED_SENSORS',()))
        return world

    def finish(self, world, action=True, drive=False):
        for _ in range(200):
            result=world.update(0.25,action,right=True) if drive else world.update(0.25,action)
            if result: return result
        return None

    def test_each_solution_wins_by_manual_steps_and_draws(self):
        for slug,body in SOLUTIONS.items():
            with self.subTest(slug=slug):
                world=self.make(slug,body)
                if slug=='greenhouse-grid': world.x=49
                result=self.finish(world,drive=slug=='foggy-tunnel')
                if slug=='greenhouse-grid':
                    self.assertIsNone(result)
                    self.assertEqual(world.stages,[3,3,3])
                    for _ in range(55): world.update(0.05,right=True)
                    self.assertTrue(world.has_key)
                    for _ in range(13): world.update(0.05,right=True)
                    world.update(0.01,True)
                    for _ in range(20): world.update(0.05)
                    for _ in range(15):
                        result=world.update(0.05,right=True)
                        if result: break
                if slug=='bridge-builder':
                    self.assertIsNone(result)
                    for _ in range(80):
                        result=world.update(0.05,right=True)
                        if result: break
                self.assertEqual(result,'won')
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
        for slug in ('greenhouse-grid',):
            with self.subTest(slug=slug):
                world=self.make(slug)
                world.x=49
                self.assertEqual(self.finish(world),'dead')

    def test_bridge_movement_is_independent_of_building_and_stops_on_key_release(self):
        world=self.make('bridge-builder',SOLUTIONS['bridge-builder'])
        self.assertIsNone(world.update(0.2,left=True))
        self.assertLess(world.x,66)
        left_x=world.x
        self.assertIsNone(world.update(0.2,action=True,right=True))
        self.assertGreater(world.x,left_x)
        self.assertEqual(world.planks,1)
        stopped_x=world.x
        self.assertIsNone(world.update(0.5))
        self.assertEqual(world.x,stopped_x)

    def test_complete_bridge_never_walks_or_wins_without_movement_input(self):
        world=self.make('bridge-builder',SOLUTIONS['bridge-builder'])
        self.assertIsNone(self.finish(world))
        self.assertEqual(world.planks,10)
        self.assertEqual(world.x,66)
        self.assertEqual(world.y,141)
        self.assertEqual(self.games['bridge-builder'][0]['COLLECTED_COINS'],set())
        # Space held past the end must not restart the loop and place extra planks.
        self.assertTrue(world.program_done)
        for _ in range(20): self.assertIsNone(world.update(0.05,right=True))
        right_x=world.x
        for _ in range(10): self.assertIsNone(world.update(0.05,left=True))
        self.assertLess(world.x,right_x)
        stopped_x=world.x
        self.assertIsNone(world.update(1.0))
        self.assertEqual(world.x,stopped_x)

    def test_bridge_starter_leaves_a_real_gap_that_the_player_falls_through(self):
        world=self.make('bridge-builder')
        self.assertIsNone(self.finish(world))
        self.assertEqual(world.planks,5)
        result=None
        for _ in range(100):
            result=world.update(0.05,right=True)
            if result: break
        self.assertEqual(result,'dead')
        self.assertGreater(world.y,180)
        self.assertNotIn('first',self.games['bridge-builder'][0]['COLLECTED_COINS'])

    def test_one_space_tap_runs_the_entire_bridge_loop_after_release(self):
        for count in (5,10,12):
            with self.subTest(count=count):
                world=self.make('bridge-builder',f'    for plank in range({count}):\n        place_plank()\n')
                for _ in range(10): self.assertIsNone(world.update(0.05))
                self.assertEqual(world.planks,0)
                self.assertIsNone(world.update(0.01,action=True))
                self.assertEqual(world.planks,1)
                for _ in range(100): self.assertIsNone(world.update(0.05,action=False))
                self.assertEqual(world.planks,count)
                self.assertTrue(world.program_done)
                self.assertEqual(world.x,66)
                for _ in range(10): self.assertIsNone(world.update(0.25,action=True))
                self.assertEqual(world.planks,count)

    def test_nine_planks_leave_a_gap_but_ten_allow_a_manual_crossing(self):
        for count,expected in ((9,'dead'),(10,'won')):
            with self.subTest(count=count):
                world=self.make('bridge-builder',f'    for plank in range({count}):\n        place_plank()\n')
                world.update(0.01,action=True)
                self.assertIsNone(self.finish(world,action=False))
                result=None
                for _ in range(100):
                    result=world.update(0.05,right=True)
                    if result: break
                self.assertEqual(result,expected)

    def test_parcels_require_a_correct_decision_for_every_colour(self):
        world=self.make('parcel-sorter',SOLUTIONS['parcel-sorter'].replace('send_middle()','send_left()'),colours=['red','blue','yellow','yellow','red','blue'])
        self.assertEqual(self.finish(world),'dead')
        self.assertEqual(world.sorted,1)

    def test_side_parcels_ride_the_belt_then_deposit_before_the_next_arrives(self):
        for colour,direction in (('red',-1),('yellow',1)):
            with self.subTest(colour=colour):
                world=self.make('parcel-sorter',SOLUTIONS['parcel-sorter'],colours=[colour,'blue','red','yellow','red','blue'])
                self.assertIsNone(world.update(0.01,True))
                self.assertEqual(world.phase,'travel')
                self.assertIsNone(world.update(0.325,True))
                self.assertGreater((world.parcel_x-155)*direction,0)
                self.assertGreater(world.belt_offset*direction,0)
                self.assertEqual(world.actions,1)  # Holding Space cannot replace the moving box.
                self.assertEqual(world.sorted,0)
                self.assertEqual(world.parcel_colour(),colour)
                world.update(0.325,False)
                self.assertEqual(world.phase,'deposit')
                belt=world.belt_offset
                world.update(0.25,True)
                self.assertGreater(world.parcel_y,71)
                self.assertEqual(world.belt_offset,belt)
                self.assertEqual(world.sorted,0)
                ns,_=self.games['parcel-sorter']
                ns['draw_scene'](pygame.Surface((320,180)),world,pygame.font.Font(None,10),pygame.font.Font(None,16))
                self.assertIsNone(world.update(0.31,True))
                self.assertEqual(world.sorted,1)
                self.assertEqual(world.phase,'arrive')
                self.assertEqual(world.parcel_colour(),'blue')
                self.assertEqual(world.parcel_x,155)
                world.update(0.2,True)
                self.assertGreater(world.parcel_y,40)
                self.assertLess(world.parcel_y,71)
                self.assertEqual(world.actions,1)
                world.update(0.2,False)
                self.assertEqual(world.phase,'ready')
                self.assertEqual(world.parcel_y,71)

    def test_middle_delivery_and_next_parcel_do_not_move_the_belt(self):
        world=self.make('parcel-sorter',SOLUTIONS['parcel-sorter'],colours=['blue','red','yellow','blue','red','yellow'])
        world.update(0.01,True)
        self.assertEqual(world.phase,'deposit')
        for _ in range(24):
            self.assertIsNone(world.update(0.05,False))
            self.assertEqual(world.parcel_x,155)
            self.assertEqual(world.belt_offset,0)
        self.assertEqual(world.phase,'ready')
        self.assertEqual(world.sorted,1)
        self.assertEqual(world.parcel_colour(),'red')

    def test_wrong_delivery_loses_only_after_the_box_is_inside_the_chosen_bay(self):
        world=self.make('parcel-sorter','    if parcel_colour() != "":\n        send_right()\n',colours=['red']*6)
        self.assertIsNone(world.update(0.01,True))
        self.assertIsNone(world.update(0.65,True))
        self.assertEqual(world.parcel_x,247)  # Animate the student's choice, even when wrong.
        self.assertEqual(world.phase,'deposit')
        self.assertIsNone(world.update(0.3,True))
        self.assertTrue(world.parcel_visible)
        self.assertEqual(world.sorted,0)
        self.assertEqual(world.update(0.25,True),'dead')
        self.assertFalse(world.parcel_visible)
        self.assertEqual(world.phase,'failed')
        self.assertEqual(world.actions,1)
        self.assertEqual(world.deposited['right'],1)
        self.assertEqual(world.sorted,0)
        self.assertEqual(world.parcel_colour(),'red')

    def test_last_parcel_must_finish_its_deposit_before_winning(self):
        world=self.make('parcel-sorter',SOLUTIONS['parcel-sorter'],colours=['blue']*6)
        for _ in range(5):
            world.update(0.01,True)
            self.assertIsNone(world.update(0.55,False))
            self.assertIsNone(world.update(0.4,False))
        self.assertEqual(world.sorted,5)
        self.assertIsNone(world.update(0.01,True))
        self.assertIsNone(world.update(0.3,False))
        self.assertEqual(world.sorted,5)
        self.assertNotIn('second',self.games['parcel-sorter'][0]['COLLECTED_COINS'])
        self.assertEqual(world.update(0.25,False),'won')
        self.assertEqual(world.sorted,6)
        self.assertFalse(world.parcel_visible)
        self.assertEqual(world.phase,'complete')

    def test_for_challenge_does_not_accept_an_unrolled_or_while_solution(self):
        for body in ('    move_left()\n','    while True:\n        move_left()\n','    for i in range(1):\n        pass\n    move_left()\n'):
            with self.subTest(body=body),self.assertRaises(ValueError): self.make('lost-robot',body)

    def test_robot_moves_between_tiles_and_finishes_a_tapped_action(self):
        world=self.make('lost-robot',SOLUTIONS['lost-robot'])
        start_x,start_y=world.x,world.y
        self.assertIsNone(world.update(0.01,True))
        self.assertTrue(world.moving)
        self.assertEqual((world.x,world.y),(start_x,start_y))
        self.assertIsNone(world.update(0.125,True))
        self.assertEqual(world.cell,(8,5))
        self.assertLess(world.x,start_x)
        self.assertGreater(world.x,start_x-24)
        self.assertEqual(world.y,start_y)
        self.assertEqual(world.actions,1)  # Holding Space must not skip a moving step.
        self.assertIsNone(world.update(0.375,False))
        self.assertEqual(world.cell,(7,5))
        self.assertEqual((world.x,world.y),(start_x-24,start_y))
        self.assertFalse(world.moving)
        self.assertIsNone(world.update(5,False))
        self.assertEqual(world.cell,(7,5))
        self.assertEqual(world.actions,1)

    def test_robot_bad_steps_animate_to_the_wall_before_game_over(self):
        cases=[('right',(8,5)),('up',(8,5)),('down',(8,5)),('left',(2,3))]
        ns,_=self.games['lost-robot']
        for direction,cell in cases:
            with self.subTest(direction=direction):
                world=self.make('lost-robot',f'    for i in range(1):\n        move_{direction}()\n')
                world.cell=cell
                world.x,world.y=ns['robot_point'](cell)
                start_x,start_y=world.x,world.y
                self.assertIsNone(world.update(0,True))
                self.assertIsNone(world.update(0.01,False))
                self.assertNotEqual((world.x,world.y),(start_x,start_y))
                self.assertFalse(world.crashed)
                # Even a very slow frame stops at first contact, without tunnelling.
                self.assertEqual(world.update(2,True),'dead')
                self.assertTrue(world.crashed)
                self.assertFalse(world.moving)
                self.assertEqual(world.cell,cell)
                self.assertEqual(world.actions,1)
                self.assertLess(abs(world.x-start_x)+abs(world.y-start_y),12)
                robot=pygame.Rect(round(world.x)-7,round(world.y)-9,14,16)
                self.assertTrue(any(
                    robot.right==wall.left and robot.top<wall.bottom and robot.bottom>wall.top or
                    robot.left==wall.right and robot.top<wall.bottom and robot.bottom>wall.top or
                    robot.bottom==wall.top and robot.left<wall.right and robot.right>wall.left or
                    robot.top==wall.bottom and robot.left<wall.right and robot.right>wall.left
                    for wall in ns['WALLS']))
                self.assertFalse(any(robot.colliderect(wall) for wall in ns['WALLS']))
                ns['draw_scene'](pygame.Surface((320,180)),world,pygame.font.Font(None,10),pygame.font.Font(None,16))

    def test_robot_coins_and_completion_wait_for_tile_arrival(self):
        world=self.make('lost-robot','    for i in range(2):\n        move_left()\n')
        for dt,action in ((0.01,True),(0.5,False),(0.01,True),(0.25,False)):
            self.assertIsNone(world.update(dt,action))
        self.assertNotIn('loop',self.games['lost-robot'][0]['COLLECTED_COINS'])
        self.assertIsNone(world.update(0.25,False))
        self.assertIn('loop',self.games['lost-robot'][0]['COLLECTED_COINS'])
        ns,_=self.games['lost-robot']
        world=self.make('lost-robot','    for i in range(1):\n        move_left()\n')
        world.cell=(3,3);world.x,world.y=ns['robot_point'](world.cell)
        self.assertIsNone(world.update(0.01,True))
        self.assertIsNone(world.update(0.25,True))
        self.assertEqual(world.cell,(3,3))
        self.assertIsNone(world.update(0.25,True))
        self.assertEqual(world.cell,(2,3))
        self.assertEqual(world.update(0.01,True),'won')

    def test_while_challenge_rejects_fixed_for_loops_and_unrolled_moves(self):
        for body in ('    for i in range(6):\n        move_forward()\n    open_exit()\n','    move_forward()\n    open_exit()\n','    while False:\n        pass\n    move_forward()\n'):
            with self.subTest(body=body),self.assertRaises(ValueError): self.make('foggy-tunnel',body)

    def test_foggy_program_adapts_to_three_different_hidden_distances(self):
        world=self.make('foggy-tunnel',SOLUTIONS['foggy-tunnel'],lengths=[4,8,6])
        self.assertEqual(self.finish(world,drive=True),'won')
        self.assertEqual(world.round,3)
        self.assertEqual(world.actions,4+8+6+3)
        self.assertEqual(self.games['foggy-tunnel'][0]['COLLECTED_COINS'],{'tunnel-1','tunnel-2','tunnel-3'})

    def test_foggy_overshoot_or_premature_open_loses(self):
        world=self.make('foggy-tunnel','    while True:\n        move_forward()\n',lengths=[4,8,6])
        self.assertEqual(self.finish(world,drive=True),'dead')
        world=self.make('foggy-tunnel','    while not exit_detected():\n        open_exit()\n',lengths=[4,8,6])
        with self.assertRaisesRegex(ValueError,'open exit can only be attempted once'):
            self.finish(world,drive=True)

    def test_endless_non_progress_loop_is_bounded_and_trace_restored(self):
        previous=sys.gettrace()
        world=self.make('foggy-tunnel','    while True:\n        pass\n')
        with self.assertRaisesRegex(ValueError,'not making progress'): self.finish(world,drive=True)
        self.assertIs(sys.gettrace(),previous)

    def test_nested_bonus_rules_are_explicit(self):
        with self.assertRaises(ValueError): self.make('rocket-launch','    if power_on() and fuel_ready():\n        launch()\n')
        with self.assertRaises(ValueError): self.make('greenhouse-grid','    for plant in range(3):\n        water_plant(plant)\n')

    def test_invalid_runtime_access_is_rejected(self):
        for body in ('    import os\n','    return []\n','    launch.__class__\n','    eval("1")\n'):
            with self.subTest(body=body),self.assertRaises(ValueError): self.make('rocket-launch',body)

if __name__=='__main__': unittest.main()
