import pygame
from noise import pnoise2
import random
import math
import time
import json

def draw_text(surface, text, size, x, y, color=(255,255,255)):
    font = pygame.font.Font("assets/Ithaca-LVB75.ttf", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def load_unlocked_achievements(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("unlocked", []))
    except Exception:
        return set()

def save_unlocked_achievements(path, unlocked):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"unlocked": sorted(unlocked)}, f)

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
fossil_img  = pygame.transform.scale(pygame.image.load("assets/fossil1.png"), (cell_size, cell_size))
rock_img    = pygame.transform.scale(pygame.image.load("assets/rock1.png"),   (cell_size, cell_size))
medkit_img  = pygame.transform.scale(pygame.image.load("assets/medkit.png"),  (cell_size, cell_size))
bullet_img  = pygame.transform.scale(pygame.image.load("assets/bullet.png"),  (cell_size, cell_size))
lightning_img = pygame.transform.scale(pygame.image.load("assets/lightning.png"), (cell_size, cell_size))
# NEW: Spawner image
spawner_img = pygame.transform.scale(pygame.image.load("assets/spawner.png").convert_alpha(), (cell_size, cell_size))

mole_img_orig = pygame.transform.scale(pygame.image.load("assets/mole.png"), (square_size, square_size))
mole_img = mole_img_orig
dirt_imgs = [pygame.transform.scale(pygame.image.load(f"assets/dirt{i}.png"), (cell_size, cell_size)) for i in range(1,4)]

heart_size = 40
w_heart_img    = pygame.transform.scale(pygame.image.load("assets/heart-full.png"),  (heart_size, heart_size))
half_heart_img = pygame.transform.scale(pygame.image.load("assets/heart-half.png"),  (heart_size, heart_size))
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

# Revolver icon - CENTER BOTTOM POSITION
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
shoot_held = False

ACHIEVEMENT_SAVE_FILE = "achievements.json"
ACHIEVEMENT_POPUP_MS = 3500
ACHIEVEMENT_FADE_MS = 300

ACHIEVEMENTS = {
    "first_start": "A shit show",
    "rookie_richie": "Rookie Richie",
    "finally_american": "Finally american",
    "flash_guess": "I guess you're flash",
}

unlocked_achievements = load_unlocked_achievements(ACHIEVEMENT_SAVE_FILE)
achievement_queue = []
active_achievement = None

KONAMI_CODE = ["up", "up", "down", "down", "left", "right", "left", "right", "b", "a"]
konami_buffer = []

trail = []
trail_length = 20
air_color = (30, 30, 30)
fossil_chance = 0.07
rock_chance   = 0.10
seed = random.randint(0, 10000)

map_grid    = {}
coin_tiles  = set()
medkit_tiles = set()
bullet_tiles = set()
lightning_tiles = set()
# NEW: Spawner tiles set
spawner_tiles = set()
coin_spawn_chance = 0.03

# NEW: Spawner settings
SPAWNER_SPAWN_CHANCE = 0.008  # Chance per valid tile
SPAWNER_MIN_DISTANCE_FROM_PLAYER = 8  # Keep enough distance, but still allow spawning in generated area
ENEMY_SPAWN_INTERVAL = 3000  # Spawn enemy every 3 seconds from each spawner
MAX_ENEMIES_PER_SPAWNER = 3  # Max enemies per spawner at once

# NEW: Speed powerup settings
LIGHTNING_COST = 10
BASE_SPEED = 5
speed_boost_active = False
speed_boost_multiplier = 2.0
speed_boost_end_time = 0
SPEED_BOOST_DURATION = 5000

# NEW: Enemy management (no longer fixed positions)
enemy_img = pygame.transform.scale(mole_img_orig, (square_size, square_size))
enemy_speed = 2.5 / cell_size
enemy_positions = []  # Now dynamic list
enemy_spawn_timers = {}  # spawner_pos -> last_spawn_time
enemy_health = []

# Track which spawner spawned which enemy
enemy_source_spawner = {}  # enemy_idx -> spawner_pos

coin_imgs = [pygame.transform.scale(pygame.image.load(f"assets/coin{i}.png"), (cell_size, cell_size)) for i in range(1,9)]
coin_anim_speed = 0.15

achievement_icons = {
    "first_start": mole_img_orig,
    "rookie_richie": coin_imgs[0],
    "finally_american": revolver_icon,
    "flash_guess": lightning_img,
}

max_health = 6
health = max_health
shake_time = 0
shake_intensity = 0
enemy_attack_cooldown = 0

player_slash_frame = None
player_slash_time  = 0
player_slash_hit_this_swing = set()
enemy_slash_frames = []
enemy_slash_times  = []

PLAYER_SLASH_REACH = 1.5
ENEMY_ATTACK_REACH = 1.2

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
            if random.random() < 0.01:
                if (row, col) not in coin_tiles and (row, col) not in medkit_tiles:
                    bullet_tiles.add((row, col))
            if random.random() < 0.005:
                if (row, col) not in coin_tiles and (row, col) not in medkit_tiles and (row, col) not in bullet_tiles:
                    lightning_tiles.add((row, col))
            # NEW: Spawner spawn logic - avoid all other items
            if random.random() < SPAWNER_SPAWN_CHANCE:
                if ((row, col) not in coin_tiles and 
                    (row, col) not in medkit_tiles and 
                    (row, col) not in bullet_tiles and
                    (row, col) not in lightning_tiles):
                    # Check distance from player
                    dist_from_player = math.hypot(col - world_x, row - world_y)
                    if dist_from_player >= SPAWNER_MIN_DISTANCE_FROM_PLAYER:
                        spawner_tiles.add((row, col))
                        enemy_spawn_timers[(row, col)] = 0
            return f'dirt{random.randint(1,3)}'
    else:
        r = random.random()
        if r < 0.66:
            if random.random() < coin_spawn_chance:
                coin_tiles.add((row, col))
            if random.random() < 0.01:
                medkit_tiles.add((row, col))
            if random.random() < 0.01:
                if (row, col) not in coin_tiles and (row, col) not in medkit_tiles:
                    bullet_tiles.add((row, col))
            if random.random() < 0.005:
                if (row, col) not in coin_tiles and (row, col) not in medkit_tiles and (row, col) not in bullet_tiles:
                    lightning_tiles.add((row, col))
            # NEW: Spawner spawn logic in secondary area
            if random.random() < SPAWNER_SPAWN_CHANCE:
                if ((row, col) not in coin_tiles and 
                    (row, col) not in medkit_tiles and 
                    (row, col) not in bullet_tiles and
                    (row, col) not in lightning_tiles):
                    dist_from_player = math.hypot(col - world_x, row - world_y)
                    if dist_from_player >= SPAWNER_MIN_DISTANCE_FROM_PLAYER:
                        spawner_tiles.add((row, col))
                        enemy_spawn_timers[(row, col)] = 0
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
    ix = w // 2 - REVOLVER_ICON_SIZE // 2
    iy = h - REVOLVER_ICON_SIZE - 20

    if not unlocked:
        if coin_count >= REVOLVER_COST:
            surface.blit(revolver_icon, (ix, iy))
            pulse = int(60 + 50 * math.sin(gt * 4))
            glow_surf = pygame.Surface((REVOLVER_ICON_SIZE, REVOLVER_ICON_SIZE), pygame.SRCALPHA)
            glow_surf.fill((255, 215, 0, pulse))
            surface.blit(glow_surf, (ix, iy))
            glow_col = (255, int(180 + 75 * math.sin(gt * 4)), 0)
            pygame.draw.rect(surface, glow_col, (ix-3, iy-3, REVOLVER_ICON_SIZE+6, REVOLVER_ICON_SIZE+6), 3)
            draw_text(surface, f"[E]  Buy  {REVOLVER_COST} coins", 19,
                      ix + REVOLVER_ICON_SIZE//2, iy - 16, (255, 215, 0))
        else:
            faded = revolver_icon.copy()
            faded.set_alpha(55)
            surface.blit(faded, (ix, iy))
            progress = coin_count / REVOLVER_COST
            bar_w = REVOLVER_ICON_SIZE
            pygame.draw.rect(surface, (70,70,70),  (ix, iy+REVOLVER_ICON_SIZE+4, bar_w, 6))
            pygame.draw.rect(surface, (180,140,40), (ix, iy+REVOLVER_ICON_SIZE+4, int(bar_w*progress), 6))
            draw_text(surface, f"{coin_count}/{REVOLVER_COST}", 17,
                      ix + REVOLVER_ICON_SIZE//2, iy+REVOLVER_ICON_SIZE+18, (150,150,150))
    else:
        if equipped:
            pygame.draw.rect(surface, (255,100,50), (ix-3, iy-3, REVOLVER_ICON_SIZE+6, REVOLVER_ICON_SIZE+6), 3)
        surface.blit(revolver_icon, (ix, iy))
        pip_r = 5
        pip_gap = 14
        start_x = ix + (REVOLVER_ICON_SIZE - (6 * pip_gap)) // 2
        for b in range(REVOLVER_MAX_BULLETS):
            row_n = b // 6
            col_n = b % 6
            px = start_x + col_n * pip_gap + pip_r
            py = iy + REVOLVER_ICON_SIZE + 8 + row_n * 12
            color = (220, 180, 50) if b < bul else (55, 55, 55)
            pygame.draw.circle(surface, color, (px, py), pip_r)
        hint = "[1] equipped" if equipped else "[1] equip"
        draw_text(surface, hint, 17, ix + REVOLVER_ICON_SIZE//2, iy+REVOLVER_ICON_SIZE+35, (190,190,190))

def draw_speed_hud(surface, w, h, gt):
    icon_size = 40
    lx = w - icon_size - 20
    ly = 100

    if speed_boost_active:
        pulse = int(100 + 100 * math.sin(gt * 8))
        glow_surf = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        glow_surf.fill((255, 255, 0, pulse))
        surface.blit(glow_surf, (lx, ly))
        pygame.draw.rect(surface, (255, 255, 0), (lx-2, ly-2, icon_size+4, icon_size+4), 2)
        remaining = max(0, (speed_boost_end_time - pygame.time.get_ticks()) / 1000)
        draw_text(surface, f"SPEED! {remaining:.1f}s", 20, lx + icon_size//2, ly + icon_size + 15, (255, 255, 0))
    else:
        faded = lightning_img.copy()
        faded.set_alpha(80)
        surface.blit(faded, (lx, ly))
        draw_text(surface, f"{LIGHTNING_COST} coins", 16, lx + icon_size//2, ly + icon_size + 12, (150, 150, 150))

def unlock_achievement(key):
    global unlocked_achievements
    if key in unlocked_achievements:
        return
    unlocked_achievements.add(key)
    save_unlocked_achievements(ACHIEVEMENT_SAVE_FILE, unlocked_achievements)
    achievement_queue.append({
        "key": key,
        "name": ACHIEVEMENTS.get(key, key),
        "start": None,
    })

def draw_achievement_popup(surface, w):
    global active_achievement
    now = pygame.time.get_ticks()

    if active_achievement is None and achievement_queue:
        active_achievement = achievement_queue.pop(0)
        active_achievement["start"] = now

    if active_achievement is None:
        return

    elapsed = now - active_achievement["start"]
    if elapsed >= ACHIEVEMENT_POPUP_MS:
        active_achievement = None
        return

    alpha = 1.0
    if elapsed < ACHIEVEMENT_FADE_MS:
        alpha = elapsed / ACHIEVEMENT_FADE_MS
    elif elapsed > ACHIEVEMENT_POPUP_MS - ACHIEVEMENT_FADE_MS:
        alpha = (ACHIEVEMENT_POPUP_MS - elapsed) / ACHIEVEMENT_FADE_MS
    alpha = max(0.0, min(1.0, alpha))

    box_w, box_h = 360, 86
    x, y = w - box_w - 20, 20
    panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, int(215 * alpha)))
    border_col = (int(180 * alpha), int(180 * alpha), int(180 * alpha), int(255 * alpha))
    pygame.draw.rect(panel, border_col, panel.get_rect(), 2)

    icon = achievement_icons.get(active_achievement["key"], coin_imgs[0])
    icon_size = 48
    icon_surface = pygame.transform.scale(icon, (icon_size, icon_size)).copy()
    icon_surface.set_alpha(int(255 * alpha))
    panel.blit(icon_surface, (14, (box_h - icon_size) // 2))

    head_font = pygame.font.Font("assets/Ithaca-LVB75.ttf", 22)
    name_font = pygame.font.Font("assets/Ithaca-LVB75.ttf", 28)
    head = head_font.render("Achievement get!", True, (244, 212, 94))
    name = name_font.render(active_achievement["name"], True, (255, 255, 255))
    head.set_alpha(int(255 * alpha))
    name.set_alpha(int(255 * alpha))
    panel.blit(head, (78, 16))
    panel.blit(name, (78, 44))

    surface.blit(panel, (x, y))

# NEW: Count enemies from a specific spawner
def count_enemies_from_spawner(spawner_pos):
    count = 0
    for idx, source in enemy_source_spawner.items():
        if source == spawner_pos and idx < len(enemy_positions):
            count += 1
    return count

# NEW: Remove dead enemies and clean up tracking
def remove_enemy(idx):
    if idx < len(enemy_positions):
        enemy_positions.pop(idx)
        if idx < len(enemy_health):
            enemy_health.pop(idx)
        if idx < len(enemy_slash_frames):
            enemy_slash_frames.pop(idx)
        if idx < len(enemy_slash_times):
            enemy_slash_times.pop(idx)
        # Update source tracking indices
        new_source = {}
        for old_idx, source in enemy_source_spawner.items():
            if old_idx < idx:
                new_source[old_idx] = source
            elif old_idx > idx:
                new_source[old_idx - 1] = source
        enemy_source_spawner.clear()
        enemy_source_spawner.update(new_source)

choice, music_volume, sfx_volume = start_screen(screen, width, height, music_volume, sfx_volume)
if choice == 'play':
    pygame.mixer.music.load("assets/main.flac")
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)
    unlock_achievement("first_start")

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
            konami_map = {
                pygame.K_UP: "up",
                pygame.K_DOWN: "down",
                pygame.K_LEFT: "left",
                pygame.K_RIGHT: "right",
                pygame.K_b: "b",
                pygame.K_a: "a",
            }
            konami_input = konami_map.get(event.key)
            if konami_input:
                konami_buffer.append(konami_input)
                if len(konami_buffer) > len(KONAMI_CODE):
                    konami_buffer.pop(0)
                if konami_buffer == KONAMI_CODE:
                    coin_count += 1000
                    buy_prompt_text = "KONAMI! +1000 coins"
                    buy_prompt_until = pygame.time.get_ticks() + 1800
                    konami_buffer.clear()
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
                    unlock_achievement("finally_american")
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

    # ── Check speed boost expiration ─────────────────────────────────
    if speed_boost_active and pygame.time.get_ticks() > speed_boost_end_time:
        speed_boost_active = False

    # ── Melee (space, only when revolver NOT equipped) ───────────────
    if space_pressed_this_frame and not revolver_equipped and player_slash_frame is None:
        player_slash_frame = 0
        player_slash_time  = pygame.time.get_ticks()
        player_slash_hit_this_swing = set()

    # ── Shoot (space when revolver equipped — one shot per press) ────
    if space_pressed_this_frame and revolver_equipped and bullets > 0:
        mx, my = pygame.mouse.get_pos()
        cam_x_now = world_x - cols / 2
        cam_y_now = world_y - rows / 2
        target_wx = cam_x_now + (mx / cell_size)
        target_wy = cam_y_now + (my / cell_size)
        shot_dx = target_wx - world_x
        shot_dy = target_wy - world_y
        shot_len = math.hypot(shot_dx, shot_dy)
        if shot_len > 0:
            bdx, bdy = shot_dx / shot_len, shot_dy / shot_len
            active_bullets.append([world_x, world_y, bdx, bdy, 0.0])
            bullets -= 1
            play_sound("assets/shoot.mp3")

    # ── Movement ─────────────────────────────────────────────────────
    current_speed = speed * (speed_boost_multiplier if speed_boost_active else 1.0)

    dx, dy = 0.0, 0.0
    dir_now = None
    if keys[pygame.K_w]: dy -= current_speed / cell_size; dir_now = 'up'
    if keys[pygame.K_s]: dy += current_speed / cell_size; dir_now = 'down'
    if keys[pygame.K_a]: dx -= current_speed / cell_size; dir_now = 'left'
    if keys[pygame.K_d]: dx += current_speed / cell_size; dir_now = 'right'

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
            if coin_count >= 10:
                unlock_achievement("rookie_richie")
        if ptile in medkit_tiles:
            medkit_tiles.remove(ptile)
            health = min(max_health, health + 2)
        if ptile in bullet_tiles:
            bullet_tiles.remove(ptile)
            if revolver_unlocked:
                bullets = REVOLVER_MAX_BULLETS
                play_sound("assets/coin-collect.mp3")
        if ptile in lightning_tiles:
            if coin_count >= LIGHTNING_COST:
                lightning_tiles.remove(ptile)
                coin_count -= LIGHTNING_COST
                speed_boost_active = True
                speed_boost_end_time = pygame.time.get_ticks() + SPEED_BOOST_DURATION
                play_sound("assets/coin-collect.mp3")
                buy_prompt_text = "SPEED BOOST!"
                buy_prompt_until = pygame.time.get_ticks() + 1500
                unlock_achievement("flash_guess")
            else:
                buy_prompt_text = f"Need {LIGHTNING_COST} coins!"
                buy_prompt_until = pygame.time.get_ticks() + 1000

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

    # ── NEW: Enemy Spawner Logic ─────────────────────────────────────
    current_time = pygame.time.get_ticks()
    for spawner_pos in list(spawner_tiles):
        last_spawn = enemy_spawn_timers.get(spawner_pos, 0)
        if current_time - last_spawn > ENEMY_SPAWN_INTERVAL:
            # Count current enemies from this spawner
            current_count = count_enemies_from_spawner(spawner_pos)
            if current_count < MAX_ENEMIES_PER_SPAWNER:
                # Spawn new enemy
                spawn_col, spawn_row = spawner_pos[1], spawner_pos[0]
                # Spawn nearby but not on top of spawner
                offset_x = random.choice([-1, 1]) * random.uniform(1, 2)
                offset_y = random.choice([-1, 1]) * random.uniform(1, 2)
                enemy_positions.append([spawn_col + offset_x, spawn_row + offset_y])
                enemy_health.append(1)
                enemy_slash_frames.append(None)
                enemy_slash_times.append(0)
                enemy_source_spawner[len(enemy_positions) - 1] = spawner_pos
                enemy_spawn_timers[spawner_pos] = current_time

    # ── Move bullets ─────────────────────────────────────────────────
    dead_enemies = set()
    dead_bullets = []
    for bi, b in enumerate(active_bullets):
        b[0] += b[2] * BULLET_SPEED
        b[1] += b[3] * BULLET_SPEED
        b[4] += BULLET_SPEED
        if b[4] > BULLET_RANGE or map_grid.get((int(b[1]), int(b[0])), 'air') == 'rock':
            dead_bullets.append(bi)
            continue
        for i in range(len(enemy_positions)):
            ex, ey = enemy_positions[i]
            if math.hypot(b[0]-ex, b[1]-ey) < BULLET_RADIUS:
                enemy_health[i] -= 1
                if enemy_health[i] <= 0:
                    dead_enemies.add(i)
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
            if (row, col) in bullet_tiles:
                screen.blit(bullet_img, (ipx, ipy))
            if (row, col) in lightning_tiles:
                screen.blit(lightning_img, (ipx, ipy))
                cost_text = f"{LIGHTNING_COST}"
                draw_text(screen, cost_text, 14, ipx + cell_size//2, ipy - 8, (255, 255, 0))
            # NEW: Draw spawners
            if (row, col) in spawner_tiles:
                screen.blit(spawner_img, (ipx, ipy))
                # Optional: show spawn indicator
                pulse = int(100 + 100 * math.sin(glow_t * 3))
                pygame.draw.circle(screen, (255, 0, 0, pulse), (ipx + cell_size//2, ipy + cell_size//2), 5)

    # ── Draw bullets ──────────────────────────────────────────────────
    for b in active_bullets:
        bsx, bsy = world_to_screen(b[0], b[1], cam_x, cam_y)
        pygame.draw.circle(screen, (255, 240, 100), (int(bsx), int(bsy)), BULLET_SIZE_PX)
        pygame.draw.circle(screen, (200, 150,  20), (int(bsx), int(bsy)), BULLET_SIZE_PX - 2)

    # ── Enemy AI + damage ─────────────────────────────────────────────
    for i in range(len(enemy_positions)):
        if i in dead_enemies:
            continue
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
                # Ensure slash arrays are long enough
                while len(enemy_slash_frames) <= i:
                    enemy_slash_frames.append(None)
                    enemy_slash_times.append(0)
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
            enemy_health[i] -= 1
            if enemy_health[i] <= 0:
                dead_enemies.add(i)
            play_sound("assets/hurt.mp3")

    # Remove dead enemies and reset spawner cooldown so replacements do not appear instantly
    for i in sorted(dead_enemies, reverse=True):
        source = enemy_source_spawner.get(i)
        remove_enemy(i)
        if source in enemy_spawn_timers:
            enemy_spawn_timers[source] = max(enemy_spawn_timers[source], current_time)

    # ── Draw enemies ──────────────────────────────────────────────────
    for i in range(len(enemy_positions)):
        ex, ey = enemy_positions[i]
        esx, esy = world_to_screen(ex, ey, cam_x, cam_y)
        screen.blit(enemy_img, (int(esx), int(esy)))
        # Ensure slash arrays are long enough
        while len(enemy_slash_frames) <= i:
            enemy_slash_frames.append(None)
            enemy_slash_times.append(0)
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

    # NEW: Speed boost HUD
    draw_speed_hud(screen, width, height, glow_t)

    # ── Buy prompt flash ──────────────────────────────────────────────
    if pygame.time.get_ticks() < buy_prompt_until:
        draw_text(screen, buy_prompt_text, 28, width//2, height//2 - 60, (255, 215, 0))

    # ── Achievement popup ─────────────────────────────────────────────
    draw_achievement_popup(screen, width)

    # ── Game Over Effect ─────────────────────────────────────────────
    if health <= 0:
        fade = pygame.Surface((width, height), pygame.SRCALPHA)
        fade.fill((80, 80, 80, 200))
        screen.blit(fade, (0, 0))
        surf = pygame.transform.smoothscale(screen, (width//2, height//2))
        surf = pygame.transform.smoothscale(surf, (width, height))
        screen.blit(surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        draw_text(screen, "WASTED", 96, width//2, height//2, (220, 0, 40))
        pygame.display.flip()
        pygame.time.wait(2200)
        running = False
    else:
        pygame.display.flip()
        dt = clock.tick(60) / 1000.0

pygame.quit()
