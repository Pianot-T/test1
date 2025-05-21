#!/usr/bin/env python3
"""Simple one‑button platformer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Ce jeu illustre trois contraintes :
1. **Saut unique** : le joueur ne peut déclencher un nouveau saut qu’une fois revenu en
   collision avec le sol ou une plateforme.
2. **Plates‑formes traversables** : tant que le joueur monte (vel_y < 0) il traverse les
   plateformes. La collision n’est prise en compte que s’il descend et que sa position au
   tick précédent était au‑dessus de la plateforme.
3. **Hitbox plein contour** : la collision se fait sur le rectangle englobant complet du
   sprite.

Le code reste auto‑contenu et ne dépend que de **pygame** ≥ 2.0.
"""
from __future__ import annotations

import os
import random
import sys
from pathlib import Path

import pygame

# ---------------------------------------------------------------------------
# Constantes globales
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 600              # fenêtre d’affichage
WORLD_WIDTH = 2000                    # largeur du niveau « virtuel »
FPS = 60

GROUND_Y = HEIGHT - 40                # Y max du sol (top du sol)

# Couleurs
WHITE   = (255, 255, 255)
BLACK   = (0, 0, 0)
RED     = (255,   0,   0)
GREEN   = (0,   255,   0)
YELLOW  = (255, 255,   0)
SKY_TOP    = (135, 206, 250)
SKY_BOTTOM = (0,   120, 255)

# Joueur
PLAYER_W, PLAYER_H = 40, 60
PLAYER_SPEED       = 5
JUMP_VELOCITY      = 16
GRAVITY            = 0.8

# Ennemi
ENEMY_W, ENEMY_H = 40, 60
ENEMY_SPEED       = 2

# Plateforme
PLATFORM_W, PLATFORM_H = 120, 20

# Pièce
COIN_R = 10

ASSET_DIR = Path(__file__).with_suffix("").parent

# ---------------------------------------------------------------------------
# Classes de sprites
# ---------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    """Sprite contrôlable par le joueur."""

    def __init__(self, x: int, y: int):
        super().__init__()

        # Charge une éventuelle skin perso, sinon dessine un placeholder.
        skin_path = ASSET_DIR / "player_skin.png"
        if skin_path.exists():
            img = pygame.image.load(str(skin_path)).convert_alpha()
            img = pygame.transform.scale(img, (PLAYER_W, PLAYER_H))
            self.image = img
        else:
            self.image = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
            self.image.fill(GREEN)
            # visage minimaliste
            eye = pygame.Surface((8, 8))
            eye.fill(WHITE)
            self.image.blit(eye, (10, 15))
            self.image.blit(eye, (PLAYER_W - 18, 15))
            pygame.draw.rect(self.image, BLACK, (8, PLAYER_H - 15, PLAYER_W - 16, 5))

        self.rect = self.image.get_rect(midbottom=(x, y))
        self.vel = pygame.Vector2(0, 0)  # (vx, vy)
        self.on_ground = False            # maj à chaque frame par Game

    # ---------------------------------------------------------------------
    # Mécanique de mouvement / input
    # ---------------------------------------------------------------------
    def _handle_inputs(self) -> None:
        keys = pygame.key.get_pressed()
        # déplacement horizontal
        self.vel.x = 0
        if keys[pygame.K_LEFT]:
            self.vel.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel.x += PLAYER_SPEED

        # saut unique
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel.y = -JUMP_VELOCITY
            self.on_ground = False

    def update(self) -> None:
        """Mise à jour à chaque tick (input + physique)."""
        self._handle_inputs()
        # gravité
        self.vel.y += GRAVITY
        # appliquer la vélocité
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

        # limites du monde horizontal
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WORLD_WIDTH:
            self.rect.right = WORLD_WIDTH


class Enemy(pygame.sprite.Sprite):
    """Ennemi qui patrouille entre les bords du monde."""

    def __init__(self, x: int):
        super().__init__()
        self.image = pygame.Surface((ENEMY_W, ENEMY_H))
        self.image.fill(RED)
        # visage générique
        eye = pygame.Surface((6, 6))
        eye.fill(WHITE)
        self.image.blit(eye, (8, 10))
        self.image.blit(eye, (ENEMY_W - 14, 10))
        pygame.draw.rect(self.image, BLACK, (5, ENEMY_H - 15, ENEMY_W - 10, 5))

        self.rect = self.image.get_rect(midbottom=(x, GROUND_Y))
        self.direction = 1  # 1 = droite, -1 = gauche

    def update(self) -> None:
        self.rect.x += ENEMY_SPEED * self.direction
        if self.rect.left <= 0 or self.rect.right >= WORLD_WIDTH:
            self.direction *= -1


class Coin(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((COIN_R * 2, COIN_R * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (COIN_R, COIN_R), COIN_R)
        self.rect = self.image.get_rect(center=(x, y))


class Platform(pygame.sprite.Sprite):
    """Plateforme horizontale traversable par dessous."""

    def __init__(self, x: int, y: int, w: int = PLATFORM_W, h: int = PLATFORM_H):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))


# ---------------------------------------------------------------------------
# Boucle de jeu
# ---------------------------------------------------------------------------
class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Simple Platformer")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)

        self.running: bool = True
        self.state: str = "menu"  # « menu » ou « play »

        # sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()

        self.player: Player | None = None
        self.camera_x = 0
        self.score = 0

        # arrière‑plan dégradé
        self.background = self._build_gradient()

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _build_gradient(self) -> pygame.Surface:
        bg = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
            pygame.draw.line(bg, (r, g, b), (0, y), (WIDTH, y))
        return bg

    def _draw_text(self, text: str, x: int, y: int, color: tuple[int, int, int] = WHITE) -> None:
        surf = self.font.render(text, True, color)
        rect = surf.get_rect(center=(x, y))
        self.screen.blit(surf, rect)

    # ---------------------------------------------------------------------
    # Initialisation / reset
    # ---------------------------------------------------------------------
    def _reset_game(self) -> None:
        self.all_sprites.empty()
        self.enemies.empty()
        self.coins.empty()
        self.platforms.empty()

        self.score = 0
        self.camera_x = 0

        # joueur
        self.player = Player(WIDTH // 2, GROUND_Y)
        self.all_sprites.add(self.player)

        # un ennemi « demo »
        enemy = Enemy(random.randint(200, WORLD_WIDTH - 200))
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

        # une pièce « demo »
        coin = Coin(random.randint(100, WORLD_WIDTH - 100), HEIGHT // 2)
        self.coins.add(coin)
        self.all_sprites.add(coin)

        # une plateforme au centre
        plat = Platform(WIDTH // 2 - PLATFORM_W // 2, GROUND_Y - 150)
        self.platforms.add(plat)
        self.all_sprites.add(plat)

    # ---------------------------------------------------------------------
    # Boucles d’état
    # ---------------------------------------------------------------------
    def _menu_loop(self) -> None:
        while self.state == "menu" and self.running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        self._reset_game()
                        self.state = "play"
                    elif ev.key == pygame.K_ESCAPE:
                        self.running = False

            # affichage menu
            self.screen.blit(self.background, (0, 0))
            self._draw_text("Platformer", WIDTH // 2, HEIGHT // 3)
            self._draw_text("Appuyez sur ENTRÉE pour jouer", WIDTH // 2, HEIGHT // 2)
            self._draw_text("Échap pour quitter", WIDTH // 2, HEIGHT // 2 + 40)
            pygame.display.flip()
            self.clock.tick(FPS)

    # ------------------------------------------------------------------
    # Gestion des collisions sol / plateformes
    # ------------------------------------------------------------------
    def _handle_vertical_collisions(self) -> None:
        assert self.player is not None  # pour mypy
        pl = self.player

        # remise à zéro de l’état « au sol » à chaque frame
        pl.on_ground = False

        # collision avec le sol
        if pl.rect.bottom >= GROUND_Y:
            pl.rect.bottom = GROUND_Y
            pl.vel.y = 0
            pl.on_ground = True

        # collision avec plateformes – seulement si le joueur tombe
        if pl.vel.y >= 0:
            for platform in self.platforms:
                if pl.rect.colliderect(platform.rect):
                    # était‑il au‑dessus à la frame précédente ?
                    prev_bottom = pl.rect.bottom - pl.vel.y
                    if prev_bottom <= platform.rect.top:
                        pl.rect.bottom = platform.rect.top
                        pl.vel.y = 0
                        pl.on_ground = True
                        break  # une seule plateforme suffit

    # ------------------------------------------------------------------
    # Boucle principale « play »
    # ------------------------------------------------------------------
    def _play_loop(self) -> None:
        while self.state == "play" and self.running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.state = "menu"
                break

            # update logique
            self.all_sprites.update()
            self._handle_vertical_collisions()

            # collisions divers
            self._handle_entity_collisions()

            # camera suit le joueur
            assert self.player is not None
            self.camera_x = self.player.rect.centerx - WIDTH // 2
            self.camera_x = max(0, min(self.camera_x, WORLD_WIDTH - WIDTH))

            # rendu
            self._draw_scene()
            self.clock.tick(FPS)

    def _handle_entity_collisions(self) -> None:
        assert self.player is not None
        pl = self.player

        # joueur vs ennemis
        for enemy in pygame.sprite.spritecollide(pl, self.enemies, False):
            # écrasement par le dessus
            if pl.vel.y > 0 and pl.rect.bottom <= enemy.rect.top + 10:
                enemy.kill()
                pl.vel.y = -JUMP_VELOCITY / 2  # petit rebond
            else:
                self.state = "menu"  # game over retour menu
                break

        # joueur vs pièces
        for coin in pygame.sprite.spritecollide(pl, self.coins, True):
            self.score += 1

    # ------------------------------------------------------------------
    # Rendu
    # ------------------------------------------------------------------
    def _draw_scene(self) -> None:
        # fond
        self.screen.blit(self.background, (0, 0))

        # sprites
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, 0))

        # sol
        pygame.draw.rect(self.screen, WHITE, (-self.camera_x, GROUND_Y, WORLD_WIDTH, HEIGHT - GROUND_Y))

        # UI
        self._draw_text(f"Score : {self.score}", WIDTH - 70, 20)
        pygame.display.flip()

    # ------------------------------------------------------------------
    # Boucle générale
    # ------------------------------------------------------------------
    def run(self) -> None:
        while self.running:
            if self.state == "menu":
                self._menu_loop()
            elif self.state == "play":
                self._play_loop()
        pygame.quit()


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    Game().run()
