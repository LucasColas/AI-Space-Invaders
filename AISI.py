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
        return not(self.y <= height and self.y >= -70)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 10

    def __init__(self, x, y, lasers, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.lasers = lasers.copy()
        self.ship_img = None
        self.laser_img = None
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)


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
        self.target = False

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(- vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            self.target = True

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

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def get(enemies, lasers, player_vel):
    enemies_pos = []
    enemies_laser = []
    for enemy in enemies:
        enemies_pos.append((enemy.x, enemy.y))
        for laser in enemy.lasers:
            enemies_laser.append((laser.x, laser.y))

        enemies_pos.sort(key = lambda enemie_pos: enemie_pos[1], reverse = True)
        enemies_laser.sort(key = lambda enemie_laser: enemie_laser[1], reverse = True)

    if len(lasers) > 0:
        enemies_inputs = [enemies_pos[0][0], enemies_pos[0][1], enemies_laser[0][0], enemies_laser[0][1], player_vel]
    else:
        enemies_inputs = [enemies_pos[0][0], enemies_pos[0][1], 0, 0, player_vel]

    return enemies_inputs

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (round(offset_x), round(offset_y))) != None

def main(genomes, config):
    run = True
    FPS = 1000
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    neat_font = pygame.font.SysFont("comicsans", 40)


    wave_length = 5
    enemy_vel = 4

    player_vel = 3
    laser_vel = 5
    player = Player(WIDTH/2, HEIGHT/(5/3), lasers)

    global gen
    gen += 1
    nets = []
    ge = []
    players = []

    #Neural Network
    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player(WIDTH/2, HEIGHT/(13/10), lasers))
        g.fitness = 0
        ge.append(g)


    clock = pygame.time.Clock()

    def redraw_window(gen, players,enemies):
        WIN.fill((0,0,0)) #Avoid trace
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        enemies_label = neat_font.render("Enemies : " + str(len(enemies)), 1, (255,255,255))
        alive_label = neat_font.render("Alive : " + str(len(players)), 1, (255, 255, 255))

        if gen == 0:
            gen = 1

        gen_label = neat_font.render("Gen : " + str(gen), 1, (255, 255, 255))
        WIN.blit(gen_label, (10, 50))
        WIN.blit(enemies_label, (10, 80))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(alive_label, (WIDTH - level_label.get_width() - 10, 50))

        for enemy in enemies:
            enemy.draw(WIN)

        for player in players:
            player.draw(WIN)

        pygame.display.update()

    enemies = [Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]), lasers)]
    while run and len(players) > 0:
        clock.tick(FPS)

        if len(enemies) <= 1:
            level += 1
            wave_length = 4

            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]), lasers)
                enemies.append(enemy)

            for g in ge:
                g.fitness += 30 # When there is a new generation of enemies, we give to each player a fitness of 30

        for x, player in enumerate(players):
            ge[x].fitness += 0.001 #Each frame they stay alive, fitness function increases of 0.1

            outputs = nets[x].activate(get(enemies,lasers, player_vel))
            #print(outputs)

            if outputs[0] > 0.5 and player.x + player_vel + player.get_width() < WIDTH:
                player.x += player_vel

            if outputs[1] > 0.5 and player.x - player_vel > 0:
                player.x -= player_vel

            if outputs[2] > 0.2:
                player.shoot()

            player.move_lasers(laser_vel, enemies)

            if player.target:
                increase_fitness = 50
                print("Target")
                for g in ge:
                    g.fitness += increase_fitness
                player.target = False

            if not player.target:
                decrease_fitness = 1
                for g in ge:
                    g.fitness -= decrease_fitness


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            for player in players:
                if enemy in enemies:
                    if collide(enemy, player):
                        player.health -= 10
                        enemies.remove(enemy)
                        ge[players.index(player)].fitness -= 12
                if player.health <= 0:
                    ge[players.index(player)].fitness -= 20
                    players.pop(players.index(player))



        for x, enemy in enumerate(enemies):
             if enemy.y > HEIGHT:
                 lives -= 1
                 enemies.pop(x)
                 for g in ge:
                     g.fitness -= 100

        if lives <= 0:
            players.clear()
            print("Pop deleted")
            for g in ge:
                g.fitness -= 500

        redraw_window(gen, players,enemies)


def run(config_path):
    max_gen = 150
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
    neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    #Stats
    stats = neat.StatisticsReporter()
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(stats)

    winner = p.run(main, max_gen)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "NeatConfig.txt")
    run(config_path)
