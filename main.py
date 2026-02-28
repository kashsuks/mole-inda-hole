import pygame
from noise import pnoise2
import random

pygame.init()


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
offset_x, offset_y = 0, 0  # top-left cell of the visible screen

mole_img = pygame.image.load("assets/mole.png")
mole_img = pygame.transform.scale(mole_img, (square_size, square_size))

fossil_img = pygame.image.load("assets/fossil1.png")
fossil_img = pygame.transform.scale(fossil_img, (cell_size, cell_size))
rock_img = pygame.image.load("assets/rock1.png")
rock_img = pygame.transform.scale(rock_img, (cell_size, cell_size))

trail = []  # (x, y) coords
trail_length = 20

## Perlin noise map gen
soil_color = (160, 82, 45)  # new shade for soil
rock_color = (100, 100, 100)
air_color = (30, 30, 30)
fossil_chance = 0.07
rock_chance = 0.10
seed = random.randint(0, 10000)

# map grid for (row, col)
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
        return 'air'

def ensure_map_area(top, left, bottom, right):
    for row in range(top, bottom):
        for col in range(left, right):
            if (row, col) not in map_grid:
                map_grid[(row, col)] = generate_tile(row, col)

# basic ass pygame loop
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

    world_x += dx
    world_y += dy
    world_x = max(-10000, min(world_x, 10000))
    world_y = max(-10000, min(world_y, 10000))

    offset_x = int(world_x - cols // 2)
    offset_y = int(world_y - rows // 2)

    ensure_map_area(offset_y, offset_x, offset_y + rows, offset_x + cols)

    # screen pos
    mole_screen_x = int((world_x - offset_x) * cell_size)
    mole_screen_y = int((world_y - offset_y) * cell_size)
    trail.append((mole_screen_x, mole_screen_y))
    if len(trail) > trail_length:
        trail.pop(0)

    for row in range(offset_y, offset_y + rows):
        for col in range(offset_x, offset_x + cols):
            tile = map_grid[(row, col)]
            px, py = (col - offset_x) * cell_size, (row - offset_y) * cell_size
            if tile == 'soil':
                pygame.draw.rect(screen, soil_color, (px, py, cell_size, cell_size))
            elif tile == 'fossil':
                pygame.draw.rect(screen, soil_color, (px, py, cell_size, cell_size))
                screen.blit(fossil_img, (px, py))
            elif tile == 'rock':
                pygame.draw.rect(screen, rock_color, (px, py, cell_size, cell_size))
                screen.blit(rock_img, (px, py))
            elif tile == 'air':
                pygame.draw.rect(screen, air_color, (px, py, cell_size, cell_size))

    # draw the trail with the fading brown
    for i, (tx, ty) in enumerate(trail):
        alpha = int(255 * (i + 1) / trail_length)
        soil = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        soil.fill((139, 69, 19, alpha))
        screen.blit(soil, (tx, ty))

    # Draw mole
    screen.blit(mole_img, (mole_screen_x, mole_screen_y))

    pygame.display.flip()
    clock.tick(60)