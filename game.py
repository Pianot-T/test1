import pygame
import random
import os

# Screen dimensions
WIDTH, HEIGHT = 800, 600
WORLD_WIDTH = 1600
FPS = 60

# Y coordinate of the top of the ground platform
GROUND_Y = HEIGHT - 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
SKY_TOP = (135, 206, 250)
SKY_BOTTOM = (0, 120, 255)

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

# Platform settings
PLATFORM_WIDTH = 120
PLATFORM_HEIGHT = 20

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if os.path.exists("player_skin.png"):
            img = pygame.image.load("player_skin.png").convert_alpha()
            img = pygame.transform.scale(img, (PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image = img
        else:
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image.fill(GREEN)
            # draw a simple face as a placeholder texture
            eye = pygame.Surface((8, 8))
            eye.fill(WHITE)
            self.image.blit(eye, (10, 15))
            self.image.blit(eye, (PLAYER_WIDTH - 18, 15))
            pygame.draw.rect(
                self.image,
                BLACK,
                (8, PLAYER_HEIGHT - 15, PLAYER_WIDTH - 16, 5),
            )
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        # start the player on the ground
        self.rect.bottom = GROUND_Y
        self.vel_y = 0
        self.health = 100
        self.on_ground = True

    def move(self, dx, dy, platforms):
        """Move the player and resolve collisions."""
        # Horizontal movement. Platforms are ignored so the player can pass
        # through them without collisions.
        self.rect.x += dx

        # Vertical movement. The player only collides with the ground; platforms
        # are ignored to avoid creating an "invisible" collision surface.
        self.rect.y += dy
        self.on_ground = False
        if (
            0 <= self.rect.centerx <= WORLD_WIDTH
            and self.rect.bottom >= GROUND_Y
        ):
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True

        # No secondary collision check needed since platforms are ignored.

    def update(self, keys_pressed=None, platforms=None):
        if keys_pressed is None:
            keys_pressed = pygame.key.get_pressed()
        if platforms is None:
            platforms = []

        dx = 0
        if keys_pressed[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT]:
            dx += PLAYER_SPEED

        if keys_pressed[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -JUMP_POWER
            self.on_ground = False

        self.vel_y += GRAVITY
        dy = self.vel_y

        self.move(dx, dy, platforms)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y=GROUND_Y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(RED)
        # simple texture: eyes and mouth
        eye = pygame.Surface((6, 6))
        eye.fill(WHITE)
        self.image.blit(eye, (8, 10))
        self.image.blit(eye, (ENEMY_WIDTH - 14, 10))
        pygame.draw.rect(self.image, BLACK, (5, ENEMY_HEIGHT - 15, ENEMY_WIDTH - 10, 5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        # ensure the enemy sits on the ground
        self.rect.bottom = y
        self.direction = 1

    def update(self, *args):
        self.rect.x += ENEMY_SPEED * self.direction
        if self.rect.left <= 0 or self.rect.right >= WORLD_WIDTH:
            self.direction *= -1

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((COIN_RADIUS * 2, COIN_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (COIN_RADIUS, COIN_RADIUS), COIN_RADIUS)
        self.rect = self.image.get_rect(center=(x, y))


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=PLATFORM_WIDTH, height=PLATFORM_HEIGHT):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))

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
        self.platforms = pygame.sprite.Group()
        self.score = 0
        self.player = Player()
        self.camera_x = 0
        self.background = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * ratio)
            g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * ratio)
            b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * ratio)
            pygame.draw.line(self.background, (r, g, b), (0, y), (WIDTH, y))

    def reset_game(self):
        self.all_sprites.empty()
        self.enemies.empty()
        self.coins.empty()
        self.platforms.empty()
        self.score = 0
        self.player = Player()
        self.camera_x = 0
        self.all_sprites.add(self.player)
        # create one enemy and one coin for demonstration
        enemy = Enemy(random.randint(100, WORLD_WIDTH - 100), GROUND_Y)
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)
        coin = Coin(random.randint(50, WORLD_WIDTH - 50), HEIGHT - 100)
        self.all_sprites.add(coin)
        self.coins.add(coin)
        # add a platform the player can stand on
        platform = Platform(WIDTH // 2 - PLATFORM_WIDTH // 2, GROUND_Y - 150)
        self.all_sprites.add(platform)
        self.platforms.add(platform)

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

            self.screen.blit(self.background, (0, 0))
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

            self.player.update(keys_pressed, self.platforms)
            self.enemies.update()

            self.camera_x = self.player.rect.centerx - WIDTH // 2

            # collisions
            for enemy in pygame.sprite.spritecollide(self.player, self.enemies, False):
                if self.player.vel_y > 0 and self.player.rect.bottom <= enemy.rect.top + 10:
                    enemy.kill()
                    self.player.vel_y = -JUMP_POWER // 2
                else:
                    self.player.health -= 1
                    if self.player.health <= 0:
                        self.state = "menu"
                        break

            for coin in pygame.sprite.spritecollide(self.player, self.coins, True):
                self.score += 1

            self.screen.blit(self.background, (0, 0))
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, 0))
            self.draw_health_bar(10, 10, self.player.health)
            self.draw_text(f"Score: {self.score}", WIDTH - 80, 20)
            # ground
            pygame.draw.rect(
                self.screen, WHITE, (-self.camera_x, GROUND_Y, WORLD_WIDTH, HEIGHT - GROUND_Y)
            )
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
