"""Nested decisions reveal hidden gifts before handling them, one action after a bomb."""
import ast
import os
import random
from pathlib import Path
import sys
import unittest
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'game'))
import pygame
import lesson_bridge
SOLUTION='    if gift_in_basket():\n        open_gift()\n        if gift_is_bomb():\n            drop()\n        else:\n            collect()\n'

class GiftCatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=(ROOT/'game/levels/gift-catcher.py').read_text(encoding='utf-8')
        tree=ast.parse(source);tree.body.pop();cls.ns={};exec(compile(tree,'gift-catcher','exec'),cls.ns)
        cls.starter=source.split('# EDIT START\n')[1].split('    # EDIT END')[0]
        pygame.init()

    def make(self,body=SOLUTION,gifts=None):
        random.seed(42)
        self.ns['COLLECTED_COINS'].clear()
        w=self.ns['World'](gifts)
        w.program=lesson_bridge.compile_lesson(body,self.ns['PROGRAM_NAME'],w.commands(),w.sensors(),self.ns['CONCEPT'])
        return w

    def catch(self,w,kind):
        w.falling=[{'x':w.x,'y':125.0,'kind':'coin' if kind in self.ns['COIN_NAMES'] else kind,'coin_id':kind if kind in self.ns['COIN_NAMES'] else None,'opened':False}]
        self.assertIsNone(w.update(0.1))
        self.assertEqual(w.falling,[]);self.assertIsNotNone(w.cargo)

    def finish_handler(self,w):
        w.update(0.01)
        for _ in range(200):
            result=w.update(0.01)
            if result or not w.processing and w.phase!='exploding': return result
        self.fail('Gift handler failed to finish')

    def test_editable_program_has_only_nested_conditions_and_rejects_loops(self):
        tree=ast.parse('def handle_gift():\n'+SOLUTION)
        self.assertFalse(any(isinstance(n,(ast.For,ast.While)) for n in ast.walk(tree)))
        for body in ('    for i in range(2):\n        open_gift()\n','    while gift_in_basket():\n        open_gift()\n','    if gift_in_basket():\n        open_gift()\n'):
            with self.subTest(body=body),self.assertRaises(ValueError): self.make(body)

    def test_contents_cannot_be_inspected_before_opening(self):
        w=self.make()
        with self.assertRaisesRegex(ValueError,'Open the gift'): w.gift_is_bomb()
        self.catch(w,'bomb')
        with self.assertRaisesRegex(ValueError,'Open the gift'): w.gift_is_bomb()
        w.update(0.01)
        self.assertEqual(w.phase,'opening')
        w.update(0.25)
        with self.assertRaisesRegex(ValueError,'Open the gift'): w.gift_is_bomb()
        w.update(0.25)
        self.assertTrue(w.gift_is_bomb())

    def test_empty_basket_runs_only_the_outer_check(self):
        w=self.make();w.update(0.01)
        self.assertFalse(w.outer_result);self.assertIsNone(w.inner_result)
        self.assertEqual(w.actions,0);self.assertFalse(w.processing)

    def test_caught_gift_is_handled_without_space_and_inner_check_waits(self):
        w=self.make();self.catch(w,'egg')
        self.assertEqual(w.phase,'opening');self.assertEqual(w.actions,1)
        self.assertFalse(w.cargo['opened'])
        w.update(self.ns['OPEN_SECONDS'])
        self.assertTrue(w.cargo['opened']);self.assertIsNone(w.inner_result)
        w.update(self.ns['DECISION_SECONDS']-0.01);self.assertIsNone(w.inner_result)
        w.update(0.02);self.assertFalse(w.inner_result)
        self.assertEqual(w.phase,'collecting')

    def test_correct_nested_if_drops_a_bomb_as_the_next_action(self):
        w=self.make();self.catch(w,'bomb')
        self.assertIsNone(self.finish_handler(w))
        self.assertEqual((w.actions,w.eggs,w.missed),(2,0,0))
        self.assertIsNone(w.cargo);self.assertTrue(w.inner_result)

    def test_wrong_next_action_plays_an_explosion_before_game_over(self):
        w=self.make(self.starter);self.catch(w,'bomb')
        w.update(0.01);w.update(0.5)
        self.assertEqual(w.phase,'deciding');self.assertFalse(w.ended)
        w.update(0.35)
        self.assertEqual(w.phase,'exploding');self.assertFalse(w.ended)
        self.assertIsNone(w.update(0.3))
        self.assertEqual(w.update(0.36),'dead')

    def test_ending_the_function_with_an_open_bomb_also_explodes(self):
        body='    if gift_in_basket():\n        open_gift()\n        if gift_is_bomb():\n            pass\n'
        w=self.make(body);self.catch(w,'bomb')
        self.assertEqual(self.finish_handler(w),'dead')

    def test_eggs_and_real_coin_gifts_are_collected_after_the_animation(self):
        for kind in ('egg',*self.ns['COIN_NAMES']):
            with self.subTest(kind=kind):
                w=self.make();self.catch(w,kind)
                w.update(0.01);w.update(0.5);w.update(0.35)
                self.assertEqual(w.phase,'collecting')
                self.assertEqual(w.eggs,0);self.assertEqual(self.ns['COLLECTED_COINS'],set())
                for _ in range(80): w.update(0.01)
                if kind=='egg': self.assertEqual(w.eggs,1)
                else: self.assertEqual(self.ns['COLLECTED_COINS'],{kind})

    def test_manual_basket_movement_and_first_missed_gift_end_the_run(self):
        w=self.make();start=w.x
        w.update(0.1,left=True);self.assertLess(w.x,start)
        w.update(0.1,right=True);self.assertAlmostEqual(w.x,start)
        w.falling=[{'x':35.0,'y':159.0,'kind':'egg','coin_id':None,'opened':False}]
        self.assertEqual(w.update(0.1),'dead');self.assertEqual(w.missed,1)

    def test_movement_alone_catches_the_rain_and_coins_persist(self):
        w=self.make(gifts=['egg','gift-1','egg','bomb','egg','gift-2','egg','bomb','egg'])
        result=None
        for _ in range(12000):
            target=max(w.falling,key=lambda gift:gift['y'],default=None)
            dx=target['x']-w.x if target else 0
            result=w.update(1/60,left=dx < -2,right=dx > 2)
            if result: break
        self.assertEqual(result,'won');self.assertEqual(w.eggs,5)
        self.assertEqual(w.missed,0)
        self.assertEqual(self.ns['COLLECTED_COINS'],set(self.ns['COIN_NAMES']))

    def test_starter_cannot_collect_eggs_and_waiting_cannot_win(self):
        w=self.make(self.starter);self.catch(w,'egg')
        self.assertEqual(self.finish_handler(w),'dead');self.assertEqual(w.eggs,0)
        w=self.make()
        for _ in range(1200):
            result=w.update(1/60)
            if result: break
        self.assertNotEqual(result,'won');self.assertEqual(w.eggs,0)

    def test_empty_basket_is_checked_repeatedly_without_input(self):
        w=self.make();checks=[]
        def sensor():checks.append(w.elapsed);return w.gift_in_basket()
        w.program=lesson_bridge.compile_lesson(SOLUTION,self.ns['PROGRAM_NAME'],w.commands(),{**w.sensors(),'gift_in_basket':sensor},self.ns['CONCEPT'])
        for _ in range(20):w.update(0.01)
        self.assertGreaterEqual(len(checks),2);self.assertEqual(w.actions,0)

    def test_multiple_boxes_spawn_and_keep_falling_while_opening(self):
        w=self.make();self.catch(w,'egg')
        incoming={'x':240.,'y':70.,'kind':'egg','coin_id':None,'opened':False}
        w.falling.append(incoming);w.spawn_timer=0.1
        w.update(0.2)
        self.assertEqual(w.phase,'opening');self.assertGreater(incoming['y'],70)
        self.assertGreaterEqual(len(w.falling),2)
        w.update(0.2);w.update(self.ns['DECISION_SECONDS'])
        self.assertEqual(w.phase,'collecting');before=incoming['y'];count=len(w.falling);w.spawn_timer=0.05
        w.update(0.15)
        self.assertGreater(incoming['y'],before);self.assertGreater(len(w.falling),count)

    def test_missing_any_kind_is_fatal_even_during_a_handler(self):
        for kind in ('egg','bomb',*self.ns['COIN_NAMES']):
            with self.subTest(kind=kind):
                w=self.make();self.catch(w,'egg')
                w.falling=[{'x':35.,'y':159.,'kind':'coin' if kind in self.ns['COIN_NAMES'] else kind,'coin_id':None,'opened':False}]
                self.assertEqual(w.update(0.1),'dead');self.assertTrue(w.ended);self.assertEqual(w.missed,1)

    def test_next_landings_are_reachable_but_require_basket_movement(self):
        w=self.make();previous=w.next_gift()['x']
        for _ in range(200):
            x=w.next_gift()['x'];self.assertTrue(35<=x<=285)
            self.assertGreater(abs(x-previous),42)
            self.assertLess(abs(x-previous),112*self.ns['SPAWN_SECONDS'])
            previous=x

    def test_continuous_rain_is_winnable_across_different_layouts(self):
        for seed in range(20):
            with self.subTest(seed=seed):
                w=self.make();random.seed(seed);result=None
                for _ in range(4000):
                    target=max(w.falling,key=lambda gift:gift['y'],default=None)
                    dx=target['x']-w.x if target else 0
                    result=w.update(1/60,left=dx < -2,right=dx > 2)
                    if result:break
                self.assertEqual(result,'won');self.assertEqual(w.missed,0)
                self.assertEqual(self.ns['COLLECTED_COINS'],set(self.ns['COIN_NAMES']))

    def test_preview_open_drop_coin_and_explosion_frames_draw(self):
        surface=pygame.Surface((320,180));small=pygame.font.Font(None,10);title=pygame.font.Font(None,16)
        for kind in ('egg','bomb','gift-1'):
            w=self.make();self.ns['draw_scene'](surface,w,small,title);self.catch(w,kind)
            w.update(0.01);w.update(0.25);self.ns['draw_scene'](surface,w,small,title)
            w.update(0.25);w.update(0.35);w.update(0.2);self.ns['draw_scene'](surface,w,small,title)
        w=self.make(self.starter);self.catch(w,'bomb');w.update(0.01);w.update(0.5);w.update(0.35);w.update(0.3)
        self.ns['draw_scene'](surface,w,small,title)

if __name__=='__main__': unittest.main()
