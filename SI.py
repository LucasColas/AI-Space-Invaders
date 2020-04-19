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

class Ship:
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

def main():
    run = True
    FPS = 120
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)

    enemies = []
    wave_length = 5
    enemy_vel = 3



    player_vel = 10
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


        pygame.display.update()

    while run:
        clock.tick(FPS)

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
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < Height: #Down
            player.y += player_vel

        redraw_window()

main()
