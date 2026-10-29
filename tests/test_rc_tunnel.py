"""Manual remote control, animated sensors and a single opening attempt per run."""
import ast
import os
from pathlib import Path
import sys
import unittest
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'game'))
import pygame
import lesson_bridge
SOLUTION='    while not exit_detected():\n        move_forward()\n    open_exit()\n'

class RCTunnelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree=ast.parse((ROOT/'game/levels/foggy-tunnel.py').read_text(encoding='utf-8'));tree.body.pop();cls.ns={}
        exec(compile(tree,'foggy-tunnel','exec'),cls.ns);pygame.init()

    def make(self,body=SOLUTION):
        self.ns['COLLECTED_COINS'].clear()
        w=self.ns['World']([4,8,6])
        w.program=lesson_bridge.compile_lesson(body,self.ns['PROGRAM_NAME'],w.commands(),w.sensors(),self.ns['CONCEPT'],self.ns['LOOP_COMMANDS'],self.ns['ANIMATED_SENSORS'])
        return w

    def enter(self,w):
        while w.phase=='outside': self.assertIsNone(w.update(0.05,right=True))
        self.assertFalse(w.has_signal())

    def until(self,w,predicate,drive=False):
        for _ in range(6000):
            if predicate(): return
            result=w.update(1/60,right=drive)
            if result: self.fail(f'Unexpected {result}: {w.message}')
        self.fail('Tunnel animation did not reach its expected state')

    def test_remote_controls_outside_and_code_waits_for_entry(self):
        w=self.make();start=w.car_x
        w.update(0.1,left=True);self.assertLess(w.car_x,start)
        w.update(0.1,right=True);self.assertAlmostEqual(w.car_x,start)
        for _ in range(120): self.assertIsNone(w.update(1/60,action=True))
        self.assertEqual(w.actions,0);self.assertEqual(w.scans,0);self.assertTrue(w.has_signal())
        self.enter(w)
        self.until(w,lambda:w.phase=='scan')
        x=w.car_x
        w.update(0.15,left=True)
        self.assertEqual(w.car_x,x);self.assertEqual(w.phase,'scan')
        self.assertEqual(w.scans,1)
        self.until(w,lambda:w.phase=='drive')
        self.assertEqual(w.position,0)
        w.update(0.15)
        self.assertGreater(w.car_x,x);self.assertLess(w.car_x,x+18)
        self.assertEqual(w.position,0)
        self.until(w,lambda:w.position==1)
        self.assertEqual(w.car_x,x+18)

    def test_each_sensor_call_and_gate_opening_have_separate_animations(self):
        w=self.make();self.enter(w)
        self.until(w,lambda:w.phase=='open')
        self.assertEqual(w.scans,5)
        self.assertEqual(w.open_attempts,1)
        self.assertFalse(w.door_open)
        self.assertEqual(w.door_lift,0)
        w.update(0.3)
        self.assertGreater(w.door_lift,0);self.assertLess(w.door_lift,1)
        self.assertFalse(w.door_open)
        self.until(w,lambda:w.phase=='exit')
        self.assertTrue(w.door_open);self.assertEqual(w.door_lift,1)

    def test_a_second_open_is_an_error_even_after_the_first_open_succeeded(self):
        w=self.make(SOLUTION+'    open_exit()\n');self.enter(w)
        with self.assertRaisesRegex(ValueError,'^open exit can only be attempted once$'):
            for _ in range(3000): w.update(1/60)
        self.assertTrue(w.door_open)
        self.assertEqual(w.open_attempts,1)
        self.assertEqual(w.round,0)
        self.assertEqual(w.position,4)

    def test_an_early_open_uses_the_attempt_and_a_second_attempt_is_rejected(self):
        w=self.make('    while not exit_detected():\n        open_exit()\n');self.enter(w)
        self.until(w,lambda:w.phase=='open')
        self.assertEqual(w.open_attempts,1);self.assertFalse(w.open_here)
        with self.assertRaisesRegex(ValueError,'open exit can only be attempted once'):
            for _ in range(300): w.update(1/60)
        self.assertFalse(w.door_open)

    def test_open_allowance_resets_only_for_a_new_tunnel_or_a_new_attempt(self):
        w=self.make();self.enter(w)
        self.until(w,lambda:w.round==1)
        self.assertEqual(w.phase,'outside');self.assertTrue(w.has_signal())
        self.assertEqual(w.open_attempts,0);self.assertEqual(w.position,0)
        self.enter(w);self.until(w,lambda:w.phase=='open')
        self.assertEqual(w.open_attempts,1)
        restarted=self.make()
        self.assertEqual(restarted.open_attempts,0)

    def test_correct_code_clears_three_runs_and_saves_all_coins(self):
        w=self.make();result=None
        for _ in range(6000):
            result=w.update(1/60,right=True)
            if result: break
        self.assertEqual(result,'won');self.assertEqual(w.round,3)
        self.assertEqual(w.actions,4+8+6+3)
        self.assertEqual(w.scans,4+1+8+1+6+1)
        self.assertEqual(self.ns['COLLECTED_COINS'],set(self.ns['COIN_NAMES']))

    def test_scene_draws_opaque_entry_sensor_checks_opening_and_restored_signal(self):
        w=self.make();surface=pygame.Surface((320,180));small=pygame.font.Font(None,10);title=pygame.font.Font(None,16)
        self.ns['draw_scene'](surface,w,small,title)
        self.enter(w);self.until(w,lambda:w.phase=='scan')
        self.ns['draw_scene'](surface,w,small,title)
        self.until(w,lambda:w.phase=='open');w.update(0.3)
        self.ns['draw_scene'](surface,w,small,title)
        self.until(w,lambda:w.phase=='between')
        self.ns['draw_scene'](surface,w,small,title)

if __name__=='__main__': unittest.main()
