import pygame
import os
import time
import random
import neat
import sys

pygame.font.init()

WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

gen = 0

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


target = False
lasers = []

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

    def collision(self, obj):
        return collide(self, obj)



class Ship:
    COOLDOWN = 1

    def __init__(self, x, y, lasers, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.lasers = lasers
        self.ship_img = None
        self.laser_img = None
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
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, lasers, health=100):
        super().__init__(x, y, lasers, health)
        self.ship_img = YELLOW_SPACE_SHIP
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
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            target = True

    def get_distance(self, enemies, lasers):
        for enemy in enemies:
            for laser in lasers:
                if enemy.y > self.y and laser.y > self.y:
                    return [enemy.y, enemy.x, laser.x, laser.y]

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, lasers, health=100):
        super().__init__(x, y, lasers, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main(genomes, config):
    run = True
    FPS = 120
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    neat_font = pygame.font.SysFont("comicsans", 40)

    enemies = []
    wave_length = 5
    enemy_vel = 4

    player_vel = 10
    laser_vel = 5
    #player = Player(300, 630)

    global gen
    gen += 1
    nets = []
    ge = []
    players = []

    #Neural Network
    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(g)
        players.append(Player(WIDTH/2, HEIGHT/(5/4), lasers))
        g.fitness = 0
        ge.append(g)


    clock = pygame.time.Clock()

    def redraw_window(gen):
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        if gen == 0:
            gen = 1

        gen_label = neat_font.render("Gen : " + str(gen), 1, (255, 255, 255))
        WIN.blit(gen_label, (10, 50))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        for player in players:
            player.draw(WIN)

        pygame.display.update()

    while run and len(players) > 0:
        clock.tick(FPS)
        redraw_window(gen)

        if len(enemies) == 0:
            level += 1
            wave_length = 7

            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]), lasers)
                enemies.append(enemy)

            for g in ge:
                g.fitness += 10

        for x, player in enumerate(players):

            ge[x].fitness += 0.1

            inputs = (player.get_distance(enemies, lasers))
            outputs = nets[x].activate(inputs)


            if outputs[0] > 0.5 and player.y + player_vel + player.get_height() < HEIGHT:
                player.y += player_vel

            if outputs[1] > 0.5 and player.x + player_vel + player.get_width() < WIDTH:
                player.x += player.vel

            if outputs[2] > 0.5 and player.x - player_vel > 0:
                player.x -= player_vel

            if outputs[3] > 0.5 and player.y - player_vel > 0:
                player.y -= player_vel

            if outputs[4] > 0.2:
                player.shoot()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            for player in players:

                if collide(enemy, player):
                    player.health -= 10
                    enemies.remove(enemy)
                    ge[players.index(player)].fitness -= 2
                if enemy.y + enemy.get_height() > HEIGHT:
                    lives -= 1
                    enemies.remove(enemy)
                    for g in ge:
                        g.fitness -= 10
                if player.health <= 0:
                    ge[players.index(player)].fitness -= 20
                    players.remove(index(player))


        player.move_lasers(-laser_vel, enemies)

        if target:
            increase_fitness = 10
            for g in ge:
                g.fitness += increase_fitness


def run(config_path):
    max_gen = 150
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
    neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    #Stats
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, max_gen)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "NeatConfig.txt")
    run(config_path)
