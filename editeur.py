import pygame
import os

CELL_SIZE = 20
GRID_SIZE = 32
WIDTH = CELL_SIZE * GRID_SIZE
PALETTE_SIZE = 40
BUTTON_HEIGHT = 40
HEIGHT = WIDTH + PALETTE_SIZE + BUTTON_HEIGHT

SKIN_FILE = "player_skin.png"

PALETTE_COLORS = [
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
]

def load_existing_skin():
    if os.path.exists(SKIN_FILE):
        image = pygame.image.load(SKIN_FILE).convert_alpha()
        image = pygame.transform.scale(image, (GRID_SIZE, GRID_SIZE))
        data = [
            [image.get_at((x, y)) for x in range(GRID_SIZE)]
            for y in range(GRID_SIZE)
        ]
        return data
    else:
        # default green skin
        return [[(0, 255, 0) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Editeur de Skin")
    font = pygame.font.SysFont(None, 24)

    grid = load_existing_skin()
    selected_color = PALETTE_COLORS[3]  # green
    save_button = pygame.Rect(WIDTH // 2 - 60, WIDTH + PALETTE_SIZE + 5, 120, BUTTON_HEIGHT - 10)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_s:
                    # save skin
                    surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                    for y in range(GRID_SIZE):
                        for x in range(GRID_SIZE):
                            surface.set_at((x, y), grid[y][x])
                    pygame.image.save(surface, SKIN_FILE)
                    print("Skin sauvegard\xC3\xA9e dans " + SKIN_FILE)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if my < WIDTH:
                    gx = mx // CELL_SIZE
                    gy = my // CELL_SIZE
                    if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
                        grid[gy][gx] = selected_color
                elif my < WIDTH + PALETTE_SIZE:
                    # palette selection
                    palette_width = PALETTE_SIZE * len(PALETTE_COLORS)
                    start_x = (WIDTH - palette_width) // 2
                    if start_x <= mx < start_x + palette_width:
                        index = (mx - start_x) // PALETTE_SIZE
                        if 0 <= index < len(PALETTE_COLORS):
                            selected_color = PALETTE_COLORS[index]
                else:
                    if save_button.collidepoint(mx, my):
                        surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                        for y in range(GRID_SIZE):
                            for x in range(GRID_SIZE):
                                surface.set_at((x, y), grid[y][x])
                        pygame.image.save(surface, SKIN_FILE)
                        print("Skin sauvegard\xC3\xA9e dans " + SKIN_FILE)

        # draw grid
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, grid[y][x], rect)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)

        # draw palette
        start_x = (WIDTH - PALETTE_SIZE * len(PALETTE_COLORS)) // 2
        for i, color in enumerate(PALETTE_COLORS):
            rect = pygame.Rect(start_x + i * PALETTE_SIZE, WIDTH, PALETTE_SIZE, PALETTE_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)
            if color == selected_color:
                pygame.draw.rect(screen, (255, 255, 255), rect, 3)

        # draw save button
        pygame.draw.rect(screen, (180, 180, 180), save_button)
        pygame.draw.rect(screen, (50, 50, 50), save_button, 1)
        text = font.render("Sauvegarder", True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=save_button.center))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
