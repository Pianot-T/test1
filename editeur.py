import pygame
import os

CELL_SIZE = 5
GRID_WIDTH = 40
GRID_HEIGHT = 60
WIDTH = CELL_SIZE * GRID_WIDTH
CANVAS_HEIGHT = CELL_SIZE * GRID_HEIGHT
PALETTE_SIZE = 40
BUTTON_HEIGHT = 40
HEIGHT = CANVAS_HEIGHT + PALETTE_SIZE + BUTTON_HEIGHT

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
    if os.path.exists("player_skin.png"):
        image = pygame.image.load("player_skin.png").convert_alpha()
        image = pygame.transform.scale(image, (GRID_WIDTH, GRID_HEIGHT))
        data = [
            [image.get_at((x, y)) for x in range(GRID_WIDTH)]
            for y in range(GRID_HEIGHT)
        ]
        return data
    else:
        # default green skin
        return [[(0, 255, 0) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Editeur de Skin")
    font = pygame.font.SysFont(None, 24)

    grid = load_existing_skin()
    selected_color = PALETTE_COLORS[3]  # green
    save_button = pygame.Rect(WIDTH // 2 - 60, CANVAS_HEIGHT + PALETTE_SIZE + 5, 120, BUTTON_HEIGHT - 10)

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
                    surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
                    for y in range(GRID_HEIGHT):
                        for x in range(GRID_WIDTH):
                            surface.set_at((x, y), grid[y][x])
                    pygame.image.save(surface, "player_skin.png")
                    print("Skin sauvegarde dans player_skin.png")
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if my < CANVAS_HEIGHT:
                    gx = mx // CELL_SIZE
                    gy = my // CELL_SIZE
                    if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                        grid[gy][gx] = selected_color
                elif my < CANVAS_HEIGHT + PALETTE_SIZE:
                    # palette selection
                    palette_width = PALETTE_SIZE * len(PALETTE_COLORS)
                    start_x = (WIDTH - palette_width) // 2
                    if start_x <= mx < start_x + palette_width:
                        index = (mx - start_x) // PALETTE_SIZE
                        if 0 <= index < len(PALETTE_COLORS):
                            selected_color = PALETTE_COLORS[index]
                else:
                    if save_button.collidepoint(mx, my):
                        surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
                        for y in range(GRID_HEIGHT):
                            for x in range(GRID_WIDTH):
                                surface.set_at((x, y), grid[y][x])
                        pygame.image.save(surface, "player_skin.png")
                        print("Skin sauvegarde dans player_skin.png")

        # draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, grid[y][x], rect)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)

        # draw palette
        start_x = (WIDTH - PALETTE_SIZE * len(PALETTE_COLORS)) // 2
        for i, color in enumerate(PALETTE_COLORS):
            rect = pygame.Rect(start_x + i * PALETTE_SIZE, CANVAS_HEIGHT, PALETTE_SIZE, PALETTE_SIZE)
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
