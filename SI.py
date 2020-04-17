import pygame
import os
import time
import random

Width, Height = 1280, 720
Win = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("AI Space Invaders")

Red_Space_Ship = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
Blue_Space_Ship = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
Green_Space_Ship = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
Yellow_Space_Ship = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

Blue_Laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
Red_Laser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
Yellow_Laser = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
Green_Laser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))

Bg = pygame.image.load(os.path.join("assets", "background-black.png"))


def main():
    run = True

    FPS = 120
    clock = pygame.time.Clock()



    while run:
        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False


main()