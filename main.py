import pygame
from noise import pnoise2
import random

pygame.init()

# Initial window size
width, height = 800, 600
cell_size = 40
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
cols = width // cell_size
rows = height // cell_size

pygame.display.set_caption('Mole in da hole')

running = True
square_size = 40
speed = 5  # fast mole like original
clock = pygame.time.Clock()

world_x, world_y = float(cols // 2), float(rows // 2)

mole_img = pygame.image.load("assets/mole.png")
mole_img = pygame.transform.scale(mole_img, (square_size, square_size))

fossil_img = pygame.image.load("assets/fossil1.png")
fossil_img = pygame.transform.scale(fossil_img, (cell_size, cell_size))
rock_img = pygame.image.load("assets/rock1.png")
rock_img = pygame.transform.scale(rock_img, (cell_size, cell_size))

trail = []  # world-space float coords
trail_length = 20

soil_color = (160, 82, 45)
rock_color = (100, 100, 100)
air_color = (30, 30, 30)
darker_soil = (110, 50, 20)
lighter_soil = (210, 140, 80)
fossil_chance = 0.07
rock_chance = 0.10
seed = random.randint(0, 10000)

map_grid = {}

def generate_tile(row, col):
    n = pnoise2(col * 0.15 + seed, row * 0.15 + seed)
    if n > -0.2:
        if n > 0.25 and random.random() < rock_chance:
            return 'rock'
        elif n > 0.1 and random.random() < fossil_chance:
            return 'fossil'
        else:
            return 'soil'
    else:
        # Instead of pure air, randomly fill with darker/lighter soil
        r = random.random()
        if r < 0.33:
            return 'darker_soil'
        elif r < 0.66:
            return 'lighter_soil'
        else:
            return 'air'

def ensure_map_area(top, left, bottom, right):
    for row in range(top, bottom):
        for col in range(left, right):
            if (row, col) not in map_grid:
                map_grid[(row, col)] = generate_tile(row, col)

def world_to_screen(wx, wy, cam_x, cam_y):
    """Convert world (float cell) coords to pixel screen coords."""
    return (wx - cam_x) * cell_size, (wy - cam_y) * cell_size

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            width, height = event.w, event.h
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            cols = width // cell_size
            rows = height // cell_size
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()

    keys = pygame.key.get_pressed()
    dx, dy = 0.0, 0.0
    if keys[pygame.K_w]:
        dy -= speed / cell_size
    if keys[pygame.K_s]:
        dy += speed / cell_size
    if keys[pygame.K_a]:
        dx -= speed / cell_size
    if keys[pygame.K_d]:
        dx += speed / cell_size

    next_x = world_x + dx
    next_y = world_y + dy
    check_tile = map_grid.get((int(next_y), int(next_x)), None)
    if check_tile != 'rock':
        world_x = next_x
        world_y = next_y
        world_x = max(-10000, min(world_x, 10000))
        world_y = max(-10000, min(world_y, 10000))

    cam_x = world_x - cols / 2
    cam_y = world_y - rows / 2

    tile_left  = int(cam_x) - 1
    tile_top   = int(cam_y) - 1
    tile_right  = tile_left + cols + 3
    tile_bottom = tile_top  + rows + 3
    ensure_map_area(tile_top, tile_left, tile_bottom, tile_right)

    trail.append((world_x, world_y))
    if len(trail) > trail_length:
        trail.pop(0)

    for row in range(tile_top, tile_bottom):
        for col in range(tile_left, tile_right):
            tile = map_grid[(row, col)]
            px = (col - cam_x) * cell_size
            py = (row - cam_y) * cell_size
            ipx, ipy = int(px), int(py)
            if tile == 'soil':
                pygame.draw.rect(screen, soil_color, (ipx, ipy, cell_size + 1, cell_size + 1))
            elif tile == 'fossil':
                pygame.draw.rect(screen, soil_color, (ipx, ipy, cell_size + 1, cell_size + 1))
                screen.blit(fossil_img, (ipx, ipy))
            elif tile == 'rock':
                pygame.draw.rect(screen, rock_color, (ipx, ipy, cell_size + 1, cell_size + 1))
                screen.blit(rock_img, (ipx, ipy))
            elif tile == 'darker_soil':
                pygame.draw.rect(screen, darker_soil, (ipx, ipy, cell_size + 1, cell_size + 1))
            elif tile == 'lighter_soil':
                pygame.draw.rect(screen, lighter_soil, (ipx, ipy, cell_size + 1, cell_size + 1))
            elif tile == 'air':
                pygame.draw.rect(screen, air_color, (ipx, ipy, cell_size + 1, cell_size + 1))

    # draw the trail
    for i, (tx, ty) in enumerate(trail):
        alpha = int(255 * (i + 1) / trail_length)
        spx, spy = world_to_screen(tx, ty, cam_x, cam_y)
        soil = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        soil.fill((139, 69, 19, alpha))
        screen.blit(soil, (int(spx), int(spy)))

    # render mole and the correct pos
    mole_sx, mole_sy = world_to_screen(world_x, world_y, cam_x, cam_y)
    screen.blit(mole_img, (int(mole_sx), int(mole_sy)))

    pygame.display.flip()
    clock.tick(60)