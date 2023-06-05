import pygame

import random

pygame.font.init()

WIDTH, HEIGHT = 600, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spaceship Game!")

# Load images
BACKGROUND = pygame.image.load("galaxy_BACKGROUND.jpg")
Asteroid1 = pygame.image.load("rock.png")
Asteroid2 = pygame.image.load("rock.png")
Gemstone = pygame.image.load("gemstone.png")
Laser = pygame.image.load("pixel_laser_yellow.png")
Coin = pygame.image.load("coin.png")

# Player spaceship
Yellow_spaceship_main = pygame.image.load("pixel_ship_yellow.png")

# Loading music
pygame.mixer.init()
gamemusic = pygame.mixer.Sound("bensound-epic.mp3")
gamemusic2 = pygame.mixer.Sound("bensound-epic.mp3")
gamemusic.set_volume(0.02)
gamemusic2.set_volume(0.02)
gamemusic.play(loops=-1)
gamemusic2.play(loops=-1)

hit = pygame.mixer.Sound("hit.wav")
laser = pygame.mixer.Sound("laser.wav")
hit.set_volume(0.2)
laser.set_volume(0.2)
hit.play()
laser.play()

# Load background
BACKGROUND = pygame.image.load("galaxy_BACKGROUND.jpg")
BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))

FONT = pygame.font.SysFont("comicsans", 50)
LOST_FONT = pygame.font.SysFont("comicsans", 60)


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        self.vel = -5

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, velocity):
        self.y += velocity

    def offscreen(self, height):
        return self.y > height or self.y < 0


class Spaceship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

   

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            for obj in objs:
                if obj.collision(laser):
                    objs.remove(obj)
                    if laser in self.lasers:
                        self.lasers.remove(laser)
                    self.score += 1  # Increment the score by 1
                    break
            


    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Spaceship):
    def __init__(self, x, y, laser_img, health=100):
        super().__init__(x, y, health)
        self.ship_img = Yellow_spaceship_main
        self.laser_img = laser_img
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.laser_vel = -5
        self.score = 0
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            for obj in objs:
                if obj.collision(laser):
                    objs.remove(obj)
                    if laser in self.lasers:
                        self.lasers.remove(laser)
                    self.score += 1
                    hit.play()
                    break
          

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        if self.max_health > 0:
            pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, int(self.ship_img.get_width() * (self.health / self.max_health)), 10))


class Asteroid:
    def __init__(self, x, y, health=100, vel=1):
        self.x = x
        self.y = y
        self.health = health
        self.vel = vel
        self.asteroid_img = pygame.image.load("rock.png")
        self.mask = pygame.mask.from_surface(self.asteroid_img)

    def draw(self, window):
        window.blit(self.asteroid_img, (self.x, self.y))

    def get_width(self):
        return self.asteroid_img.get_width()

    def get_height(self):
        return self.asteroid_img.get_height()

    def move(self, enemy_vel):
        self.y += enemy_vel

    def collision(self, obj):
        obj_rect = pygame.Rect(obj.x, obj.y, obj.img.get_width(), obj.img.get_height())
        asteroid_rect = pygame.Rect(self.x, self.y, self.get_width(), self.get_height())
        return asteroid_rect.colliderect(obj_rect)

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) is not None



def main():
    global high_score
    run = True
    
    FPS = 60
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("comicsans", 30)
    lost_font = pygame.font.SysFont("comicsans", 50)
    lives = 6
    level = 0
    score = 0
    high_score = 0
    gems = []
    coins = []



    enemies = []
    
    enemy_vel = 1
    asteroid_vel = 1  # Initial asteroid velocity
    wave_length = 5  # Initial number of asteroids per wave

    player_vel = 5
    laser_vel = 5

    laser_img = pygame.image.load("pixel_laser_yellow.png")

    player = Player(300, 630, laser_img)

    lost = False
    lost_count = 0

    def redraw_window():
        
        WIN.blit(BACKGROUND, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        score_label = main_font.render(f"Score: {player.score}", 1, (255, 255, 255))
        high_score_label = main_font.render(f"High Score: {high_score}", 1, (255, 255, 255))
        


        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (10, 50))
        WIN.blit(high_score_label, (10, 90))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS * 3:
                if player.score > high_score:
                    high_score = player.score
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5  # Increase the number of asteroids in the next wave
            asteroid_vel += 0.5  # Increase the asteroid velocity
            for i in range(wave_length):
                asteroid = Asteroid(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice([Asteroid1, Asteroid2]), asteroid_vel)
                enemies.append(asteroid)


            for _ in range(wave_length):
                enemy = Asteroid(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            
            

            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

            if collide(enemy, player):
                player.health -= 10
                lives-=1
                enemies.remove(enemy)
            
               
        for laser in player.lasers:
            if collide(enemy, laser):
                player.lasers.remove(laser)
                enemies.remove(enemy)
                player.score += 1               
        









        player.move_lasers(-laser_vel, enemies)
high_score=0

def main_menu():
     
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BACKGROUND, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        title_label = title_font.render(f"High Score: {high_score}", 1, (255, 255, 255))

        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()




   
