import pygame

pygame.init()

width, height = 600, 400
screen = pygame.display.set_mode((width, height))

# Setting name for window
pygame.display.set_caption('Mole in da hole')

# creating a bool value which checks 
# if game is running
running = True

square_size = 40
x, y = width // 2 - square_size // 2, height // 2 - square_size // 2
speed = 5
clock = pygame.time.Clock()

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

    screen.fill((30, 30, 30))
    pygame.draw.rect(screen, (0, 200, 255), (x, y, square_size, square_size))
    pygame.display.flip()
    clock.tick(60)