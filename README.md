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

You can create your own player appearance using `editeur.py`. The editor now provides a 10x15 grid. Each cell you color becomes a 4×4 block in the final 40x60 image used by the game. Cells are displayed as 16×16 squares to make drawing easier. Either press `S` or use the
"Sauvegarder" button to save your skin to `player_skin.png`. When you start the
game again, the sprite is displayed at this size without additional scaling.

```bash
python3 editeur.py
```
