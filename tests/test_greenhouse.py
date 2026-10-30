"""Exercise animated plant growth, rewards, and the player-operated exit."""
import ast
import os
from pathlib import Path
import sys
import unittest

os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'game'))
import pygame
import lesson_bridge

SOLUTION='    for plant in range(3):\n        for stage in range(3):\n            water_plant(plant)\n'


class GreenhouseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=(ROOT/'game/levels/greenhouse-grid.py').read_text()
        tree=ast.parse(source);tree.body.pop()
        cls.ns={};exec(compile(tree,'greenhouse','exec'),cls.ns)
        cls.starter=source.split('# EDIT START\n')[1].split('    # EDIT END')[0]
        pygame.init()

    def make(self,body=SOLUTION):
        self.ns['COLLECTED_COINS'].clear()
        world=self.ns['World']()
        world.program=lesson_bridge.compile_lesson(body,self.ns['PROGRAM_NAME'],world.commands(),world.sensors(),self.ns['CONCEPT'],self.ns['LOOP_COMMANDS'])
        return world

    def tick_until(self,world,predicate,seconds=30):
        for _ in range(int(seconds/.02)):
            result=world.update(.02)
            if result or predicate(): return result
        self.fail('Animation did not finish: '+world.message)

    def start(self,world):
        for _ in range(18): world.update(.02,right=True)
        self.assertAlmostEqual(world.x,48.92)
        return world.update(.02,True)

    def grow(self,world):
        self.start(world)
        return self.tick_until(world,lambda:world.program_done)

    def test_space_away_from_lever_and_idle_time_cannot_start(self):
        world=self.make();world.update(.02,True)
        for _ in range(100): world.update(.1)
        self.assertEqual(world.actions,0)
        self.assertEqual(world.stages,[0,0,0])

    def test_one_press_runs_all_nine_waterings_but_cannot_win(self):
        world=self.make();self.assertIsNone(self.grow(world))
        self.assertEqual(world.actions,9)
        self.assertEqual(world.stages,[3,3,3])
        self.assertFalse(world.door_open)
        self.assertFalse(world.has_key)
        self.assertAlmostEqual(world.x,48.92)

    def test_machine_moves_then_waters_then_grows_before_next_action(self):
        world=self.make();self.start(world)
        self.assertEqual(world.actions,1)
        self.assertEqual(world.phase,'moving')
        self.assertEqual(world.stages,[0,0,0])
        self.tick_until(world,lambda:world.phase=='watering')
        self.assertAlmostEqual(world.head_x,110)
        self.assertEqual(world.actions,1)
        self.tick_until(world,lambda:world.phase=='growing')
        world.update(.25)
        self.assertEqual(world.stages,[0,0,0])
        self.assertEqual(world.actions,1)
        self.tick_until(world,lambda:world.stages[0]==1)
        self.assertEqual(world.stages,[1,0,0])
        self.assertEqual(world.actions,1)

    def test_movement_continues_during_each_machine_phase(self):
        world=self.make();self.start(world)
        for phase in ('moving','watering','growing'):
            self.tick_until(world,lambda:world.phase==phase)
            before=world.x;world.update(.02,right=True)
            self.assertGreater(world.x,before)
            before=world.x;world.update(.02,left=True)
            self.assertLess(world.x,before)

    def test_coins_launch_from_left_and_middle_only_after_full_growth(self):
        world=self.make();self.start(world)
        self.tick_until(world,lambda:world.stages[0]==2)
        self.assertEqual(world.coin_flights,[])
        self.tick_until(world,lambda:world.stages[0]==3)
        self.assertEqual(world.coin_flights[0]['plant'],0)
        self.assertNotIn('row',self.ns['COLLECTED_COINS'])
        self.tick_until(world,lambda:'row' in self.ns['COLLECTED_COINS'])
        self.tick_until(world,lambda:world.stages[1]==3)
        self.assertEqual(world.coin_flights[0]['plant'],1)
        self.assertNotIn('garden',self.ns['COLLECTED_COINS'])
        self.tick_until(world,lambda:world.program_done)
        self.assertEqual(self.ns['COLLECTED_COINS'],{'row','garden'})
        self.assertIsNotNone(world.key_age)

    def test_starter_grows_two_plants_and_loses_after_animation(self):
        world=self.make(self.starter)
        self.assertEqual(self.grow(world),'dead')
        self.assertEqual(world.stages,[3,3,0])
        self.assertEqual(world.actions,6)
        self.assertIsNone(world.key_age)
        self.assertEqual(self.ns['COLLECTED_COINS'],{'row','garden'})

    def test_wrong_inner_loop_leaves_every_plant_small(self):
        world=self.make(SOLUTION.replace('for stage in range(3)','for stage in range(2)'))
        self.assertEqual(self.grow(world),'dead')
        self.assertEqual(world.stages,[2,2,2])
        self.assertEqual(self.ns['COLLECTED_COINS'],set())

    def test_overwatering_animates_water_before_game_over(self):
        world=self.make(SOLUTION.replace('for stage in range(3)','for stage in range(4)'))
        self.start(world)
        self.tick_until(world,lambda:world.actions==4 and world.phase=='watering')
        self.assertFalse(world.ended)
        self.assertEqual(world.stages,[3,0,0])
        self.assertEqual(self.tick_until(world,lambda:False),'dead')
        self.assertIn('Too much water',world.message)

    def test_out_of_bounds_plant_index_fails(self):
        world=self.make(SOLUTION.replace('for plant in range(3)','for plant in range(4)'))
        self.assertEqual(self.grow(world),'dead')
        self.assertEqual(world.stages,[3,3,3])

    def test_key_must_land_then_be_picked_up_by_the_girl(self):
        world=self.make();self.grow(world)
        self.assertFalse(world.has_key)
        self.assertLess(world.key_age,.75)
        world.x=247;world.update(.02)
        self.assertFalse(world.has_key)
        self.tick_until(world,lambda:world.has_key)
        self.assertTrue(world.has_key)

    def test_door_requires_all_plants_and_key_and_space_then_walk(self):
        world=self.make();world.x=293
        world.update(.02,True)
        self.assertEqual(world.door_progress,0)
        self.assertIn('all three plants',world.message)
        world=self.make();self.grow(world);world.update(1)
        world.x=293;world.update(.02,True)
        self.assertEqual(world.door_progress,0)
        self.assertIn('Pick up the key',world.message)
        world.x=247;world.update(.02)
        self.assertTrue(world.has_key)
        world.x=293;world.update(.02)
        self.assertEqual(world.door_progress,0)
        world.update(.02,True)
        self.assertGreater(world.door_progress,0)
        self.assertFalse(world.door_open)
        self.assertIsNone(self.tick_until(world,lambda:world.door_open))
        self.assertIsNone(world.update(.1))
        self.assertEqual(world.update(.2,right=True),'won')

    def test_recompile_resets_growth_machine_key_door_but_keeps_saved_coins(self):
        world=self.make();self.grow(world)
        fresh=self.ns['World']()
        self.assertEqual(fresh.stages,[0,0,0])
        self.assertFalse(fresh.running or fresh.has_key or fresh.door_open)
        self.assertIsNone(fresh.key_age)
        self.assertEqual(self.ns['COLLECTED_COINS'],{'row','garden'})

    def test_reverse_plant_order_waits_for_the_last_coin_before_winning(self):
        world=self.make(SOLUTION.replace('water_plant(plant)','water_plant(2-plant)'))
        self.start(world)
        self.tick_until(world,lambda:world.key_age is not None)
        world.x=247
        self.tick_until(world,lambda:world.has_key)
        world.x=293
        self.tick_until(world,lambda:world.stages==[3,3,3])
        self.assertTrue(world.coin_flights)
        world.update(.02,True)
        world.x=304
        self.assertIsNone(world.update(.6))
        self.assertTrue(world.door_open)
        self.assertEqual(world.update(.5),'won')
        self.assertEqual(self.ns['COLLECTED_COINS'],{'row','garden'})

    def test_all_animation_phases_draw_and_collected_coin_has_outline(self):
        world=self.make();self.start(world)
        surface=pygame.Surface((320,180))
        small,title=pygame.font.Font(None,10),pygame.font.Font(None,16)
        phases=set()
        for _ in range(1500):
            phases.add(world.phase)
            self.ns['draw_scene'](surface,world,small,title)
            world.update(.02)
            if world.program_done: break
        self.assertTrue({'moving','watering','growing'}.issubset(phases))
        coin=pygame.Surface((8,10));coin.fill((0,0,0))
        self.ns['draw_coin'](coin,0,0,True)
        self.assertEqual(coin.get_at((3,3))[:3],(0,0,0))
        self.assertEqual(coin.get_at((2,0))[:3],(174,146,98))


if __name__=='__main__': unittest.main()
