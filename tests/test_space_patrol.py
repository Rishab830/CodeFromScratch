"""Live weapon conditions, exact ammunition and manual flight in Space Patrol."""
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

WHILE='    while enemy_visible():\n        shoot()\n'
GUARDED='    while bullets_left() > 0:\n        if enemy_visible():\n            shoot()\n'
FOR_IF='    for bullet in range(30):\n        if enemy_visible():\n            shoot()\n'

class SpacePatrolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=(ROOT/'game/levels/space-patrol.py').read_text(encoding='utf-8')
        tree=ast.parse(source);tree.body.pop();cls.ns={}
        exec(compile(tree,'space-patrol','exec'),cls.ns)
        cls.starter=source.split('# EDIT START\n')[1].split('    # EDIT END')[0]
        pygame.init()

    def make(self,body=WHILE,hostile_fire=False):
        self.ns['COLLECTED_COINS'].clear()
        world=self.ns['World'](hostile_fire=hostile_fire)
        world.program=lesson_bridge.compile_lesson(body,self.ns['PROGRAM_NAME'],world.commands(),world.sensors(),self.ns['CONCEPT'],self.ns['LOOP_COMMANDS'])
        return world

    def play(self,world,seconds=90,pilot=False):
        direction=1
        for _ in range(int(seconds*60)):
            if pilot:
                if world.x>275: direction=-1
                if world.x<45: direction=1
            result=world.update(1/60,action=True,left=pilot and direction<0,right=pilot and direction>0)
            if result or world.cleared: return result
        self.fail('The combat did not finish within its time budget')

    def test_both_loop_solutions_save_exactly_thirty_bullets_and_need_manual_exit(self):
        for body in (WHILE,GUARDED,FOR_IF):
            with self.subTest(body=body):
                world=self.make(body)
                self.assertIsNone(self.play(world))
                self.assertEqual((world.defeated,world.shots,world.ammo,world.wasted),(10,30,0,0))
                self.assertEqual(self.ns['COLLECTED_COINS'],{'wave-five','sector-clear'})
                self.assertIsNone(world.update(2))
                for _ in range(100):
                    result=world.update(1/60,up=True)
                    if result: break
                self.assertEqual(result,'won')

    def test_unconditional_starter_wastes_shots_and_cannot_clear_all_enemies(self):
        world=self.make(self.starter)
        self.assertEqual(self.play(world),'dead')
        self.assertGreater(world.wasted,0)
        self.assertEqual(world.ammo,0)
        self.assertLess(world.defeated,10)

    def test_compiling_and_flying_do_not_arm_the_weapon(self):
        world=self.make()
        for _ in range(300): self.assertIsNone(world.update(1/60,right=True))
        self.assertFalse(world.armed)
        self.assertEqual((world.shots,world.spawned,world.actions),(0,0,0))

    def test_ship_moves_in_four_directions_and_stays_in_the_arena(self):
        world=self.make()
        world.update(0.25,left=True);self.assertLess(world.x,160)
        world.update(0.25,right=True);self.assertAlmostEqual(world.x,160)
        world.update(0.25,up=True);self.assertLess(world.y,143)
        world.update(0.25,down=True);self.assertAlmostEqual(world.y,143)
        world.update(100,left=True,up=True);self.assertEqual((world.x,world.y),(12,32))
        world.update(100,right=True,down=True);self.assertEqual((world.x,world.y),(308,155))

    def test_armed_while_rechecks_the_sensor_without_freezing_between_waves(self):
        world=self.make(GUARDED)
        world.update(0.01,action=True)
        for _ in range(30): self.assertIsNone(world.update(0.01))
        self.assertEqual(world.shots,0)
        for _ in range(120): world.update(0.01)
        self.assertGreater(world.shots,0)

    def test_enemy_takes_three_actual_hits_and_final_bullet_finishes_before_ammo_loss(self):
        world=self.make()
        world.armed=True;world.spawn_enemy();world.program=None
        for hit in range(3):
            world.perform('shoot')
            self.assertEqual(world.defeated,0)
            while world.bullets: world.update(0.01)
            if hit<2: self.assertEqual(world.enemy['hp'],2-hit)
        self.assertEqual(world.defeated,1)
        world.defeated=9;world.spawn_enemy();world.enemy['hp']=1;world.ammo=1
        world.perform('shoot')
        self.assertEqual(world.ammo,0)
        self.assertFalse(world.cleared)
        while world.bullets: self.assertIsNone(world.update(0.01))
        self.assertTrue(world.cleared)
        self.assertFalse(world.finished)  # Fly to the beacon to finish.

    def test_stationary_ship_is_vulnerable_and_active_piloting_can_clear_the_sector(self):
        stationary=self.make(hostile_fire=True)
        self.assertEqual(self.play(stationary),'dead')
        self.assertEqual(stationary.shields,0)
        flying=self.make(hostile_fire=True)
        self.assertIsNone(self.play(flying,pilot=True))
        self.assertEqual(flying.defeated,10)
        self.assertGreater(flying.shields,0)

    def test_space_scene_draws_preview_live_combat_and_exit(self):
        world=self.make()
        surface=pygame.Surface((320,180));small=pygame.font.Font(None,10);title=pygame.font.Font(None,16)
        self.ns['draw_scene'](surface,world,small,title)
        world.update(0.01,action=True)
        for _ in range(180): world.update(1/60)
        self.ns['draw_scene'](surface,world,small,title)
        self.play(world)
        self.ns['draw_scene'](surface,world,small,title)

if __name__=='__main__': unittest.main()
