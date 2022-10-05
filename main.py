import pygame
import os
import time 
import random
pygame.font.init()
pygame.mixer.init()


WIDTH, HEIGHT = 750, 800
WIN = pygame.display.set_mode((WIDTH,HEIGHT)) #adjust size of window
pygame.display.set_caption("Space Shooter")


#import imgaes

RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "boo.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "lakitu.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "goomba.png"))

#PLAYER SPACE SHIP             
MARIO = pygame.image.load(os.path.join("assets", "mario.png"))
PEACH = pygame.image.load(os.path.join("assets", "peach.png"))
HELP = pygame.image.load(os.path.join("assets", "help.png"))
BOWSER = pygame.image.load(os.path.join("assets", "dry_bowser.png"))
SUPER_BOWSER = pygame.image.load(os.path.join("assets", "bowser.png"))
COIN = pygame.image.load(os.path.join("assets", "coin.png"))
FIRE = pygame.image.load(os.path.join("assets", "fire.png"))


#lasers
BOMB = pygame.image.load(os.path.join("assets", "bomb.png"))
SHELL = pygame.image.load(os.path.join("assets", "shell.png")) 

#BG
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "mario-background.png")),(WIDTH,HEIGHT)) 


music = pygame.mixer.music.load(os.path.join("assets", "mario.mp3"))
pygame.mixer.music.play(-1)

shoot = pygame.mixer.Sound("laser.ogg")
blaster = pygame.mixer.Sound("blaster.ogg")
explosion = pygame.mixer.Sound("bomb.mp3")
coin = pygame.mixer.Sound("coin.mp3")
up = pygame.mixer.Sound("heal.ogg")

main_font = pygame.font.SysFont("comicsans",35)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    def move(self, vel):
        self.y += vel
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    def collision(self,obj):
        return collide(obj, self)


class Ship:
    COOLDOWN = 20
    COOLDOWNP = 360 #about 15 seconds
    def __init__(self, x, y, health=200):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.lasers_img = None
        self.lasers = []
        self.cool_down_counter = 0
        self.cool_down_counterp = 0
        self.enter = None
        self.usedp = None

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj, level):
        self.cooldown(level)
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                 
    def cooldown(self, level):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1 #should get to 10 ever 1/6 seconds but its more like 2/6 seconds

    
        if self.cool_down_counterp >= self.COOLDOWNP:#ready to shoot, >360 
            self.cool_down_counterp = 0
            self.enter = True
         
            
        elif self.cool_down_counterp > 0: #cooling down, 1-360
            self.cool_down_counterp += 1 #happening 6 times every 10 seconds
            if level > 12:
                Timer = main_font.render(f"Blaster:{int(360-(self.cool_down_counterp-1))}", 1, (255,0,0))#dark red
                WIN.blit(Timer,(5,50))

        
        if level > 12 and self.enter == True:
            SP = main_font.render(f"SHOOT", 1, (0,255,0))#ready to shoot super
            WIN.blit(SP,(5,50))
             
    def shoot(self):
        if self.cool_down_counter == 0:
            pygame.mixer.Sound.play(shoot)
            laser = Laser(self.x+25, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
                
    def shootp(self):
         if self.cool_down_counterp == 0:
            pygame.mixer.Sound.play(blaster)
            for x in range(15):
                laser = Laser(self.x-((x * 20)-140), self.y+10, self.laser_imgp)#overrides to make enemy laser come out of middle
                self.lasers.append(laser)
                self.cool_down_counterp = 1
                self.enter = False
   
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_width()

class Player(Ship): #inheriting form ship
    def __init__(self, x, y, health=200):
        super().__init__(x, y, health)
        self.ship_img = MARIO
        self.laser_img = SHELL
        self.laser_imgp = FIRE
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs, level):
        self.cooldown(level)
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if(level != 10):
                        if laser.collision(obj):
                            objs.remove(obj)
                            pygame.mixer.Sound.play(explosion)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(),10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health),10))
               
class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, BOMB),
        "blue": (BLUE_SPACE_SHIP, BOMB),
        "green": (GREEN_SPACE_SHIP, BOMB),
        "bowser": (BOWSER, FIRE),
        "super bowser": (SUPER_BOWSER, FIRE)
        }
    def shoot(self):
         if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def shootsb(self):
        if self.cool_down_counter == 0:
            for x in range(10):
                laser = Laser(self.x-((x * 20)-200), self.y+150, self.laser_img)#overrides to make enemy laser come out of middle
                self.lasers.append(laser)
                self.cool_down_counter = 1
                
    def shootb(self):
        if self.cool_down_counter == 0:
            for x in range(15):
                laser = Laser(self.x-((x * 20)-230), self.y+130, self.laser_img)#overrides to make enemy laser come out of middle
                self.lasers.append(laser)
                self.cool_down_counter = 1
    def __init__(self, x, y, color, health=200): 
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    def move(self, vel):
        self.y += vel
    def mover(self, vel):
        self.x += vel
    def movel(self, vel):
        self.x -= vel
                  
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def collection():
    title_font = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        WIN.blit(BG,(0,0))
        music = pygame.mixer.music.load(os.path.join("assets", "bowser.mp3"))
        pygame.mixer.music.play(-1)
        title_label = title_font.render("Bowser has entered! He disabled your shooter!", 1, (255,0,0))
        ten_label = title_font.render("Collect the coins to recharge your shooter!", 1, (255,255,255))
        c_label = title_font.render("Click to continue", 1, (0,255,0))
        WIN.blit(ten_label,(WIDTH/2 - ten_label.get_width()/2,350))
        WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2 - 5,300))
        WIN.blit(c_label,(WIDTH/2 - c_label.get_width()/2 - 5,400))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

def collectionb():
    title_font = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        WIN.blit(BG,(0,0))
        title_label = title_font.render("You angered bowser!", 1, (255,0,0))
        music = pygame.mixer.music.load(os.path.join("assets", "bowser2.ogg"))
        pygame.mixer.music.play()
        
        ten_label = title_font.render("Survive until you're shooter is recharged", 1, (0,255,0))
        WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2 - 5,300))
        WIN.blit(ten_label,(WIDTH/2 - ten_label.get_width()/2,350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False


def win_screen():
    title_font = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        WIN.blit(BG,(0,0))
        
        won_label = title_font.render("YOU SAVED PRINCESS PEACH", 1, (255,255,0))
        WIN.blit(won_label, (WIDTH/2 - won_label.get_width()/2, 300))
        
        finish = title_font.render("CLICK Q TO RETURN TO MENU", 1, (0,255,0))
        WIN.blit(finish, (WIDTH/2 - finish.get_width()/2, 350))
        
        arcade_label = title_font.render("CLICK MOUSE TO CONTINUE TO ARCADE MODE", 1, (0,255,0))
        WIN.blit(arcade_label, (WIDTH/2 - arcade_label.get_width()/2, 400))
        pygame.display.update()
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q] == True:
                run = False
                main_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False
                arcade_screen()
                
def arcade_screen():
    title_font = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        WIN.blit(BG,(0,0))
        welcome_label = title_font.render("Welcome to arcade mode!", 1, (255,255,255))
        WIN.blit(welcome_label, (WIDTH/2 - welcome_label.get_width()/2, 150))
        arcade_label = title_font.render("Every 3 levels you will be healed and gain 1 life", 1, (255,255,255))
        WIN.blit(arcade_label, (WIDTH/2 - arcade_label.get_width()/2, 250))
        arcade_label = title_font.render("How long can you survive?", 1, (255,255,255))
        WIN.blit(arcade_label, (WIDTH/2 - arcade_label.get_width()/2, 300))
        arcade_label = title_font.render("click to start", 1, (0,255,0))
        WIN.blit(arcade_label, (WIDTH/2 - arcade_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

def lost_menu(level):


    title_font = pygame.font.SysFont("comicsans", 30)
     #check 60 times every second if we are pressing a key

    run = True
    while run:
        WIN.blit(BG,(0,0))
        
        lost_label = main_font.render("GAME OVER!", 1, (255,0,0))
        WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 300))
        lost_label = main_font.render(f"You made it to level: {level}", 1, (255,255,255))
        WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
        lost_label = main_font.render("Press Q to quit!", 1, (255,255,255))
        WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 400))
        lost_label = main_font.render("Click mouse button to play again", 1, (255,255,255))
        WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 450))
            
        pygame.display.update()
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q] == True:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                main_menu()
    pygame.quit()  


def beat_bowser():
    title_font = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        music = pygame.mixer.music.load(os.path.join("assets", "mario.mp3"))
        pygame.mixer.music.play()
        WIN.blit(BG,(0,0))

        
        title_label = title_font.render("You beat bowser!", 1, (0,255,0))
        UN = title_font.render("YOU UNLOCKED BLASTER", 1, (255,255,255))#ready to shoot super
        s = title_font.render("Survive to level 20!", 1, (255,255,255))#ready to shoot super
        USE = title_font.render("click to continue", 1, (0,255,0))#ready to shoot super
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 150))
        WIN.blit(UN, (WIDTH/2 - UN.get_width()/2, 200))
        WIN.blit(s, (WIDTH/2 - s.get_width()/2, 250))
        WIN.blit(USE, (WIDTH/2 - USE.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False 

def main():
    FPS = 60 #how fast does game run
   
    run = True;
    clock = pygame.time.Clock()
    level = 0
    lives = 5
    lost_font = pygame.font.SysFont("comicsans",70)
    enemies = []
    wave_length = 1
    enemy_vel = 1.7 #enemy velocity
    sbowser_vel = 5
    laser_vel = 7
    player_vel = 6
    player = Player(300, 630)
    lost = False
    lost_count = 0
    won_count = 0
    right = True
    bowser_hit_counter = 0
    level_2_first = True
    level_3_first = True
    counter = 0
    collect = 0
    end = False
    jesus = False
    rightb = True
    count_down = 15
    shooter = True
    counting = True
    usedp = False
    heal = False
    seconds = 0
    won = False
    warning = False
    warningb = False
    warningc = False
    healb = False
    last = False
    beatb = False

    def redraw_window(): #draws everything for our window
        pygame.display.update() #everytime we loop, we redraw everything on the screen so that it is updated (60 times a second)
        WIN.blit(BG,(0,0))#blit takes the image and draws it in the window at given coordinates -> (0,0) is top right of the screen
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255)) # red,  green,  blue
        WIN.blit(lives_label,(10,10))
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

    while run:

        if level == 13 and beatb == False:
            beat_bowser()
            beatb = True
        if level < 21:
            WIN.blit(PEACH,(WIDTH/2 - 50,HEIGHT-100))
        if level < 2:
            WIN.blit(HELP,(390 - 50,HEIGHT-160))
        if level == 20 and last == False:
            last = True
            win_screen()  
        if level != 10 and level != 12:
            level_label = main_font.render(f"Level:{level}", 1, (255,255,255))
            WIN.blit(level_label,(WIDTH - level_label.get_width() - 10,10))    
        else:
            level_label = main_font.render(f"BOSS", 1, (128,0,0))
            WIN.blit(level_label,(WIDTH - level_label.get_width() - 10,10))   
        if level > 5 and (level - 5) % 3 == 0 and healb == False: #heal player every 3 rounds
            player.health = 200
            pygame.mixer.Sound.play(up)
            print(level)
            healb = True
            if(lives < 10):
                lives += 1    
        if(level != 12):
            enemy_font = pygame.font.SysFont("comicsans", 30)
            enemy_counter = enemy_font.render(f"Enemies:{len(enemies)}", 1, (255,255,255))
            WIN.blit(enemy_counter,(WIDTH - level_label.get_width() - 30,50))
        if level == 12:
            enemy_counter = main_font.render(f"Enemies:{1}", 1, (255,255,255))
            WIN.blit(enemy_counter,(WIDTH - level_label.get_width() - 60,50))
        if usedp == False and level> 12 and lost == False:
            UN = main_font.render(f"YOU UNLOCKED BLASTER", 1, (0,255,0))#ready to shoot super
            USE = main_font.render(f"PRESS P FOR BLASTER", 1, (0,255,0))#ready to shoot super
            WIN.blit(UN,(150,350))
            WIN.blit(USE,(175,400))
        if level == 10: 
            COIND = main_font.render(f"Coins:{10-collect}", 1, (0,255,0))#ready to shoot super
            WIN.blit(COIND,(5,55))
        if level == 10 and warning == False:
            warning = True
            Player.health = 200
            pygame.mixer.Sound.play(heal)
            lives = 5
            collection()
        if level == 12 and warningb == False:
            warningb = True
            Player.health = 200
            pygame.mixer.Sound.play(heal)
            lives = 5
            collectionb()
        if level == 13 and warningc == False:
            warningc = True
            Player.health = 200
            pygame.mixer.Sound.play(heal)
            lives = 10
        if(level == 12 and counting == True):
             shooter = False
             Timer = main_font.render(f"Recharging:{int(count_down)}", 1, (128,0,0))#dark red
             WIN.blit(Timer,(5,50))
             count_down -= 1/60
        if(int(count_down)==0):
             count_down = int(1)
             counting = False
             shooter = True
        if (level == 12 and counting == False):
             Shoot = main_font.render(f"SHOOT!!!", 1, (0,255,0))#green
             WIN.blit(Shoot,(10,100))

        clock.tick(FPS)
        redraw_window()
        
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            lost_menu(level)
        if len(enemies) == 0:
            if level != 10:
                level += 1   
                healb = False
                if(enemy_vel < 2.8):
                    enemy_vel += 0.5 #increase enemy vel up to 3.5
                if level == 13:
                    player_velocity = 8
                if wave_length < 30:
                    wave_length = int(level*1.55) #add more enemies for each wave
                if level == 10 and counter != 2:
                    for i in range(wave_length):
                        enemy = Enemy(WIDTH/2, 70 ,"super bowser")
                        enemies.append(enemy)
                        jesus = True
                elif level == 12:
                    for i in range(wave_length):
                        enemy = Enemy(WIDTH/2, 90,"bowser")
                        enemies.append(enemy)
                else:
                    for i in range(wave_length):#spawning at random loc off  screen
                        enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                        enemies.append(enemy)         
        for event in pygame.event.get(): #every time we run this loop, check if an event has occured*60 times a second)
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed() #check 60 times every second if we are pressing a key

        if level == 10:
            if keys[pygame.K_a] and player.x - player_vel > 0: #left
                player.x -= player_vel
            if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
                player.x += player_vel
            if keys[pygame.K_w] and player.y - player_vel > 75:  #up
                player.y -= player_vel
            if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: #down
                player.y += player_vel
        elif level > 12:
            if keys[pygame.K_a] and player.x - player_vel > 0: #left
                player.x -= player_vel
            if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
                player.x += player_vel
            if keys[pygame.K_w] and player.y - player_vel > 75:  #up
                player.y -= player_vel
            if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: #down
                player.y += player_vel
            if keys[pygame.K_SPACE]: #space
                player.shoot()
            if keys[pygame.K_p]: #p
                usedp = True
                player.shootp()     
        elif level == 12:
            if keys[pygame.K_a] and player.x - player_vel > 0: #left
                player.x -= player_vel
            if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
                player.x += player_vel
            if keys[pygame.K_w] and player.y - player_vel > 75:  #up
                player.y -= player_vel
            if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: #down
                player.y += player_vel
            if shooter == True:
                if keys[pygame.K_SPACE]: #space
                    player.shoot()       
        else:
            if keys[pygame.K_a] and player.x - player_vel > 0: #left
                player.x -= player_vel
            if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
                player.x += player_vel
            if keys[pygame.K_w] and player.y - player_vel > 75:  #up
                player.y -= player_vel
            if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: #down
                player.y += player_vel
            if keys[pygame.K_SPACE]: 
                player.shoot()
        for enemy in enemies[:]:
            if level == 10:
                if collect == 0:
                    WIN.blit(COIN,(100,160)) #draw collectibles
                if collect == 1:
                    WIN.blit(COIN,(100,250)) #draw collectibles
                if collect == 2:
                    WIN.blit(COIN,(300,80)) #draw collectibles
                if collect == 3:
                    WIN.blit(COIN,(500,100)) #draw collectibles
                if collect == 4:
                    WIN.blit(COIN,(275, HEIGHT - 100)) #draw collectibles
                if collect == 5:
                    WIN.blit(COIN,(650,500)) #draw collectibles
                if collect == 6:
                    WIN.blit(COIN,(345,200)) #draw collectibles
                if collect == 7:
                    WIN.blit(COIN,(150,600)) #draw collectibles
                if collect == 8:
                    WIN.blit(COIN,(350,350)) #draw collectibles
                if collect == 9:
                    WIN.blit(COIN,(425, 700)) #draw collectibles
                if collide(enemy, player): #player collision
                    player.health -= 159
                    enemies.remove(enemy)
                if enemy.x > 560.5:
                    right = False 
                elif enemy.x < -75.0:
                    right = True
                if right == True:
                    enemy.mover(enemy_vel)
                    enemy.move_lasers(laser_vel, player,level)
                else:
                    enemy.movel(enemy_vel)
                    enemy.move_lasers(laser_vel, player,level)
                if random.randrange(0, 400) == 1: #super bowser difficulty
                    enemy.shootsb()#super bowser shooting
                elif enemy.y + enemy.get_width() > WIDTH: #if enemy makes it off the screen
                    enemies.remove(enemy)     
            elif level == 12:
                if collide(enemy, player): #player collision
                    player.health -= 200
                    enemies.remove(enemy)
                if enemy.x > 625.0:
                    rightb = False   
                elif enemy.x < 10:
                    rightb = True
                if rightb == True:
                    enemy.mover(enemy_vel)
                    enemy.move_lasers(laser_vel, player,level)
                else:
                    enemy.movel(enemy_vel)
                    enemy.move_lasers(laser_vel, player,level)
                if random.randrange(0, 450) == 1: #bowser difficulty
                    enemy.shootb()#bowser shooting
                elif enemy.y + enemy.get_width() > WIDTH: #if enemy makes it off the screen
                    enemies.remove(enemy)     
            else:
                enemy.move(enemy_vel)
                enemy.move_lasers(laser_vel, player, level)
                if random.randrange(0, 160) == 1: #50% chance of enemy shooting every second x 60fps)
                    enemy.shoot()
                if collide(enemy, player): #player collision
                    player.health -= 10
                    enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > HEIGHT: #if enemy makes it off the screen
                    lives -= 1
                    enemies.remove(enemy)
        if counter == 0:           
            if (player.x >= 70 and player.x <= 130) and  (player.y >= 130 and player.y <= 210):
                counter += 1
                collect += 1
                pygame.mixer.Sound.play(coin)
        if counter == 1:
            if (player.x >= 70 and player.x <= 130) and  (player.y >= 220 and player.y <= 300):
                counter += 1
                collect += 1
                pygame.mixer.Sound.play(coin)
        if counter == 2:
            if (player.x >= 270 and player.x <= 330) and  (player.y >= 50 and player.y <= 130):
                counter += 1
                collect += 1
                pygame.mixer.Sound.play(coin)
        if counter  == 3:
            if (player.x >= 470 and player.x <= 530) and  (player.y >= 70 and player.y <= 150):
                counter += 1
                collect += 1
                pygame.mixer.Sound.play(coin)
        if counter == 4:
            if (player.x >= 245 and player.x <= 305) and  (player.y >= 670 and player.y <= 750):
                counter += 1
                collect += 1
                pygame.mixer.Sound.play(coin)
        if counter == 5:           
            if (player.x >= 620 and player.x <= 680) and  (player.y >= 470 and player.y <= 550):
                counter += 1
                collect += 1
                pygame.mixer.Sound.play(coin)
        if counter == 6:
            if (player.x >= 315 and player.x <= 375) and  (player.y >= 170 and player.y <= 250):
                counter += 1
                collect += 1
                pygame.mixer.Sound.play(coin)
        if counter == 7:
            if (player.x >= 120 and player.x <= 180) and  (player.y >= 570 and player.y <= 650):
                counter += 1
                collect += 1
                pygame.mixer.Sound.play(coin)
        if counter == 8:
            if (player.x >= 320 and player.x <= 380) and  (player.y >= 320 and player.y <= 400):
                counter += 1
                collect += 1
                pygame.mixer.Sound.play(coin)
        if counter == 9:
            if (player.x >= 395 and player.x <= 455) and  (player.y >= 650 and player.y <= 750):
                counter += 1
                collect += 1
                pygame.mixer.Sound.play(coin)
        player.move_lasers(-laser_vel, enemies, level)
        if level == 10 and counter == 10 and jesus == True:
            jesus = False
            enemies = []
            level += 1
        
    pygame.quit()

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 45)
    controls_font = pygame.font.SysFont("comicsans", 20)
    run = True
     
    while run:
        WIN.blit(BG,(0,0))
        title_label = title_font.render("Press the mouse to continue...", 1, (0,255,0))
        intro_label = title_font.render("Welcome to Mario Space Shooters", 1, (255,255,255))
        name_label = title_font.render("Made by Lucas LeVant", 1, (255,255,255))
        w_label = controls_font.render("Controls: W to move up", 1, (255,255,255))
        a_label = controls_font.render("Controls: A to move left", 1, (255,255,255))
        s_label = controls_font.render("Controls: S to move down", 1, (255,255,255))
        d_label = controls_font.render("Controls: D to move right", 1, (255,255,255))
        space_label = controls_font.render("Controls: SPACE to shoot ", 1, (255,255,255))
        WIN.blit(intro_label,(WIDTH/2 - intro_label.get_width()/2,60))
        WIN.blit(name_label,(WIDTH/2 - name_label.get_width()/2,110))
        WIN.blit(w_label,(WIDTH/2 - w_label.get_width()/2,200))
        WIN.blit(a_label,(WIDTH/2 - a_label.get_width()/2,250))
        WIN.blit(s_label,(WIDTH/2 - s_label.get_width()/2,300))
        WIN.blit(d_label,(WIDTH/2 - d_label.get_width()/2,350))
        WIN.blit(space_label,(WIDTH/2 - space_label.get_width()/2,400))
        WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2,450))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                controls()
    pygame.quit()


def controls():
    title_font = pygame.font.SysFont("comicsans", 45)
    second_font = pygame.font.SysFont("comicsans", 25)
    run = True
     
    while run:
        WIN.blit(BG,(0,0))

        ten_label = title_font.render("Rescue Princess Peach!", 1, (255,255,255))
        WIN.blit(ten_label,(WIDTH/2 - ten_label.get_width()/2,50))
        ten_label = second_font.render("If an enemy makes it off the screen you lose a life", 1, (255,255,255))
        WIN.blit(ten_label,(WIDTH/2 - ten_label.get_width()/2,200))
        ten_label = second_font.render("If you collide with an enemy or an enemy laser you lose health", 1, (255,255,255))
        WIN.blit(ten_label,(WIDTH/2 - ten_label.get_width()/2,250))
        title_label = title_font.render("Press the mouse to start", 1, (0,255,0))
        ten_label = title_font.render("Beware level 10...", 1, (255,0,0))
        WIN.blit(ten_label,(WIDTH/2 - ten_label.get_width()/2,300))
        WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2 - 5,500))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

                
    pygame.quit()
    
      
main_menu()


        
