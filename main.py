import pygame
from noise import pnoise2
import random

pygame.init()

width, height = 600, 400
screen = pygame.display.set_mode((width, height))
cell_size = 40
cols = width // cell_size
rows = height // cell_size

pygame.display.set_caption('Mole in da hole')

# creating a bool value which checks 
# if game is running
running = True

square_size = 40
x, y = width // 2 - square_size // 2, height // 2 - square_size // 2
speed = 5
clock = pygame.time.Clock()

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
map_grid = []
for row in range(rows):
    map_row = []
    for col in range(cols):
        n = pnoise2(col * 0.15 + seed, row * 0.15 + seed)
        if n > -0.2:  # everything below is air
            if n > 0.25 and random.random() < rock_chance:
                map_row.append('rock')
            elif n > 0.1 and random.random() < fossil_chance:
                map_row.append('fossil')
            else:
                map_row.append('soil')
        else:
            map_row.append('air')
    map_grid.append(map_row)

# basic ass pygame loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        y -= speed
    if keys[pygame.K_s]:
        y += speed
    if keys[pygame.K_a]:
        x -= speed
    if keys[pygame.K_d]:
        x += speed

    # clamp the position into the canvas
    x = max(0, min(x, width - square_size))
    y = max(0, min(y, height - square_size))

    # Update trail
    trail.append((x, y))
    if len(trail) > trail_length:
        trail.pop(0)

    # Draw map
    for row in range(rows):
        for col in range(cols):
            tile = map_grid[row][col]
            px, py = col * cell_size, row * cell_size
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
    screen.blit(mole_img, (x, y))

    pygame.display.flip()
    clock.tick(60)