import os
import random
import sys

import pygame

# ----------------------------
# CONSTANTS
# ----------------------------
WIDTH, HEIGHT = 800, 600           # Size of the visible window
WORLD_WIDTH = 1_600                # Total width of the scrolling level
FPS = 60

GROUND_Y = HEIGHT - 40             # Top‑edge of the ground strip

# Colours
WHITE  = (255, 255, 255)
BLACK  = (0, 0,   0)
RED    = (255, 0,   0)
YELLOW = (255, 255, 0)
GREEN  = (0,   255, 0)
SKY_TOP, SKY_BOTTOM = (135, 206, 250), (0, 120, 255)

# Player physics
PLAYER_W, PLAYER_H = 40, 60
PLAYER_SPEED  = 5
JUMP_POWER    = 15
GRAVITY       = 1

# Enemy
ENEMY_W, ENEMY_H = 40, 60
ENEMY_SPEED = 2

# Collectable
COIN_RADIUS = 10

# Platform
PLATFORM_W, PLATFORM_H = 120, 20


# ----------------------------
# SPRITES
# ----------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

        # Try to load a custom skin, else fallback to a coloured rectangle
        if os.path.exists("player_skin.png"):
            img = pygame.image.load("player_skin.png").convert_alpha()
            img = pygame.transform.scale(img, (PLAYER_W, PLAYER_H))
            self.image = img
        else:
            self.image = pygame.Surface((PLAYER_W, PLAYER_H))
            self.image.fill(GREEN)

            # simple placeholder face
            eye = pygame.Surface((8, 8))
            eye.fill(WHITE)
            self.image.blit(eye, (10, 15))
            self.image.blit(eye, (PLAYER_W - 18, 15))
            pygame.draw.rect(self.image, BLACK, (8, PLAYER_H - 15, PLAYER_W - 16, 5))

        self.rect = self.image.get_rect(centerx=WIDTH // 2, bottom=GROUND_Y)

        self.vel_y     = 0
        self.health    = 100
        self.on_ground = True

    # ---------------------------------------------------------
    # MOVEMENT / COLLISION
    # ---------------------------------------------------------
    def _horizontal_collide(self, dx: int, platforms: pygame.sprite.Group) -> None:
        """Resolve horizontal collisions *after* moving by *dx*."""
        self.rect.x += dx
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0:
                    self.rect.right = platform.rect.left
                elif dx < 0:
                    self.rect.left  = platform.rect.right

        # Clamp to level bounds
        self.rect.left  = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, WORLD_WIDTH)

    def _vertical_collide(self, dy: int, platforms: pygame.sprite.Group) -> None:
        """Resolve vertical collisions (ground + platforms)."""
        self.rect.y += dy
        self.on_ground = False

        collided = False
        if dy > 0:   # Falling – test feet against platform tops
            for plat in platforms:
                if self.rect.colliderect(plat.rect):
                    self.rect.bottom = plat.rect.top
                    collided = True
        elif dy < 0: # Jumping – test head against platform undersides
            for plat in platforms:
                if self.rect.colliderect(plat.rect):
                    self.rect.top = plat.rect.bottom
                    collided = True

        if collided:
            self.vel_y = 0
            self.on_ground = dy > 0

        # --- Ground ---
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True

    def move(self, dx: int, dy: int, platforms: pygame.sprite.Group) -> None:
        self._horizontal_collide(dx, platforms)
        self._vertical_collide(dy, platforms)

    def update(self, keys: pygame.key.ScancodeWrapper, platforms: pygame.sprite.Group) -> None:
        # Horizontal input
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -JUMP_POWER
            self.on_ground = False

        # Gravity
        self.vel_y += GRAVITY
        dy = self.vel_y

        self.move(dx, dy, platforms)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int = GROUND_Y) -> None:
        super().__init__()

        self.image = pygame.Surface((ENEMY_W, ENEMY_H))
        self.image.fill(RED)
        eye = pygame.Surface((6, 6))
        eye.fill(WHITE)
        self.image.blit(eye, (8, 10))
        self.image.blit(eye, (ENEMY_W - 14, 10))
        pygame.draw.rect(self.image, BLACK, (5, ENEMY_H - 15, ENEMY_W - 10, 5))

        self.rect = self.image.get_rect(bottom=y, x=x)
        self.direction = 1

    def update(self, *_: object) -> None:
        self.rect.x += ENEMY_SPEED * self.direction

        # Bounce on world edges
        if self.rect.left <= 0 or self.rect.right >= WORLD_WIDTH:
            self.direction *= -1


class Coin(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        size = COIN_RADIUS * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (COIN_RADIUS, COIN_RADIUS), COIN_RADIUS)
        self.rect = self.image.get_rect(center=(x, y))


class Platform(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int,
                 w: int = PLATFORM_W, h: int = PLATFORM_H) -> None:
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))


# ----------------------------
# GAME LOGIC
# ----------------------------
class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Simple Platformer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)

        # Game state
        self.running = True
        self.state   = "menu"      # "menu" / "play"

        # Level entities
        self.all_sprites = pygame.sprite.Group()
        self.enemies     = pygame.sprite.Group()
        self.coins       = pygame.sprite.Group()
        self.platforms   = pygame.sprite.Group()

        self.score = 0
        self.player: Player
        self.camera_x = 0

        # Pre‑render a vertical gradient for the background
        self.background = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / (HEIGHT - 1)
            r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
            pygame.draw.line(self.background, (r, g, b), (0, y), (WIDTH, y))

    # ---------------------------------------------------------
    # LEVEL SETUP
    # ---------------------------------------------------------
    def reset_game(self) -> None:
        """Clear the level and spawn fresh entities."""
        for grp in (self.all_sprites, self.enemies, self.coins, self.platforms):
            grp.empty()

        self.score = 0
        self.camera_x = 0

        # Player
        self.player = Player()
        self.all_sprites.add(self.player)

        # Example enemy & coin
        enemy = Enemy(random.randint(100, WORLD_WIDTH - 100))
        coin  = Coin(random.randint(50, WORLD_WIDTH - 50), HEIGHT - 100)

        self.enemies.add(enemy)
        self.coins.add(coin)
        self.all_sprites
