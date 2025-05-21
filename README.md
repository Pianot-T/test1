# Simple Platformer Game

This repository contains a small 2D platformer written with **pygame**. The game implements the following features:

- Player controls with arrow keys and jumping using the space bar.
- A health bar that decreases on enemy collisions.
- Moving enemies.
- Yellow coins that increase the score when collected.
- A basic 2D environment with a ground platform and a simple sky gradient.
- Basic textures for the player and enemies.
- Enemies can be defeated by jumping on them.
- Scrolling camera that follows the player across a larger world.
- A main menu where you can start the game or quit.

## Requirements

- Python 3.8+
- `pygame` library

## Running

Install `pygame` (not included in this environment):

```bash
pip install pygame
```

Then launch the game:

```bash
python3 game.py
```

Controls:

- **Arrow keys**: move left/right
- **Space**: jump
- **Esc**: return to menu or quit
- **Enter**: start game from menu

## Custom Player Skin

You can create your own player appearance using `editeur.py`. Run the editor and
draw a 32x32 pixel skin with the palette provided. Press `S` to save your skin
to `player_skin.png`. When you start the game again, this image will be loaded
and used for the player sprite.

```bash
python3 editeur.py
```
