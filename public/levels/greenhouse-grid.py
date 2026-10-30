"""Grow three plants with nested loops, then carry their key to the exit."""
import asyncio
import math
import pygame
import lesson_bridge

LEVEL_NUMBER = 6
COIN_STORAGE_ID = 13
WIDTH, HEIGHT = 320, 180
PROGRAM_NAME = 'water_plants'
CONCEPT = 'nested-loops'
LOOP_COMMANDS = ('water_plant',)
# Two bonus coins, released by the left and middle plants.
COIN_NAMES = ('row', 'garden')
COLLECTED_COINS = set()
PLANT_X = (110, 174, 238)
LEVER_X, DOOR_X, GIRL_SPEED = 49, 293, 72
WATER_SECONDS, GROW_SECONDS, REWARD_SECONDS = 0.48, 0.52, 1.0


def water_plants():
    # EDIT START
    for plant in range(2):
        for stage in range(3):
            water_plant(plant)
    # EDIT END


GIRL_SPRITE = ['...hhhh....', '..hhhhhh.pp', '.hhhhhhhhpp', '.hhsssshhh.', '.hssessesh.', '..ssssssh..', '...ssss....', '....ss.....', '..dddddd...', '.sdddddds..', '.sdddddds..', '.sdddddds..', '..dddddd...', '..dddddd...', '.dddddddd..', '...s..s....', '...s..s....', '...s..s....', '..bb..bb...', '.bbb..bbb..']
PALETTE = {'h': (88,66,99), 's': (255,207,173), 'e': (65,56,85), 'd': (237,160,185), 'p': (255,223,144), 'b': (101,85,121)}
COIN_SPRITE = ['..oooo..', '.offffo.', 'offffffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offhhffo', 'offffffo', '.offffo.', '..oooo..']


def label(surface, font, text, x, y, color=(78,76,95)):
    surface.blit(font.render(text,False,color),(round(x),round(y)))


def draw_coin(surface, x, y, collected=False):
    colors={'o':(174,146,98) if collected else (188,132,59),'f':(255,207,100),'h':(255,242,179)}
    for row,line in enumerate(COIN_SPRITE):
        for col,pixel in enumerate(line):
            if pixel in colors and (not collected or pixel=='o'):
                surface.set_at((round(x)+col,round(y)+row),colors[pixel])


def remember(name):
    if name not in COLLECTED_COINS:
        COLLECTED_COINS.add(name)
        lesson_bridge.save_coins(COIN_STORAGE_ID,COLLECTED_COINS)


class World:
    def __init__(self):
        self.program = self.generator = None
        self.elapsed = self.phase_time = 0.0
        self.actions = 0
        self.x = 23.0
        self.moving = self.running = self.program_done = self.ended = False
        self.action_held = False
        self.stages = [0,0,0]
        self.phase = 'idle'
        self.target = None
        self.head_x = float(LEVER_X)
        self.coin_flights = []
        self.key_age = None
        self.has_key = self.door_open = False
        self.door_progress = 0.0
        self.message = 'Walk to the lever. Tap Space to run your watering code.'

    def commands(self): return {'water_plant':self.water_plant}
    def sensors(self): return {}
    def water_plant(self,plant): return ('water',plant)

    def perform(self,command):
        plant = command[1]
        if type(plant) is not int or not 0<=plant<3:
            self.message = 'There are only three plants: 0, 1, and 2. Check the outer loop.'
            self.ended = True
            return 'dead'
        self.target = plant
        self.phase,self.phase_time = 'moving',0.0
        self.message = f'Machine moving to plant {plant+1}. Growth: {self.stages[plant]}/3.'
        return None

    def program_finished(self):
        self.running = False
        if not all(stage==3 for stage in self.stages):
            self.phase = 'incomplete'
            self.message = 'The machine stopped. Let the last reward reach the counter...'
            return None
        self.program_done = True
        self.message = 'All three plants are fully grown! Pick up the key on the right.'
        return None

    def update_rewards(self,dt):
        for flight in list(self.coin_flights):
            flight['age'] += dt
            if flight['age']>=REWARD_SECONDS:
                remember(flight['name'])
                self.coin_flights.remove(flight)
        if self.key_age is not None:
            self.key_age += dt
            if self.key_age>=0.75 and not self.has_key and abs(self.x-(PLANT_X[2]+9))<12:
                self.has_key = True
                self.message = 'Key collected! Walk to the door and tap Space.'

    def update(self,dt,action=False,left=False,right=False):
        if self.ended: return None
        self.elapsed += dt
        direction = int(right)-int(left)
        self.moving = direction!=0
        # The girl remains under the player's control during every machine phase.
        self.x = max(12.0,min(309.0,self.x+direction*GIRL_SPEED*dt))
        pressed = action and not self.action_held
        self.action_held = action
        self.update_rewards(dt)
        if pressed:
            if abs(self.x-LEVER_X)<=15 and not self.running and not self.program_done and self.phase=='idle':
                if self.program is None:
                    self.message = 'Compile your code first.'
                else:
                    self.running = True
                    self.generator = self.program()
                    self.message = 'Lever on! The machine is running your nested loops.'
            elif abs(self.x-DOOR_X)<=19:
                if not all(stage==3 for stage in self.stages): self.message = 'The door needs all three plants fully grown.'
                elif not self.has_key: self.message = 'The door is locked. Pick up the key from the right plant.'
                elif self.door_progress==0:
                    self.door_progress = 0.001
                    self.message = 'Key turns... the exit door is opening!'
            elif not self.running:
                self.message = 'Stand beside the lever or the door, then tap Space.'
        if self.door_progress>0 and not self.door_open:
            self.door_progress = min(1.0,self.door_progress+dt/0.6)
            if self.door_progress==1:
                self.door_open = True
                self.message = 'Door open! Walk through the exit on the right.'
        if self.door_open and self.x>=302 and not self.coin_flights:
            self.ended = True
            return 'won'
        if self.phase=='incomplete' and not self.coin_flights:
            self.program_done,self.ended = True,True
            self.message = 'Machine stopped with unfinished plants. Each of the three needs three waterings.'
            return 'dead'
        if not self.running: return None
        self.phase_time += dt
        if self.phase=='moving':
            distance = PLANT_X[self.target]-self.head_x
            self.head_x += max(-110*dt,min(110*dt,distance))
            if abs(distance)<=110*dt:
                self.phase,self.phase_time = 'watering',0.0
                self.message = f'Watering plant {self.target+1}: stage {self.stages[self.target]+1} of 3.'
        elif self.phase=='watering' and self.phase_time>=WATER_SECONDS:
            if self.stages[self.target]>=3:
                self.message = 'Too much water! A plant only needs three waterings. Check the inner loop.'
                self.ended = True
                return 'dead'
            self.phase,self.phase_time = 'growing',0.0
        elif self.phase=='growing' and self.phase_time>=GROW_SECONDS:
            plant = self.target
            self.stages[plant] += 1
            self.phase,self.phase_time = 'idle',0.0
            self.message = f'Plant {plant+1} grew to stage {self.stages[plant]} of 3.'
            if self.stages[plant]==3:
                if plant<2: self.coin_flights.append({'name':COIN_NAMES[plant],'plant':plant,'age':0.0})
                else: self.key_age = 0.0
        elif self.phase=='idle':
            return advance_program(self)
        return None


def draw_key(surface,x,y):
    x,y=round(x),round(y)
    pygame.draw.rect(surface,(165,118,56),(x-4,y-4,8,8),2)
    pygame.draw.line(surface,(234,185,84),(x,y+1),(x,y+10),3)
    pygame.draw.line(surface,(165,118,56),(x,y+9),(x+4,y+9),2)
    pygame.draw.line(surface,(234,185,84),(x,y+6),(x+3,y+6),2)


def draw_plant(surface,x,growth,index,time):
    pygame.draw.rect(surface,(181,135,119),(x-11,150,22,10))
    pygame.draw.rect(surface,(227,176,145),(x-13,147,26,5))
    pygame.draw.rect(surface,(121,96,90),(x-10,147,20,2))
    if growth<=0: return
    height = 5+growth*10
    top = round(147-height)
    sway = round(math.sin(time*2+index)*min(1,growth/2))
    pygame.draw.line(surface,(88,134,104),(x,147),(x+sway,top),2)
    for tier in range(3):
        scale = max(0.0,min(1.0,growth-tier))
        if scale:
            y = 140-tier*9
            w,h = max(1,round(9*scale)),max(1,round(5*scale))
            pygame.draw.rect(surface,(121,176,120),(x-w,y-h,w,h))
            pygame.draw.rect(surface,(152,198,135),(x+1,y-h-3,w,h))
    bloom = max(0.0,min(1.0,growth-2))
    if bloom:
        size = max(1,round(6*bloom))
        color = ((240,172,191),(242,210,134),(180,165,224))[index]
        pygame.draw.rect(surface,color,(x-size+sway,top-3,2*size+1,5))
        pygame.draw.rect(surface,color,(x-2+sway,top-size,5,2*size+1))
        pygame.draw.rect(surface,(255,239,175),(x-1+sway,top-1,3,3))


def draw_scene(surface,world,small,title):
    surface.fill((222,235,224))
    # Glasshouse beams, roof, and pastel panes.
    for x in (8,78,148,218,310): pygame.draw.line(surface,(188,210,192),(x,44),(x,159),2)
    pygame.draw.lines(surface,(171,198,178),False,[(7,45),(159,20),(311,45)],3)
    pygame.draw.line(surface,(199,219,199),(8,95),(311,95),1)
    label(surface,title,'THREE LITTLE PLANTS',98,7)
    label(surface,small,'GROW EACH ONE THROUGH 3 STAGES',83,28)
    for i,name in enumerate(COIN_NAMES): draw_coin(surface,281+i*13,8,name in COLLECTED_COINS)
    pygame.draw.rect(surface,(185,212,175),(0,160,320,6))
    pygame.draw.rect(surface,(237,207,180),(0,166,320,14))
    for x in range(8,320,27): pygame.draw.rect(surface,(251,225,193),(x,169,4,2))
    # Tank and rail carry a moving watering nozzle above the plants.
    pygame.draw.rect(surface,(138,166,170),(13,53,22,34))
    pygame.draw.rect(surface,(170,209,224),(16,59,16,24))
    pygame.draw.lines(surface,(133,167,163),False,[(34,66),(43,66),(43,60),(253,60)],4)
    hx = round(world.head_x)
    pygame.draw.rect(surface,(125,151,155),(hx-9,58,19,13))
    pygame.draw.rect(surface,(188,210,206),(hx-7,60,15,8))
    pygame.draw.rect(surface,(140,163,167),(hx-3,71,7,7))
    pygame.draw.rect(surface,(184,224,170) if world.running else (224,184,158),(hx-2,62,4,3))
    if world.phase=='watering':
        for i in range(8):
            y = 80+(i*9+world.phase_time*87)%56
            pygame.draw.rect(surface,(112,178,213),(hx-5+(i%3)*4,round(y),2,4))
    # Exit opens only after the player brings the key and interacts.
    pygame.draw.rect(surface,(125,141,126),(281,111,29,49))
    pygame.draw.rect(surface,(69,88,85),(284,114,23,46))
    width = round(23*(1-world.door_progress))
    if width:
        pygame.draw.rect(surface,(207,182,190),(284,114,width,46))
        pygame.draw.rect(surface,(236,210,206),(286,118,max(1,width-4),7))
        pygame.draw.rect(surface,(249,216,133),(284+max(1,width-5),138,2,4))
    label(surface,small,'OPEN' if world.door_open else 'EXIT',286,102)
    for index,x in enumerate(PLANT_X):
        growth = world.stages[index]
        if world.phase=='growing' and world.target==index: growth+=min(1,world.phase_time/GROW_SECONDS)
        draw_plant(surface,x,growth,index,world.elapsed)
        label(surface,small,f'{index}: {world.stages[index]}/3',x-9,163)
    pygame.draw.rect(surface,(143,129,151),(LEVER_X-6,144,12,16))
    pygame.draw.rect(surface,(192,177,198),(LEVER_X-4,146,8,5))
    angle = 1 if world.running or world.program_done else -1
    pygame.draw.line(surface,(104,99,120),(LEVER_X,144),(LEVER_X+angle*7,133),2)
    pygame.draw.rect(surface,(238,162,170),(LEVER_X+angle*7-2,130,5,5))
    if not world.running and not world.program_done: label(surface,small,'SPACE',LEVER_X-10,122)
    if world.key_age is not None and not world.has_key:
        t = min(1,world.key_age/0.75)
        draw_key(surface,PLANT_X[2]+9*t,105+44*t-35*math.sin(math.pi*t))
    for row,line in enumerate(GIRL_SPRITE):
        for col,pixel in enumerate(line):
            if pixel in PALETTE:
                step = int(world.elapsed*9)%2 if world.moving and row>=15 else 0
                surface.set_at((round(world.x)-5+col,140+row-step),PALETTE[pixel])
    if world.has_key: draw_key(surface,world.x+9,140)
    for flight in world.coin_flights:
        t = min(1,flight['age']/REWARD_SECONDS)
        start = PLANT_X[flight['plant']]-4
        end = 281+13*COIN_NAMES.index(flight['name'])
        draw_coin(surface,start+(end-start)*t,99-91*t-25*math.sin(math.pi*t),flight['name'] in COLLECTED_COINS)
    pygame.draw.rect(surface,(214,225,207),(0,171,320,9))
    label(surface,small,world.message[:79],4,172)


def advance_program(world):
    try: command = next(world.generator)
    except StopIteration:
        world.generator = None
        return world.program_finished()
    world.actions += 1
    return world.perform(command)


async def main():
    lesson_bridge.emit('loading',phase=4,label='Starting your game',fraction=None,loaded=0,total=0)
    pygame.init()
    screen = pygame.display.set_mode((800,450))
    surface = pygame.Surface((WIDTH,HEIGHT))
    small,title = pygame.font.Font(None,10),pygame.font.Font(None,16)
    clock,world = pygame.time.Clock(),World()
    COLLECTED_COINS.update(name for name in lesson_bridge.load_coins(COIN_STORAGE_ID) if name in COIN_NAMES)
    state,attempt,previous_message = 'idle',0,''
    lesson_bridge.ready()
    while True:
        dt = min(clock.tick(60)/1000,0.04)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: return
        command = lesson_bridge.poll()
        if command:
            try:
                candidate = World()
                candidate.program = lesson_bridge.compile_lesson(command['body'],PROGRAM_NAME,candidate.commands(),candidate.sensors(),CONCEPT,LOOP_COMMANDS)
                world = candidate
                state,previous_message = 'playing',''
                attempt += 1
                lesson_bridge.emit('started',attempt=attempt)
            except Exception as error:
                state = 'idle'
                lesson_bridge.emit('error',message=str(error))
        if state=='playing':
            try:
                keys = pygame.key.get_pressed()
                result = world.update(dt,bool(keys[pygame.K_SPACE]),bool(keys[pygame.K_LEFT] or keys[pygame.K_a]),bool(keys[pygame.K_RIGHT] or keys[pygame.K_d]))
                if world.message!=previous_message:
                    previous_message = world.message
                    lesson_bridge.emit('notice',message=world.message)
                if result:
                    state = result
                    lesson_bridge.emit(result,seconds=round(world.elapsed,1),coins=sorted(COLLECTED_COINS))
            except Exception as error:
                state = 'idle'
                lesson_bridge.emit('error',message=str(error))
        draw_scene(surface,world,small,title)
        pygame.transform.scale(surface,(800,450),screen)
        pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())
