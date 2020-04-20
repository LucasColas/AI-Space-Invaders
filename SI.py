import pygame
import os
import time
import random

pygame.font.init()

Width, Height = 1280, 720
Win = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Space Invaders")


Red_Space_Ship = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
Blue_Space_Ship = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
Green_Space_Ship = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
Yellow_Space_Ship = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

Blue_Laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
Red_Laser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
Yellow_Laser = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
Green_Laser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))

Bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (Width, Height))


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
        return not (self.y < height and self.y >=0)

    def collision(self, obj):
        return collide(self, obj)

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.x
    return obj1.mask.overlap(obj2.mask, (round(offset_x), round(offset_y))) != None


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0


    def draw(self, window):
        Win.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(Height):
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
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()



class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = Yellow_Space_Ship
        self.laser_img = Yellow_Laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(Height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10,
        self.ship_img.get_width() * (self.health/self.max_health), 10))



class Enemy(Ship):

    Color_Map = {
                "red": (Red_Space_Ship, Red_Laser),
                "green": (Green_Space_Ship, Green_Laser),
                "blue": (Blue_Space_Ship, Blue_Laser)
    }
    def __init__(self,x,y,color, health=1000):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.Color_Map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def main():
    run = True
    FPS = 120
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 70)

    enemies = []
    wave_length = 5
    enemy_vel = 3

    lost = False
    lost_count = 0

    player_vel = 10
    laser_vel = 5
    player = Player(Width/2, Height/2)

    clock = pygame.time.Clock()

    def redraw_window():
        Win.blit(Bg, (0,0))

        lives_label = main_font.render(f"Lives : {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level : {level}", 1, (255, 255, 255))

        Win.blit(lives_label, (10, 10))
        Win.blit(level_label, (Width-level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(Win)

        player.draw(Win)

        if lost:
            lost_label = lost_font.render("You Lost !", 1, (255, 255, 255))
            Win.blit(lost_label, (Width/2-lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 33:
                run = False
                quit()
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5

            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, Width-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)


        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False


        keys = pygame.key.get_pressed()
        if keys[pygame.K_q] and player.x - player_vel > 0: #left
            player.x -= player_vel

        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < Width:#right
            player.x += player_vel
        if keys[pygame.K_z] and player.y - player_vel > 0: #Up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 25 < Height: #Down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*120) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > Height:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


main()
