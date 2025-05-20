import pygame
import random

# Screen dimensions
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Player settings
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 5
JUMP_POWER = 15
GRAVITY = 1

# Enemy settings
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 60
ENEMY_SPEED = 2

# Coin settings
COIN_RADIUS = 10

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 50
        self.vel_y = 0
        self.health = 100

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        self.vel_y += GRAVITY
        if keys_pressed[pygame.K_SPACE] and self.rect.bottom >= HEIGHT - 50:
            self.vel_y = -JUMP_POWER

        self.rect.y += self.vel_y

        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.vel_y = 0

        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, WIDTH)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.direction = 1

    def update(self):
        self.rect.x += ENEMY_SPEED * self.direction
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((COIN_RADIUS * 2, COIN_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (COIN_RADIUS, COIN_RADIUS), COIN_RADIUS)
        self.rect = self.image.get_rect(center=(x, y))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Simple Platformer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.running = True
        self.state = "menu"  # menu or play
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.score = 0
        self.player = Player()

    def reset_game(self):
        self.all_sprites.empty()
        self.enemies.empty()
        self.coins.empty()
        self.score = 0
        self.player = Player()
        self.all_sprites.add(self.player)
        # create one enemy and one coin for demonstration
        enemy = Enemy(random.randint(100, WIDTH - 100), HEIGHT - 50)
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)
        coin = Coin(random.randint(50, WIDTH - 50), HEIGHT - 100)
        self.all_sprites.add(coin)
        self.coins.add(coin)

    def draw_text(self, text, x, y, color=WHITE):
        img = self.font.render(text, True, color)
        rect = img.get_rect()
        rect.center = (x, y)
        self.screen.blit(img, rect)

    def draw_health_bar(self, x, y, health):
        pygame.draw.rect(self.screen, RED, (x, y, 100, 10))
        pygame.draw.rect(self.screen, GREEN, (x, y, max(0, health), 10))

    def main_menu(self):
        while self.state == "menu" and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.state = "play"
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            self.screen.fill(BLACK)
            self.draw_text("Platformer", WIDTH // 2, HEIGHT // 3)
            self.draw_text("Press ENTER to Start", WIDTH // 2, HEIGHT // 2)
            self.draw_text("Press ESC to Quit", WIDTH // 2, HEIGHT // 2 + 40)
            pygame.display.flip()
            self.clock.tick(FPS)

    def play(self):
        while self.state == "play" and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_ESCAPE]:
                self.state = "menu"
                break

            self.all_sprites.update(keys_pressed)

            # collisions
            if pygame.sprite.spritecollide(self.player, self.enemies, False):
                self.player.health -= 1
                if self.player.health <= 0:
                    self.state = "menu"
                    break

            for coin in pygame.sprite.spritecollide(self.player, self.coins, True):
                self.score += 1

            self.screen.fill(BLACK)
            self.all_sprites.draw(self.screen)
            self.draw_health_bar(10, 10, self.player.health)
            self.draw_text(f"Score: {self.score}", WIDTH - 80, 20)
            # ground
            pygame.draw.rect(self.screen, WHITE, (0, HEIGHT - 40, WIDTH, 40))
            pygame.display.flip()
            self.clock.tick(FPS)

    def run(self):
        while self.running:
            if self.state == "menu":
                self.main_menu()
            elif self.state == "play":
                self.play()
        pygame.quit()

if __name__ == "__main__":
    Game().run()
