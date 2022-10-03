import pygame
import os
import time 
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 800
WIN = pygame.display.set_mode((WIDTH,HEIGHT)) #adjust size of window
pygame.display.set_caption("Space Shooter")


#import imgaes

RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#PLAYER SPACE SHIP             
MARIO = pygame.image.load(os.path.join("assets", "mario.png"))
PEACH = pygame.image.load(os.path.join("assets", "peach.png"))
HELP = pygame.image.load(os.path.join("assets", "help.png"))
BOWSER = pygame.image.load(os.path.join("assets", "bowser.png"))
SUPER_BOWSER = pygame.image.load(os.path.join("assets", "super_bowser.png"))



#lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))                       
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png")) 


#BG


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
    COOLDOWN = 5
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.lasers_img = None
        self.lasers = []
        self.cool_down_counter = 0
        
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_width()

class Player(Ship): #inheriting form ship
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = MARIO
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        #self.lasers.remove(laser)
    def move_lasersb(self, vel, objs, counter):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        if counter == 2:
                            objs.remove(obj)
                            print("removin")

                        
class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "bowser": (BOWSER, GREEN_LASER),
        "super bowser": (SUPER_BOWSER, GREEN_LASER)
        }
    def shoot(self):
         if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def shootb(self):
        if self.cool_down_counter == 0:
            for x in range(10):
                laser = Laser(self.x-((x * 20)-80), self.y, self.laser_img)#overrides to make enemy laser come out of middle
                self.lasers.append(laser)
                self.cool_down_counter = 1
    
    def __init__(self, x, y, color, health=100): 
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
        


def main():
    FPS = 60 #how fast does game run
    BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "mario-background.png")),(WIDTH,HEIGHT)) 
    run = True;

    
    clock = pygame.time.Clock()
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans",50)
    lost_font = pygame.font.SysFont("comicsans",70)

    enemies = []
    wave_length = 1
    enemy_vel = 4 #enemy velocity
    laser_vel = 10
   


    
    player_vel = 10;

    player = Player(300, 650)
    lost = False
    lost_count = 0
    right = True
    bowser_hit_counter = 0
    level_2_first = True
    level_3_first = True
    counter = 0
    collect = 0
    end = False
    jesus = False
    rightb = True

    def redraw_window(): #draws everything for our window
        pygame.display.update() #everytime we loop, we redraw everything on the screen so that it is updated (60 times a second)
        WIN.blit(BG,(0,0))#blit takes the image and draws it in the window at given coordinates -> (0,0) is top right of the screen
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255)) # red,  green,  blue
        level_label = main_font.render(f"Level:{level}", 1, (255,255,255))
      
        WIN.blit(lives_label,(10,10))
        WIN.blit(PEACH,(WIDTH/2,HEIGHT-100))
        WIN.blit(HELP,(390,HEIGHT-160))
        WIN.blit(level_label,(WIDTH - level_label.get_width() - 10,10))

        
       
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

      

        if lost:
            lost_label = lost_font.render("GAME OVER!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))


        pygame.display.update()


      
    while run:
        
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            
        if lost:
            if lost_count > FPS * 3: #how long show message (3 seconds) 
                run = False
            else:
                continue

        if len(enemies) == 0:
            if level != 2:
                print("next")
                level += 1
                enemy_vel += 0.5
                wave_length = wave_length + 3 #add more enemies for each wave
                if level == 2 and counter != 2:
                    for i in range(wave_length):
                        enemy = Enemy(200, 30,"super bowser")
                        enemies.append(enemy)
                        jesus = True
                elif level == 4:
                    for i in range(wave_length):
                        enemy = Enemy(200, 30,"bowser")
                        enemies.append(enemy)
                else:
                    for i in range(wave_length):#spawning at random loc off  screen
                        enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                        enemies.append(enemy)
                
                    
        for event in pygame.event.get(): #every time we run this loop, check if an event has occured*60 times a second)
            if event.type == pygame.QUIT:
                run = False
                
        keys = pygame.key.get_pressed() #check 60 times every second if we are pressing a key


        if keys[pygame.K_q]: #left
            run = False
            pygame.quit()
        if keys[pygame.K_a] and player.x - player_vel > 0: #left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0 :  #up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: #down
            player.y += player_vel 
        if keys[pygame.K_SPACE]: #space
            player.shoot()



        for enemy in enemies[:]:
            if level == 2:
                if collect == 0:
                    WIN.blit(HELP,(100,160)) #draw collectibles
                if collect == 1:
                    WIN.blit(HELP,(100,250)) #draw collectibles
                if enemy.x == 700:
                    right = False
                    
                elif enemy.x == 100:
                    right = True
                    
                if right == True:
                    enemy.mover(enemy_vel)
                    enemy.move_lasers(laser_vel, player)
                else:
                    enemy.movel(enemy_vel)
                    enemy.move_lasers(laser_vel, player)
                
                if random.randrange(0, 60) == 1: #50% chance of enemy shooting every second x 60fps)
                    enemy.shootb()
                    
                elif enemy.y + enemy.get_width() > WIDTH: #if enemy makes it off the screen
                    enemies.remove(enemy)
                    
            elif level == 4:
                if enemy.x == 706.0:
                    rightb = False
                    
                elif enemy.x == 35.0:
                    rightb = True
                    
                if rightb == True:
                    enemy.mover(enemy_vel)
                    enemy.move_lasers(laser_vel, player)
  
                else:
                    enemy.movel(enemy_vel)
                    enemy.move_lasers(laser_vel, player)
                
                if random.randrange(0, 60) == 1: #50% chance of enemy shooting every second x 60fps)
                    enemy.shootb()
                    
                elif enemy.y + enemy.get_width() > WIDTH: #if enemy makes it off the screen
                    enemies.remove(enemy)
                    
            else:
                enemy.move(enemy_vel)
                enemy.move_lasers(laser_vel, player)

                if random.randrange(0, 120) == 1: #50% chance of enemy shooting every second x 60fps)
                    enemy.shoot()

                if collide(enemy, player): #player collision
                    player.health -= 10
                    enemies.remove(enemy)

                
                elif enemy.y + enemy.get_height() > HEIGHT: #if enemy makes it off the screen
                    lives -= 1
                    enemies.remove(enemy)

        if counter == 0:           
            if (player.x >= 90 and player.x <= 110) and  (player.y >= 150 and player.y <= 170):
                counter += 1
                collect += 1
                
        if counter == 1:
            if (player.x >= 90 and player.x <= 110) and  (player.y >= 240 and player.y <= 260):
                counter += 1
                collect += 1
                
        
        player.move_lasers(-laser_vel, enemies)

        if level == 2 and counter == 2 and jesus == True:
            jesus = False
            enemies = []
            level += 1



        
    pygame.quit()
            

       
   
                
                    
                    
            

            
main()


        
