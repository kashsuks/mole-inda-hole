import pygame

pygame.init()

width, height = 600, 400
screen = pygame.display.set_mode((width, height))

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

trail = []  # (x, y) coords
trail_length = 20

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

    screen.fill((30, 30, 30))

    # draw the trial with the fading brown
    for i, (tx, ty) in enumerate(trail):
        alpha = int(255 * (i + 1) / trail_length)
        soil = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        soil.fill((139, 69, 19, alpha))  # control the brown trial with alpha rgba
        screen.blit(soil, (tx, ty))

    # Draw mole
    screen.blit(mole_img, (x, y))

    pygame.display.flip()
    clock.tick(60)