"""Nested decisions reveal hidden gifts before handling them, one action after a bomb."""
import ast
import os
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
        self.ns['COLLECTED_COINS'].clear()
        w=self.ns['World'](gifts)
        w.program=lesson_bridge.compile_lesson(body,self.ns['PROGRAM_NAME'],w.commands(),w.sensors(),self.ns['CONCEPT'])
        return w

    def catch(self,w,kind):
        w.falling={'x':w.x,'y':125.0,'kind':'coin' if kind in self.ns['COIN_NAMES'] else kind,'coin_id':kind if kind in self.ns['COIN_NAMES'] else None,'opened':False}
        self.assertIsNone(w.update(0.1))
        self.assertIsNone(w.falling);self.assertIsNotNone(w.cargo)

    def finish_handler(self,w):
        w.update(0.01,action=True)
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
        w.update(0.01,action=True)
        self.assertEqual(w.phase,'opening')
        w.update(0.25)
        with self.assertRaisesRegex(ValueError,'Open the gift'): w.gift_is_bomb()
        w.update(0.25)
        self.assertTrue(w.gift_is_bomb())

    def test_empty_basket_runs_only_the_outer_check(self):
        w=self.make();w.update(0.01,action=True)
        self.assertFalse(w.outer_result);self.assertIsNone(w.inner_result)
        self.assertEqual(w.actions,0);self.assertFalse(w.processing)

    def test_caught_gift_waits_for_space_and_opening_finishes_before_inner_check(self):
        w=self.make();self.catch(w,'egg')
        for _ in range(60): w.update(1/60)
        self.assertFalse(w.cargo['opened']);self.assertEqual(w.actions,0)
        w.update(0.01,action=True);w.update(0.5)
        self.assertTrue(w.cargo['opened']);self.assertIsNone(w.inner_result)
        self.assertEqual(w.actions,1)
        w.update(0.2);self.assertIsNone(w.inner_result)
        w.update(0.15);self.assertFalse(w.inner_result)
        self.assertEqual(w.phase,'collecting')

    def test_correct_nested_if_drops_a_bomb_as_the_next_action(self):
        w=self.make();self.catch(w,'bomb')
        self.assertIsNone(self.finish_handler(w))
        self.assertEqual((w.actions,w.eggs,w.lives),(2,0,3))
        self.assertIsNone(w.cargo);self.assertTrue(w.inner_result)

    def test_wrong_next_action_plays_an_explosion_before_game_over(self):
        w=self.make(self.starter);self.catch(w,'bomb')
        w.update(0.01,action=True);w.update(0.5)
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
                w.update(0.01,action=True);w.update(0.5);w.update(0.35)
                self.assertEqual(w.phase,'collecting')
                self.assertEqual(w.eggs,0);self.assertEqual(self.ns['COLLECTED_COINS'],set())
                for _ in range(80): w.update(0.01)
                if kind=='egg': self.assertEqual(w.eggs,1)
                else: self.assertEqual(self.ns['COLLECTED_COINS'],{kind})

    def test_manual_basket_movement_catches_falling_gifts_and_misses_cost_lives(self):
        w=self.make();start=w.x
        w.update(0.1,left=True);self.assertLess(w.x,start)
        w.update(0.1,right=True);self.assertAlmostEqual(w.x,start)
        w.falling={'x':35.0,'y':159.0,'kind':'egg','coin_id':None,'opened':False}
        w.update(0.1);self.assertEqual(w.lives,2)

    def test_five_eggs_require_manual_catching_and_handling_and_coins_persist(self):
        w=self.make(gifts=['egg','gift-1','egg','bomb','egg','gift-2','egg','bomb','egg'])
        result=None
        for _ in range(12000):
            dx=w.falling['x']-w.x if w.falling is not None else 0
            action=w.cargo is not None and not w.processing
            result=w.update(1/60,action,left=dx < -2,right=dx > 2)
            if result: break
        self.assertEqual(result,'won');self.assertEqual(w.eggs,5)
        self.assertEqual(w.lives,3)
        self.assertEqual(self.ns['COLLECTED_COINS'],set(self.ns['COIN_NAMES']))

    def test_starter_cannot_collect_eggs_and_waiting_cannot_win(self):
        w=self.make(self.starter);self.catch(w,'egg')
        self.assertIsNone(self.finish_handler(w));self.assertEqual(w.eggs,0);self.assertEqual(w.lives,2)
        w=self.make()
        for _ in range(1200):
            result=w.update(1/60)
            if result: break
        self.assertNotEqual(result,'won');self.assertEqual(w.eggs,0)

    def test_preview_open_drop_coin_and_explosion_frames_draw(self):
        surface=pygame.Surface((320,180));small=pygame.font.Font(None,10);title=pygame.font.Font(None,16)
        for kind in ('egg','bomb','gift-1'):
            w=self.make();self.ns['draw_scene'](surface,w,small,title);self.catch(w,kind)
            w.update(0.01,action=True);w.update(0.25);self.ns['draw_scene'](surface,w,small,title)
            w.update(0.25);w.update(0.35);w.update(0.2);self.ns['draw_scene'](surface,w,small,title)
        w=self.make(self.starter);self.catch(w,'bomb');w.update(0.01,action=True);w.update(0.5);w.update(0.35);w.update(0.3)
        self.ns['draw_scene'](surface,w,small,title)

if __name__=='__main__': unittest.main()
