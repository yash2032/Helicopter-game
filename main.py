import pygame, random
from pygame.locals import *
# from pygame.locals import (
#     K_UP,
#     K_DOWN,
#     K_LEFT,
#     K_RIGHT,
#     KEYDOWN,
#     QUIT,
#     MOUSEBUTTONDOWN,
# )

global shoot_time
shoot_time = 1

print('Click on the other window to play')
pygame.init()
pygame.mixer.init()
pygame.font.init()
clock = pygame.time.Clock()
bang = pygame.sprite.Group()
NME = pygame.sprite.Group()
music = pygame.mixer.music.load("shot.mp3")
# ms=pygame.mixer.music.load("bg.mp3")
# pygame.mixer.music.load(sound)

score = 0
display_width = 1200
display_height = 600
X = 300
Y = 500

var1 = 200
var2 = 500
clr = (204,255,255)
levelcount = 1
SCREEN_WIDTH = display_width
SCREEN_HEIGHT = display_height
screen = pygame.display.set_mode((display_width,display_height))
bullet = pygame.image.load('bul.png').convert_alpha()
alive = False

start = True
while start == True:
    for event in pygame.event.get():
        print(event)
        if event.type == MOUSEBUTTONDOWN:
            start = False
            alive = True
            global textsurface 
            textsurface= ""
    screen.fill((255,229,209))
    # pygame.mixer.music.play(-1)
    myfont = pygame.font.SysFont('Comic Sans MS', 20)
    textsurface = myfont.render('The Helicopter Game', True, (0, 0, 0))
    screen.blit(textsurface,(40,150))

   
    pygame.display.update()
    
    clock.tick(30)   

def death():
    screen.fill((150,150,150))
    pygame.display.update()
    print('You died')
    myfont = pygame.font.SysFont('Comic Sans MS', 130)
    textsurface = myfont.render('Game Over.', True, (0, 0, 0))
    screen.blit(textsurface,(0,0))
    print('Score: {}'.format(score))

def win1():
    print('Level 1 completed')
    global levelcount
    global var1 
    global var2 
    global clr
    global score
    global alive
    myfont = pygame.font.SysFont('Comic Sans MS', 100)
    textsurface = myfont.render('Level 1 completed', True, (0, 0, 0))
    screen.blit(textsurface,(0,0))
    for sprite in enemies:
        sprite.kill()
    pygame.display.flip()
    pygame.event.pump()
    pygame.time.wait(3000)
    levelcount = 2
    var1 = 200
    var2 = 300
    clr = (153, 204, 255)
    alive = True
    score = 0

def win2():
    global levelcount, var1, var2, clr, score, alive
    for sprite in enemies:
        sprite.kill()
    myfont = pygame.font.SysFont('Comic Sans MS', 100)
    textsurface = myfont.render('Level 2 completed', True, (0, 0, 0))
    screen.blit(textsurface,(0,0))
    for sprite in enemies:
        sprite.kill()
    pygame.display.flip()
    pygame.event.pump()
    pygame.time.wait(3000)
    levelcount = 3
    var1 = 100
    var2 = 200
    clr = (102, 178, 255)
    alive = True
    score = 0

def win3():
    global levelcount, var1, var2, clr, score, alive
    for sprite in enemies:
        sprite.kill()
    myfont = pygame.font.SysFont('Comic Sans MS', 100)
    textsurface = myfont.render('You beat the game!', True, (0, 0, 0))
    screen.blit(textsurface,(200, 400))
    pygame.display.flip()
    pygame.event.pump()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Player, self).__init__()
        self.surf = pygame.image.load("Heli 1.png").convert_alpha()
        
        self.rect = self.surf.get_rect(topleft = (x, y))

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)
        if pressed_keys[K_SPACE]:
        #pygame.mixer.Sound.play(sound)
         global shoot_time
         if shoot_time > 30:
           shoot_time = 0
           bullet2 = Projectile(self.rect.x+100, self.rect.y+70, bullet)
           bang.add(bullet2)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class Projectile(pygame.sprite.Sprite):
  def __init__(self, x, y, image):
    pygame.sprite.Sprite.__init__(self)
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.x = x - 50
    self.rect.y = y - 60
  def update(self):
    if self.rect.x < SCREEN_WIDTH : 
      self.rect.x += 6


def updateWindow():
  screen.blit(textsurface, (0,0))
  bang.update()
  bang.draw(screen)
  NME.update()
  NME.draw(screen)
  pygame.display.update()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("Rocket 1.png").convert_alpha()
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(10, 15)  # speed of enemies
                            
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            global score
            score += 1
            self.kill()

class Bomb(pygame.sprite.Sprite):
    def __init__(self):
        super(Bomb, self).__init__()
        self.surf = pygame.image.load("Plane 1.png").convert_alpha()
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5, 10)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            global score
            score += 2
            self.kill()

class Blimp(pygame.sprite.Sprite):
    def __init__(self):
        super(Blimp, self).__init__()
        self.surf = pygame.image.load("Blimp.png").convert_alpha()
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(4, 8)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            global score
            score += 3
            self.kill()

ADDENEMY = pygame.USEREVENT + 1
print(var1, var2, "adfadfdfasdf-------")
pygame.time.set_timer(ADDENEMY, random.randrange(var1, var2))


player = Player(display_width // 2, display_height // 2)
bang2 = Projectile(100,100,bullet)
enemies = pygame.sprite.Group()
bomb = pygame.sprite.Group()
blimp = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

while alive == True:
    for event in pygame.event.get():
        print(event)
        if event.type == pygame.QUIT:
            alive = False
        elif event.type == ADDENEMY:
            new_opponent = random.choice([Enemy(), Bomb(), Blimp()])
            enemies.add(new_opponent)
            all_sprites.add(new_opponent)

    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)

    enemies.update()

    screen.fill(clr)

    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    if pygame.sprite.spritecollideany(player, enemies):
        player.kill()
        alive = False
        death()
        
    if pygame.sprite.groupcollide(enemies, bang, True, True):
        pygame.mixer.music.play()
        hit = pygame.sprite.groupcollide(enemies, bang, True, True)
        all_sprites.remove(hit)
        pygame.display.update()
   

    if levelcount == 1:
        if score > 30:
            alive = False
            win1()
            pygame.time.set_timer(ADDENEMY, random.randrange(var1, var2))
    if levelcount == 2:
        if score > 50:
            alive = False
            win2()
            pygame.time.set_timer(ADDENEMY, random.randrange(var1, var2))
    if levelcount == 3:
        if score > 100:
            alive = False
            win3()
            pygame.time.set_timer(ADDENEMY, random.randrange(var1, var2))
    
    
    screen.blit(player.surf, player.rect)
    
    pygame.display.flip()
    pygame.display.update()
    shoot_time += 1
    updateWindow()
    clock.tick(80)
