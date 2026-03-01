import pygame
from noise import pnoise2
import random
import math
import time

def draw_text(surface, text, size, x, y, color=(255,255,255)):
    font = pygame.font.Font("assets/Ithaca-LVB75.ttf", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def settings_screen(screen, width, height, music_volume, sfx_volume):
    running = True
    slider_rect_music = pygame.Rect(width//2-150, height//2-60, 300, 20)
    slider_rect_sfx = pygame.Rect(width//2-150, height//2+20, 300, 20)
    knob_radius = 12
    music_knob_x = int(slider_rect_music.x + music_volume * slider_rect_music.width)
    sfx_knob_x = int(slider_rect_sfx.x + sfx_volume * slider_rect_sfx.width)
    dragging_music = False
    dragging_sfx = False
    font_size = 32
    back_rect = pygame.Rect(width//2-60, height//2+80, 120, 40)
    while running:
        screen.fill((30,30,30))
        draw_text(screen, "Settings", 48, width//2, height//2-120)
        draw_text(screen, "Music Volume", font_size, width//2, height//2-80)
        draw_text(screen, "SFX Volume", font_size, width//2, height//2)
        pygame.draw.rect(screen, (120,120,120), slider_rect_music)
        pygame.draw.rect(screen, (120,120,120), slider_rect_sfx)
        pygame.draw.circle(screen, (70,130,180), (music_knob_x, slider_rect_music.y+10), knob_radius)
        pygame.draw.circle(screen, (70,130,180), (sfx_knob_x, slider_rect_sfx.y+10), knob_radius)
        pygame.draw.rect(screen, (70,130,180), back_rect)
        draw_text(screen, "Back", 32, back_rect.centerx, back_rect.centery)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if (music_knob_x-knob_radius <= mx <= music_knob_x+knob_radius and
                    slider_rect_music.y <= my <= slider_rect_music.y+20):
                    dragging_music = True
                if (sfx_knob_x-knob_radius <= mx <= sfx_knob_x+knob_radius and
                    slider_rect_sfx.y <= my <= slider_rect_sfx.y+20):
                    dragging_sfx = True
                if back_rect.collidepoint(mx, my):
                    running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_music = False
                dragging_sfx = False
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if dragging_music:
                    music_knob_x = max(slider_rect_music.x, min(mx, slider_rect_music.x+slider_rect_music.width))
                    music_volume = (music_knob_x - slider_rect_music.x) / slider_rect_music.width
                    pygame.mixer.music.set_volume(music_volume)
                if dragging_sfx:
                    sfx_knob_x = max(slider_rect_sfx.x, min(mx, slider_rect_sfx.x+slider_rect_sfx.width))
                    sfx_volume = (sfx_knob_x - slider_rect_sfx.x) / slider_rect_sfx.width
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        pygame.display.flip()
        pygame.time.Clock().tick(60)
    return music_volume, sfx_volume

def start_screen(screen, width, height, music_volume, sfx_volume):
    play_rect = pygame.Rect(width//2-100, height//2-40, 200, 50)
    settings_rect = pygame.Rect(width//2-100, height//2+30, 200, 50)
    pygame.mixer.music.load("assets/loading.flac")
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)
    while True:
        screen.fill((30, 30, 30))
        draw_text(screen, "Mole in da hole", 60, width//2, height//2-120)
        pygame.draw.rect(screen, (70, 130, 180), play_rect)
        draw_text(screen, "Play", 40, width//2, height//2-15)
        pygame.draw.rect(screen, (120, 120, 120), settings_rect)
        draw_text(screen, "Settings", 40, width//2, height//2+55)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if play_rect.collidepoint(mx, my):
                    pygame.mixer.music.stop()
                    return 'play', music_volume, sfx_volume
                if settings_rect.collidepoint(mx, my):
                    music_volume, sfx_volume = settings_screen(screen, width, height, music_volume, sfx_volume)
                    pygame.mixer.music.set_volume(music_volume)
        pygame.display.flip()
        pygame.time.Clock().tick(60)


pygame.init()
pygame.mixer.init()

width, height = 800, 600
cell_size = 40
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
cols = width // cell_size
rows = height // cell_size

pygame.display.set_caption('Mole in da hole')

running = True
square_size = 40
speed = 5
clock = pygame.time.Clock()

world_x, world_y = float(cols // 2), float(rows // 2)
music_volume = 0.5
sfx_volume = 0.5

def play_sound(path):
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(sfx_volume)
        sound.play()
    except Exception:
        pass

# Load images
fossil_img = pygame.transform.scale(pygame.image.load("assets/fossil1.png"), (cell_size, cell_size))
rock_img   = pygame.transform.scale(pygame.image.load("assets/rock1.png"),   (cell_size, cell_size))
medkit_img = pygame.transform.scale(pygame.image.load("assets/medkit.png"),  (cell_size, cell_size))

mole_img_orig = pygame.transform.scale(pygame.image.load("assets/mole.png"), (square_size, square_size))
mole_img = mole_img_orig
dirt_imgs = [pygame.transform.scale(pygame.image.load(f"assets/dirt{i}.png"), (cell_size, cell_size)) for i in range(1,4)]

heart_size = 40
w_heart_img   = pygame.transform.scale(pygame.image.load("assets/heart-full.png"),  (heart_size, heart_size))
half_heart_img = pygame.transform.scale(pygame.image.load("assets/heart-half.png"), (heart_size, heart_size))
empty_heart_img = pygame.transform.scale(pygame.image.load("assets/heart-empty.png"), (heart_size, heart_size))

key_size = 48
w_key_img = pygame.transform.scale(pygame.image.load("assets/w_key.png"), (key_size, key_size))
a_key_img = pygame.transform.scale(pygame.image.load("assets/a_key.png"), (key_size, key_size))
s_key_img = pygame.transform.scale(pygame.image.load("assets/s_key.png"), (key_size, key_size))
d_key_img = pygame.transform.scale(pygame.image.load("assets/d_key.png"), (key_size, key_size))

# Slash animation
slash_img = pygame.image.load("assets/Slash.png")
slash_width, slash_height = slash_img.get_size()
slash_frame_width = slash_width // 6
slash_big_size = int(square_size * 4)
slash_frames = [
    pygame.transform.scale(
        slash_img.subsurface(pygame.Rect(i * slash_frame_width, 0, slash_frame_width, slash_height)),
        (slash_big_size, slash_big_size))
    for i in range(6)
]

# Revolver icon
REVOLVER_ICON_SIZE = 56
REVOLVER_COST = 30
REVOLVER_MAX_BULLETS = 12
revolver_icon = pygame.transform.scale(pygame.image.load("assets/revolver.png"), (REVOLVER_ICON_SIZE, REVOLVER_ICON_SIZE))
revolver_unlocked = False
revolver_equipped = False
bullets = REVOLVER_MAX_BULLETS

BULLET_SPEED  = 0.35
BULLET_RANGE  = 15.0
BULLET_RADIUS = 0.4
BULLET_SIZE_PX = 6
active_bullets = []   # each: [wx, wy, dx, dy, dist_traveled]

glow_t = 0.0
buy_prompt_text = ""
buy_prompt_until = 0
shoot_held = False   # prevent holding space from firing every frame

trail = []
trail_length = 20
air_color = (30, 30, 30)
fossil_chance = 0.07
rock_chance   = 0.10
seed = random.randint(0, 10000)

map_grid   = {}
coin_tiles  = set()
medkit_tiles = set()
coin_spawn_chance = 0.03

def generate_tile(row, col):
    n = pnoise2(col * 0.15 + seed, row * 0.15 + seed)
    if n > -0.2:
        if n > 0.25 and random.random() < rock_chance:
            return 'rock'
        elif n > 0.1 and random.random() < fossil_chance:
            return 'fossil'
        else:
            if random.random() < coin_spawn_chance:
                coin_tiles.add((row, col))
            if random.random() < 0.01:
                medkit_tiles.add((row, col))
            return f'dirt{random.randint(1,3)}'
    else:
        r = random.random()
        if r < 0.66:
            if random.random() < coin_spawn_chance:
                coin_tiles.add((row, col))
            if random.random() < 0.01:
                medkit_tiles.add((row, col))
            return f'dirt{random.randint(1,3)}'
        else:
            return 'air'

def ensure_map_area(top, left, bottom, right):
    for row in range(top, bottom):
        for col in range(left, right):
            if (row, col) not in map_grid:
                map_grid[(row, col)] = generate_tile(row, col)

def world_to_screen(wx, wy, cam_x, cam_y):
    return (wx - cam_x) * cell_size, (wy - cam_y) * cell_size

def draw_revolver_hud(surface, coin_count, unlocked, equipped, bul, w, h, gt):
    ix = w - REVOLVER_ICON_SIZE - 20
    iy = h - REVOLVER_ICON_SIZE - 20

    if not unlocked:
        if coin_count >= REVOLVER_COST:
            # Glowing — draw icon normally with gold pulse overlay
            surface.blit(revolver_icon, (ix, iy))
            pulse = int(60 + 50 * math.sin(gt * 4))
            glow_surf = pygame.Surface((REVOLVER_ICON_SIZE, REVOLVER_ICON_SIZE), pygame.SRCALPHA)
            glow_surf.fill((255, 215, 0, pulse))
            surface.blit(glow_surf, (ix, iy))
            # Gold border
            glow_col = (255, int(180 + 75 * math.sin(gt * 4)), 0)
            pygame.draw.rect(surface, glow_col, (ix-3, iy-3, REVOLVER_ICON_SIZE+6, REVOLVER_ICON_SIZE+6), 3)
            # Prompt
            draw_text(surface, f"[E]  Buy  {REVOLVER_COST} coins", 19,
                      ix + REVOLVER_ICON_SIZE//2, iy - 16, (255, 215, 0))
        else:
            # Faded icon
            faded = revolver_icon.copy()
            faded.set_alpha(55)
            surface.blit(faded, (ix, iy))
            # Progress bar
            progress = coin_count / REVOLVER_COST
            bar_w = REVOLVER_ICON_SIZE
            pygame.draw.rect(surface, (70,70,70),  (ix, iy+REVOLVER_ICON_SIZE+4, bar_w, 6))
            pygame.draw.rect(surface, (180,140,40), (ix, iy+REVOLVER_ICON_SIZE+4, int(bar_w*progress), 6))
            draw_text(surface, f"{coin_count}/{REVOLVER_COST}", 17,
                      ix + REVOLVER_ICON_SIZE//2, iy+REVOLVER_ICON_SIZE+18, (150,150,150))
    else:
        # Unlocked
        if equipped:
            pygame.draw.rect(surface, (255,100,50), (ix-3, iy-3, REVOLVER_ICON_SIZE+6, REVOLVER_ICON_SIZE+6), 3)
        surface.blit(revolver_icon, (ix, iy))
        # Bullet pips — two rows of 6
        pip_r = 5
        pip_gap = 14
        for b in range(REVOLVER_MAX_BULLETS):
            row_n = b // 6
            col_n = b % 6
            px = ix + col_n * pip_gap + pip_r
            py = iy - 14 - row_n * 14
            color = (220, 180, 50) if b < bul else (55, 55, 55)
            pygame.draw.circle(surface, color, (px, py), pip_r)
        hint = "[1] equipped" if equipped else "[1] equip"
        draw_text(surface, hint, 17, ix + REVOLVER_ICON_SIZE//2, iy+REVOLVER_ICON_SIZE+12, (190,190,190))

# Enemy setup
enemy_img = pygame.transform.scale(mole_img_orig, (square_size, square_size))
num_enemies = 3
enemy_speed = 2.5 / cell_size
enemy_positions = [[world_x + random.randint(-10,10), world_y + random.randint(-10,10)] for _ in range(num_enemies)]

coin_imgs = [pygame.transform.scale(pygame.image.load(f"assets/coin{i}.png"), (cell_size, cell_size)) for i in range(1,9)]
coin_anim_speed = 0.15

max_health = 6
health = max_health
shake_time = 0
shake_intensity = 0
enemy_attack_cooldown = 0

player_slash_frame = None
player_slash_time  = 0
player_slash_hit_this_swing = set()
enemy_slash_frames = [None] * num_enemies
enemy_slash_times  = [0]    * num_enemies

PLAYER_SLASH_REACH = 1.5
ENEMY_ATTACK_REACH = 1.2

choice, music_volume, sfx_volume = start_screen(screen, width, height, music_volume, sfx_volume)
if choice == 'play':
    pygame.mixer.music.load("assets/main.flac")
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)

coin_count = 0
last_dir   = 'down'
dt = 1/60

while running:
    # ── Events ──────────────────────────────────────────────────────
    space_pressed_this_frame = False
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
            elif event.key == pygame.K_ESCAPE:
                music_volume, sfx_volume = settings_screen(screen, width, height, music_volume, sfx_volume)
                pygame.mixer.music.set_volume(music_volume)
            elif event.key == pygame.K_e:
                if not revolver_unlocked and coin_count >= REVOLVER_COST:
                    revolver_unlocked = True
                    revolver_equipped = True
                    coin_count -= REVOLVER_COST
                    bullets = REVOLVER_MAX_BULLETS
                    buy_prompt_text  = "Revolver unlocked!"
                    buy_prompt_until = pygame.time.get_ticks() + 2200
                elif not revolver_unlocked:
                    buy_prompt_text  = f"Need {REVOLVER_COST} coins to buy!"
                    buy_prompt_until = pygame.time.get_ticks() + 1200
            elif event.key == pygame.K_1:
                if revolver_unlocked:
                    revolver_equipped = not revolver_equipped
            elif event.key == pygame.K_SPACE:
                space_pressed_this_frame = True

    keys = pygame.key.get_pressed()
    glow_t += dt

    # ── Melee (space, only when revolver NOT equipped) ───────────────
    if space_pressed_this_frame and not revolver_equipped and player_slash_frame is None:
        player_slash_frame = 0
        player_slash_time  = pygame.time.get_ticks()
        player_slash_hit_this_swing = set()

    # ── Shoot (space when revolver equipped — one shot per press) ────
    if space_pressed_this_frame and revolver_equipped and bullets > 0:
        dir_map = {'up':(0,-1), 'down':(0,1), 'left':(-1,0), 'right':(1,0)}
        bdx, bdy = dir_map.get(last_dir, (0,1))
        active_bullets.append([world_x, world_y, bdx, bdy, 0.0])
        bullets -= 1
        play_sound("assets/shoot.mp3")

    # ── Movement ─────────────────────────────────────────────────────
    dx, dy = 0.0, 0.0
    dir_now = None
    if keys[pygame.K_w]: dy -= speed / cell_size; dir_now = 'up'
    if keys[pygame.K_s]: dy += speed / cell_size; dir_now = 'down'
    if keys[pygame.K_a]: dx -= speed / cell_size; dir_now = 'left'
    if keys[pygame.K_d]: dx += speed / cell_size; dir_now = 'right'

    if dir_now:
        last_dir = dir_now
        if   last_dir == 'up':    mole_img = mole_img_orig
        elif last_dir == 'down':  mole_img = pygame.transform.rotate(mole_img_orig, 180)
        elif last_dir == 'left':  mole_img = pygame.transform.rotate(mole_img_orig, 90)
        elif last_dir == 'right': mole_img = pygame.transform.rotate(mole_img_orig, -90)

    next_x = world_x + dx
    next_y = world_y + dy
    if map_grid.get((int(next_y), int(next_x)), None) != 'rock':
        world_x = max(-10000, min(next_x, 10000))
        world_y = max(-10000, min(next_y, 10000))
        ptile = (int(world_y), int(world_x))
        if ptile in coin_tiles:
            coin_tiles.remove(ptile)
            play_sound("assets/coin-collect.mp3")
            coin_count += 1
        if ptile in medkit_tiles:
            medkit_tiles.remove(ptile)
            health = min(max_health, health + 2)

    cam_x = world_x - cols / 2
    cam_y = world_y - rows / 2
    if shake_time > pygame.time.get_ticks():
        cam_x += random.uniform(-shake_intensity, shake_intensity)
        cam_y += random.uniform(-shake_intensity, shake_intensity)

    tile_left   = int(cam_x) - 1
    tile_top    = int(cam_y) - 1
    tile_right  = tile_left + cols + 3
    tile_bottom = tile_top  + rows + 3
    ensure_map_area(tile_top, tile_left, tile_bottom, tile_right)

    trail.append((world_x, world_y))
    if len(trail) > trail_length:
        trail.pop(0)

    coin_frame = int((pygame.time.get_ticks() / 1000 / coin_anim_speed) % len(coin_imgs))

    # ── Move bullets ─────────────────────────────────────────────────
    dead_bullets = []
    for bi, b in enumerate(active_bullets):
        b[0] += b[2] * BULLET_SPEED
        b[1] += b[3] * BULLET_SPEED
        b[4] += BULLET_SPEED
        if b[4] > BULLET_RANGE or map_grid.get((int(b[1]), int(b[0])), 'air') == 'rock':
            dead_bullets.append(bi)
            continue
        for i in range(num_enemies):
            ex, ey = enemy_positions[i]
            if math.hypot(b[0]-ex, b[1]-ey) < BULLET_RADIUS:
                d = math.hypot(ex-b[0], ey-b[1]) or 0.001
                enemy_positions[i][0] += (ex-b[0])/d * 3.0
                enemy_positions[i][1] += (ey-b[1])/d * 3.0
                dead_bullets.append(bi)
                play_sound("assets/hurt.mp3")
                break
    for bi in sorted(set(dead_bullets), reverse=True):
        active_bullets.pop(bi)

    # ── Draw tiles ────────────────────────────────────────────────────
    for row in range(tile_top, tile_bottom):
        for col in range(tile_left, tile_right):
            tile = map_grid[(row, col)]
            ipx = int((col - cam_x) * cell_size)
            ipy = int((row - cam_y) * cell_size)
            if tile.startswith('dirt'):
                screen.blit(dirt_imgs[int(tile[-1])-1], (ipx, ipy))
            elif tile == 'fossil':
                screen.blit(dirt_imgs[0], (ipx, ipy))
                screen.blit(fossil_img, (ipx, ipy))
            elif tile == 'rock':
                screen.blit(rock_img, (ipx, ipy))
            elif tile == 'air':
                pygame.draw.rect(screen, air_color, (ipx, ipy, cell_size+1, cell_size+1))
            if (row, col) in coin_tiles:
                screen.blit(coin_imgs[coin_frame], (ipx, ipy))
            if (row, col) in medkit_tiles:
                screen.blit(medkit_img, (ipx, ipy))

    # ── Draw bullets ──────────────────────────────────────────────────
    for b in active_bullets:
        bsx, bsy = world_to_screen(b[0], b[1], cam_x, cam_y)
        pygame.draw.circle(screen, (255, 240, 100), (int(bsx), int(bsy)), BULLET_SIZE_PX)
        pygame.draw.circle(screen, (200, 150,  20), (int(bsx), int(bsy)), BULLET_SIZE_PX - 2)

    # ── Enemy AI + damage ─────────────────────────────────────────────
    for i in range(num_enemies):
        ex, ey = enemy_positions[i]
        ddx = world_x - ex
        ddy = world_y - ey
        dist = math.hypot(ddx, ddy)

        if dist > 0.1:
            move_x = enemy_speed * ddx / dist
            move_y = enemy_speed * ddy / dist
            nex, ney = ex + move_x, ey + move_y
            if map_grid.get((int(ney), int(nex)), None) != 'rock':
                enemy_positions[i][0] = nex
                enemy_positions[i][1] = ney

        if dist < ENEMY_ATTACK_REACH and health > 0:
            if pygame.time.get_ticks() > enemy_attack_cooldown:
                health -= 1
                enemy_attack_cooldown = pygame.time.get_ticks() + 1000
                enemy_slash_frames[i] = 0
                enemy_slash_times[i]  = pygame.time.get_ticks()
                shake_time = pygame.time.get_ticks() + 200
                shake_intensity = 0.15
                play_sound("assets/hurt.mp3")

        if (player_slash_frame is not None
                and player_slash_frame < 6
                and i not in player_slash_hit_this_swing
                and dist < PLAYER_SLASH_REACH):
            player_slash_hit_this_swing.add(i)
            if dist > 0:
                enemy_positions[i][0] += (ex - world_x) / dist * 2.0
                enemy_positions[i][1] += (ey - world_y) / dist * 2.0
            play_sound("assets/hurt.mp3")

    # ── Draw enemies ──────────────────────────────────────────────────
    for i in range(num_enemies):
        ex, ey = enemy_positions[i]
        esx, esy = world_to_screen(ex, ey, cam_x, cam_y)
        screen.blit(enemy_img, (int(esx), int(esy)))
        if enemy_slash_frames[i] is not None:
            if pygame.time.get_ticks() - enemy_slash_times[i] > 50:
                enemy_slash_frames[i] += 1
                enemy_slash_times[i]   = pygame.time.get_ticks()
            if enemy_slash_frames[i] < 6:
                screen.blit(slash_frames[enemy_slash_frames[i]], (int(esx), int(esy)))
            else:
                enemy_slash_frames[i] = None

    # ── Trail ─────────────────────────────────────────────────────────
    for idx, (tx, ty) in enumerate(trail):
        alpha = int(255 * (idx+1) / trail_length)
        spx, spy = world_to_screen(tx, ty, cam_x, cam_y)
        soil = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        soil.fill((139, 69, 19, alpha))
        screen.blit(soil, (int(spx), int(spy)))

    # ── Mole ──────────────────────────────────────────────────────────
    mole_sx, mole_sy = world_to_screen(world_x, world_y, cam_x, cam_y)
    screen.blit(mole_img, (int(mole_sx), int(mole_sy)))

    # ── Player slash ──────────────────────────────────────────────────
    if player_slash_frame is not None:
        if pygame.time.get_ticks() - player_slash_time > 50:
            player_slash_frame += 1
            player_slash_time   = pygame.time.get_ticks()
        if player_slash_frame < 6:
            screen.blit(slash_frames[player_slash_frame], (int(mole_sx), int(mole_sy)))
        else:
            player_slash_frame = None

    # ── WASD hints ────────────────────────────────────────────────────
    key_x = 40
    key_y = height - 120
    for key_const, img, ox, oy in [
        (pygame.K_w, w_key_img, key_size, 0),
        (pygame.K_a, a_key_img, 0, key_size),
        (pygame.K_s, s_key_img, key_size, key_size),
        (pygame.K_d, d_key_img, key_size*2, key_size),
    ]:
        ic = img.copy()
        ic.set_alpha(255 if keys[key_const] else 100)
        screen.blit(ic, (key_x+ox, key_y+oy))

    # ── Coin counter ──────────────────────────────────────────────────
    draw_text(screen, f"Coins: {coin_count}", 32, width-100, 40, (255,223,0))

    # ── Hearts ────────────────────────────────────────────────────────
    h = health
    for i in range(3):
        himg = w_heart_img if h >= 2 else (half_heart_img if h == 1 else empty_heart_img)
        screen.blit(himg, (40 + i*(heart_size+8), 40))
        h -= 2

    # ── Revolver HUD ──────────────────────────────────────────────────
    draw_revolver_hud(screen, coin_count, revolver_unlocked, revolver_equipped,
                      bullets, width, height, glow_t)

    # ── Buy prompt flash ──────────────────────────────────────────────
    if pygame.time.get_ticks() < buy_prompt_until:
        draw_text(screen, buy_prompt_text, 28, width//2, height//2 - 60, (255, 215, 0))

    pygame.display.flip()
    dt = clock.tick(60) / 1000.0

pygame.quit()