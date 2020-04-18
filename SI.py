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



class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health):
        self.ship_img = Yellow_Space_Ship
        self.laser_img = Yellow_Laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        


def main():
    run = True
    FPS = 120
    level = 1
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)

    player_vel = 10
    ship = Ship(Width/2, Height-120)

    clock = pygame.time.Clock()

    def redraw_window():
        Win.blit(Bg, (0,0))

        lives_label = main_font.render(f"Lives : {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level : {level}", 1, (255, 255, 255))

        Win.blit(lives_label, (10, 10))
        Win.blit(level_label, (Width-level_label.get_width() - 10, 10))
        ship.draw(Win)

        pygame.display.update()



    while run:
        clock.tick(FPS)
        redraw_window()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q] and ship.x - player_vel > 0: #left
            ship.x -= player_vel

        if keys[pygame.K_d] and ship.x + player_vel < Width:#right
            ship.x += player_vel
        if keys[pygame.K_z] and ship.y - player_vel > 0: #Up
            ship.y -= player_vel
        if keys[pygame.K_s] and ship.y + player_vel < Height: #Down
            ship.y += player_vel





main()
