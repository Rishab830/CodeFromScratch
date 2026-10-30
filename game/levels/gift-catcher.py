"""Catch wrapped gifts, open them, then use a nested if to handle the surprise."""
import asyncio
import math
import random
import pygame
import lesson_bridge

LEVEL_NUMBER = 3
COIN_STORAGE_ID = 6
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'handle_gift'
CONCEPT = 'nested-if'
LOOP_COMMANDS = ()
COIN_NAMES = ('gift-1', 'gift-2')
COLLECTED_COINS = set()
OPEN_SECONDS, DECISION_SECONDS, RESOLVE_SECONDS = 0.38, 0.28, 0.30
SPAWN_SECONDS, FALL_SPEED = 1.2, 36
HANDLER_SECONDS = 0.08


def handle_gift():
    # EDIT START
    if gift_in_basket():
        open_gift()
        if gift_is_bomb():
            collect()
        else:
            drop()
    # EDIT END


GIRL_SPRITE = ['...hhhh....', '..hhhhhh.pp', '.hhhhhhhhpp', '.hhsssshhh.', '.hssessesh.', '..ssssssh..', '...ssss....', '....ss.....', '..dddddd...', '.sdddddds..', '.sdddddds..', '.sdddddds..', '..dddddd...', '..dddddd...', '.dddddddd..', '...s..s....', '...s..s....', '...s..s....', '..bb..bb...', '.bbb..bbb..']
PALETTE = {'h': (88,66,99), 's': (255,207,173), 'e': (65,56,85), 'd': (237,160,185), 'p': (255,223,144), 'b': (101,85,121)}
COIN_SPRITE = ['..oooo..', '.offffo.', 'offffffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offffffo', '.offffo.', '..oooo..']

def label(surface,font,text,x,y,color=(92,77,112)):
    surface.blit(font.render(text,False,color),(x,y))

def draw_coin(surface,x,y,collected=False):
    colors={'o':(174,146,98) if collected else (188,132,59),'f':(255,207,100),'h':(255,242,179)}
    for row,line in enumerate(COIN_SPRITE):
        for col,pixel in enumerate(line):
            if pixel in colors and (not collected or pixel=='o'): surface.set_at((round(x)+col,round(y)+row),colors[pixel])

def remember(name):
    if name not in COLLECTED_COINS:
        COLLECTED_COINS.add(name)
        lesson_bridge.save_coins(COIN_STORAGE_ID,COLLECTED_COINS)


class World:
    def __init__(self,gifts=None):
        self.program=self.generator=None
        self.elapsed=self.phase_time=0.0
        self.x=160.0
        self.eggs=self.handled=self.actions=0
        self.missed=0
        self.phase='waiting'
        self.cargo=None
        self.falling=[]
        self.last_spawn_x=None
        self.processing=self.ended=False
        self.outer_result=self.inner_result=None
        self.spawn_timer=0.35
        self.handler_timer=0.0
        self.gift_plan=list(gifts) if gifts is not None else None
        self.plan_index=0
        self.bag=[]
        self.effect_x=self.effect_direction=0
        self.message='Move to catch every gift. Your handler runs automatically.'

    def commands(self): return {'open_gift':self.open_gift,'drop':self.drop,'collect':self.collect}
    def sensors(self): return {'gift_in_basket':self.gift_in_basket,'gift_is_bomb':self.gift_is_bomb}
    def gift_in_basket(self):
        self.outer_result=self.cargo is not None
        return self.outer_result
    def gift_is_bomb(self):
        if self.cargo is None or not self.cargo['opened']:
            raise ValueError('Open the gift before checking what is inside it.')
        self.inner_result=self.cargo['kind']=='bomb'
        return self.inner_result
    def open_gift(self): return 'open'
    def drop(self): return 'drop'
    def collect(self): return 'collect'

    def next_gift(self):
        if self.gift_plan is not None:
            kind=self.gift_plan[self.plan_index%len(self.gift_plan)]
            self.plan_index+=1
        else:
            if not self.bag:
                self.bag=['egg']*4+['bomb']*2+list(COIN_NAMES)
                random.shuffle(self.bag)
                self.bag.append('egg')
            kind=self.bag.pop(0)
        if self.last_spawn_x is None:
            x=random.randint(35,285)
        else:
            # Consecutive landings require movement but remain reachable at 112 px/s.
            x=random.choice([position for position in range(35,286) if 48<=abs(position-self.last_spawn_x)<=88])
        self.last_spawn_x=x
        return {'kind':'coin' if kind in COIN_NAMES else kind,
                'coin_id':kind if kind in COIN_NAMES else None,
                'x':float(x), 'y':56.0, 'opened':False}

    def explode(self,message):
        self.phase,self.phase_time='exploding',0.0
        self.processing=False
        self.message=message
        return None

    def perform(self,command):
        if self.cargo is None:
            raise ValueError('Catch a gift before opening, dropping, or collecting it.')
        # Reading the inner condition does not spend the bomb's action slot.
        # The very next action after opening a bomb must remove it from the basket.
        if self.cargo['opened'] and self.cargo['kind']=='bomb' and command!='drop':
            return self.explode('Bomb exploded! The action after opening it must be drop().')
        self.phase_time=0.0
        if command=='open':
            if self.cargo['opened']: raise ValueError('This gift is already open. Drop or collect it.')
            self.phase='opening'
            self.message='Opening the wrapped gift... its contents are still hidden.'
        elif command=='drop':
            self.phase='dropping'
            self.effect_x=self.x
            self.effect_direction=1 if self.x<160 else -1
            self.message='Dropping the bomb safely!' if self.cargo['kind']=='bomb' and self.cargo['opened'] else 'Dropping this gift...'
        elif command=='collect':
            if not self.cargo['opened']: raise ValueError('Open the gift before collecting its contents.')
            self.phase='collecting'
            self.effect_x=self.x
            self.message='Collecting the coin!' if self.cargo['kind']=='coin' else 'Keeping the egg safe!'
        return None

    def program_finished(self):
        self.processing=False
        if self.cargo is not None:
            if self.cargo['opened'] and self.cargo['kind']=='bomb':
                return self.explode('Bomb exploded! Your handler ended without dropping it.')
            self.phase='waiting'
            self.message='The gift is still in the basket. Finish your handler with drop() or collect().'
        elif self.eggs>=5:
            self.ended=True
            return 'won'
        else:
            self.phase='waiting'
            self.message='Automatic handler running. Catch every gift!'
        self.handler_timer=HANDLER_SECONDS
        return None

    def resolve_gift(self):
        kind=self.cargo['kind']
        if self.phase=='collecting':
            if kind=='egg': self.eggs+=1
            elif kind=='coin': remember(self.cargo['coin_id'])
        elif kind=='egg':
            self.ended=True
            self.message='An egg was dropped. Collect eggs; only bombs need dropping.'
            return 'dead'
        self.handled+=1
        self.cargo=None
        self.phase,self.phase_time='settle',0.0
        return None

    def update_rain(self,dt):
        # Rain has its own clock. Opening a box never pauses falling or spawning.
        self.spawn_timer-=dt
        while self.spawn_timer<=0:
            self.falling.append(self.next_gift())
            self.spawn_timer+=SPAWN_SECONDS
        for gift in list(self.falling):
            previous_y=gift['y']
            gift['y']+=FALL_SPEED*dt
            if previous_y+6<=133<=gift['y']+6 and abs(gift['x']-self.x)<=21 and self.cargo is None:
                self.cargo=gift
                self.falling.remove(gift)
                self.phase,self.phase_time='waiting',0.0
                self.handler_timer=0.0
                self.message='Gift caught! Your nested if is handling it.'
            elif gift['y']>=160:
                self.missed+=1
                self.ended=True
                self.message='Missed a gift! Every falling box must be caught.'
                return 'dead'
        return None

    def update(self,dt,left=False,right=False):
        if self.ended: return None
        self.elapsed+=dt
        self.x=max(22.0,min(298.0,self.x+(int(right)-int(left))*112*dt))
        self.phase_time+=dt
        if self.phase=='exploding':
            if self.phase_time>=0.65:
                self.ended=True
                return 'dead'
            return None
        result=self.update_rain(dt)
        if result: return result
        if self.phase=='opening':
            if self.phase_time>=OPEN_SECONDS:
                self.cargo['opened']=True
                self.phase,self.phase_time='deciding',0.0
                self.message='BOMB! One action left: drop it immediately.' if self.cargo['kind']=='bomb' else 'Gift opened. Now the inner if can check what is inside.'
            return None
        if self.phase in ('collecting','dropping'):
            if self.phase_time>=RESOLVE_SECONDS: return self.resolve_gift()
            return None
        self.handler_timer=max(0.0,self.handler_timer-dt)
        if not self.processing and self.handler_timer==0:
            self.generator=self.program() if self.program is not None else None
            self.processing=True
            self.outer_result=self.inner_result=None
        if self.processing and (self.phase=='waiting' or self.phase=='deciding' and self.phase_time>=DECISION_SECONDS or self.phase=='settle' and self.phase_time>=0.06):
            return advance_program(self)
        return None


def draw_wrapped_gift(surface,x,y,lid=0):
    x,y=round(x),round(y)
    pygame.draw.rect(surface,(151,111,151),(x-7,y-6,14,13))
    pygame.draw.rect(surface,(238,174,199),(x-6,y-5,12,11))
    pygame.draw.rect(surface,(251,230,174),(x-1,y-5,3,11))
    lift=round(lid*17)
    pygame.draw.rect(surface,(175,126,172),(x-8,y-7-lift,16,4))
    pygame.draw.rect(surface,(247,215,185),(x-7,y-7-lift,14,2))
    if lid<0.2:
        pygame.draw.rect(surface,(247,215,185),(x-4,y-10,4,3),1)
        pygame.draw.rect(surface,(247,215,185),(x+1,y-10,4,3),1)

def draw_contents(surface,gift,x,y):
    x,y=round(x),round(y)
    if gift['kind']=='egg':
        pygame.draw.ellipse(surface,(186,156,152),(x-4,y-6,9,13))
        pygame.draw.ellipse(surface,(255,243,214),(x-3,y-6,7,11))
        surface.set_at((x-1,y-4),(255,254,242))
    elif gift['kind']=='coin':
        draw_coin(surface,x-4,y-5,gift['coin_id'] in COLLECTED_COINS)
    else:
        pygame.draw.circle(surface,(92,78,110),(x,y),6)
        pygame.draw.rect(surface,(180,158,184),(x-3,y-4,2,2))
        pygame.draw.line(surface,(146,112,111),(x+2,y-5),(x+5,y-10),1)
        pygame.draw.rect(surface,(255,200,122),(x+4,y-11,3,3))

def draw_scene(surface,world,small,title):
    surface.fill((225,220,244))
    for x,y in ((30,66),(232,72)):
        pygame.draw.rect(surface,(255,246,238),(x,y,32,8))
        pygame.draw.rect(surface,(255,246,238),(x+6,y-5,19,5))
    pygame.draw.rect(surface,(210,229,193),(0,166,320,14))
    for x in range(6,320,22): pygame.draw.rect(surface,(179,207,174),(x,166,5,2))
    label(surface,title,'GIFT CATCHER',111,6)
    label(surface,small,f'EGGS {world.eggs}/5',8,10)
    label(surface,small,'NO MISSES',229,10)
    for i,name in enumerate(COIN_NAMES): draw_coin(surface,286+i*13,6,name in COLLECTED_COINS)
    outer='--' if world.outer_result is None else 'YES' if world.outer_result else 'NO'
    label(surface,small,'IF GIFT IN BASKET: '+outer,8,28)
    inner='LOCKED' if world.cargo is None or not world.cargo['opened'] else '?' if world.inner_result is None else 'YES' if world.inner_result else 'NO'
    label(surface,small,'IF BOMB: '+inner,20,39,(99,121,114) if world.inner_result is not None else (150,137,165))
    pygame.draw.line(surface,(174,157,187),(11,37),(11,43),1)
    pygame.draw.line(surface,(174,157,187),(11,43),(17,43),1)
    if world.cargo is not None and world.cargo['opened']:
        text=('BOMB EXPLODED' if world.phase=='exploding' else 'BOMB: DROPPING SAFELY' if world.phase=='dropping' else 'BOMB - 1 ACTION TO DROP') if world.cargo['kind']=='bomb' else 'OPENED: '+world.cargo['kind'].upper()
        label(surface,small,text,151,39,(183,102,137) if world.cargo['kind']=='bomb' else (107,130,104))
    for gift in world.falling: draw_wrapped_gift(surface,gift['x'],gift['y'])
    # Maya carries the basket; its front rim hides contents as they are collected.
    for y,row in enumerate(GIRL_SPRITE):
        for x,pixel in enumerate(row):
            if pixel in PALETTE: surface.set_at((round(world.x)-5+x,146+y),PALETTE[pixel])
    pygame.draw.line(surface,(255,207,173),(round(world.x)-7,151),(round(world.x)-12,146),2)
    pygame.draw.line(surface,(255,207,173),(round(world.x)+6,151),(round(world.x)+12,146),2)
    pygame.draw.arc(surface,(172,132,119),(round(world.x)-14,123,28,22),0,math.pi,2)
    if world.cargo is not None and world.phase!='exploding':
        gift=world.cargo
        if world.phase=='dropping':
            t=min(1,world.phase_time/RESOLVE_SECONDS)
            x,y=world.effect_x+world.effect_direction*65*t,128+39*t-28*math.sin(math.pi*t)
            if gift['opened']: draw_contents(surface,gift,x,y)
            else: draw_wrapped_gift(surface,x,y)
        elif not gift['opened']:
            draw_wrapped_gift(surface,world.x,128,min(1,world.phase_time/OPEN_SECONDS) if world.phase=='opening' else 0)
        elif world.phase=='collecting' and gift['kind']=='coin':
            t=min(1,world.phase_time/RESOLVE_SECONDS)
            target=290+13*COIN_NAMES.index(gift['coin_id'])
            draw_contents(surface,gift,world.effect_x+(target-world.effect_x)*t,128-117*t-12*math.sin(math.pi*t))
        else:
            y=128+15*min(1,world.phase_time/RESOLVE_SECONDS) if world.phase=='collecting' else 128
            draw_contents(surface,gift,world.x,y)
    pygame.draw.rect(surface,(172,128,111),(round(world.x)-17,137,34,11))
    pygame.draw.rect(surface,(228,188,145),(round(world.x)-16,140,32,7))
    for x in range(-12,16,6): pygame.draw.line(surface,(193,149,119),(round(world.x)+x,140),(round(world.x)+x,146),1)
    pygame.draw.line(surface,(246,215,172),(round(world.x)-17,138),(round(world.x)+16,138),1)
    if world.phase=='exploding':
        t=min(1,world.phase_time/0.65)
        radius=round(5+21*t)
        pygame.draw.circle(surface,(249,194,131),(round(world.x),128),radius,3)
        for i in range(8):
            angle=i*math.pi/4
            pygame.draw.rect(surface,(226,139,149),(round(world.x+math.cos(angle)*radius*1.3),round(128+math.sin(angle)*radius*1.3),3,3))
    pygame.draw.rect(surface,(217,207,230),(0,171,320,9))
    label(surface,small,world.message[:76],4,173)


def advance_program(world):
    if world.generator is None: return world.program_finished()
    try: command=next(world.generator)
    except StopIteration:
        world.generator=None
        return world.program_finished()
    world.actions+=1
    return world.perform(command)


async def main():
    lesson_bridge.emit('loading',phase=4,label='Starting your game',fraction=None,loaded=0,total=0)
    pygame.init()
    screen=pygame.display.set_mode((800,450))
    surface=pygame.Surface((WIDTH,HEIGHT))
    small,title=pygame.font.Font(None,10),pygame.font.Font(None,16)
    clock=pygame.time.Clock();world=World()
    COLLECTED_COINS.update(name for name in lesson_bridge.load_coins(COIN_STORAGE_ID) if name in COIN_NAMES)
    state,attempt,previous_message='idle',0,''
    lesson_bridge.ready()
    while True:
        dt=min(clock.tick(60)/1000,0.04)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: return
        command=lesson_bridge.poll()
        if command:
            try:
                candidate=World()
                candidate.program=lesson_bridge.compile_lesson(command['body'],PROGRAM_NAME,candidate.commands(),candidate.sensors(),CONCEPT)
                world=candidate;state,previous_message='playing','';attempt+=1
                lesson_bridge.emit('started',attempt=attempt)
            except Exception as error:
                state='idle';lesson_bridge.emit('error',message=str(error))
        if state=='playing':
            try:
                keys=pygame.key.get_pressed()
                left=bool(keys[pygame.K_LEFT] or keys[pygame.K_a]);right=bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])
                result=world.update(dt,left=left,right=right)
                if world.message!=previous_message:
                    previous_message=world.message;lesson_bridge.emit('notice',message=world.message)
                if result:
                    state=result;lesson_bridge.emit(result,seconds=round(world.elapsed,1),coins=sorted(COLLECTED_COINS))
            except Exception as error:
                state='idle';lesson_bridge.emit('error',message=str(error))
        draw_scene(surface,world,small,title)
        pygame.transform.scale(surface,(800,450),screen);pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())
