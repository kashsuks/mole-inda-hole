import pygame
import random
import math
import time
import json
import asyncio
import sys

async def main():
    def fade(t): return t * t * t * (t * (t * 6 - 15) + 10)
    def lerp(a, b, t): return a + t * (b - a)
    def grad(h, x, y):
        h &= 3
        if h == 0: return  x + y
        if h == 1: return -x + y
        if h == 2: return  x - y
        return -x - y
    
    _perm = list(range(256))
    random.shuffle(_perm)
    _perm *= 2

    def pnoise2(x, y):
        xi, yi = int(math.floor(x)) & 255, int(math.floor(y)) & 255
        xf, yf = x - math.floor(x), y - math.floor(y)
        u, v = fade(xf), fade(yf)
        a  = _perm[xi]   + yi;  aa = _perm[a];  ab = _perm[a+1]
        b  = _perm[xi+1] + yi;  ba = _perm[b];  bb = _perm[b+1]
        return lerp(lerp(grad(_perm[aa], xf,   yf),   grad(_perm[ba], xf-1, yf),   u),
                    lerp(grad(_perm[ab], xf,   yf-1), grad(_perm[bb], xf-1, yf-1), u), v)
    def draw_text(surface, text, size, x, y, color=(255,255,255)):
        font = pygame.font.Font("assets/Ithaca-LVB75.ttf", size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)

    pygame.init()
    pygame.mixer.init()

    width, height = 800, 600
    cell_size = 40
    if sys.platform == "emscripten":
        screen = pygame.display.set_mode((800, 600))  # fixed size
    else:
        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
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

    # ── Status / screen state ───────────────────────────────────────────
    status = "start"  # "start" | "settings" | "game" | "dead" | "win"

    # ── Start screen button rects (set properly once we know width/height) ──
    play_rect     = pygame.Rect(width//2-100, height//2-40, 200, 50)
    settings_rect = pygame.Rect(width//2-100, height//2+30, 200, 50)

    # ── Settings screen state ───────────────────────────────────────────
    slider_rect_music = pygame.Rect(width//2-150, height//2-60, 300, 20)
    slider_rect_sfx   = pygame.Rect(width//2-150, height//2+20, 300, 20)
    knob_radius = 12
    music_knob_x = int(slider_rect_music.x + music_volume * slider_rect_music.width)
    sfx_knob_x   = int(slider_rect_sfx.x   + sfx_volume   * slider_rect_sfx.width)
    dragging_music = False
    dragging_sfx   = False
    back_rect = pygame.Rect(width//2-60, height//2+80, 120, 40)
    settings_origin = "start"  # where to return after settings: "start" or "game"

    def play_sound(path):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(sfx_volume)
        sound.play()

    # Load images
    fossil_img    = pygame.transform.scale(pygame.image.load("assets/fossil1.png"), (cell_size, cell_size))
    rock_img      = pygame.transform.scale(pygame.image.load("assets/rock1.png"),   (cell_size, cell_size))
    medkit_img    = pygame.transform.scale(pygame.image.load("assets/medkit.png"),  (cell_size, cell_size))
    bullet_img    = pygame.transform.scale(pygame.image.load("assets/bullet.png"),  (cell_size, cell_size))
    lightning_img = pygame.transform.scale(pygame.image.load("assets/lightning.png"), (cell_size, cell_size))
    spawner_img   = pygame.transform.scale(pygame.image.load("assets/spawner.png").convert_alpha(), (cell_size, cell_size))

    mole_img_orig = pygame.transform.scale(pygame.image.load("assets/mole.png"), (square_size, square_size))
    mole_img = mole_img_orig
    dirt_imgs = [pygame.transform.scale(pygame.image.load(f"assets/dirt{i}.png"), (cell_size, cell_size)) for i in range(1,4)]

    heart_size = 40
    w_heart_img     = pygame.transform.scale(pygame.image.load("assets/heart-full.png"),  (heart_size, heart_size))
    half_heart_img  = pygame.transform.scale(pygame.image.load("assets/heart-half.png"),  (heart_size, heart_size))
    empty_heart_img = pygame.transform.scale(pygame.image.load("assets/heart-empty.png"), (heart_size, heart_size))

    key_size = 48
    w_key_img = pygame.transform.scale(pygame.image.load("assets/w_key.png"), (key_size, key_size))
    a_key_img = pygame.transform.scale(pygame.image.load("assets/a_key.png"), (key_size, key_size))
    s_key_img = pygame.transform.scale(pygame.image.load("assets/s_key.png"), (key_size, key_size))
    d_key_img = pygame.transform.scale(pygame.image.load("assets/d_key.png"), (key_size, key_size))

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
    active_bullets = []

    glow_t = 0.0
    buy_prompt_text = ""
    buy_prompt_until = 0

    KONAMI_CODE   = ["up", "up", "down", "down", "left", "right", "left", "right", "b", "a"]
    konami_buffer = []

    trail        = []
    trail_length = 20
    air_color    = (30, 30, 30)
    fossil_chance = 0.07
    rock_chance   = 0.10
    seed = random.randint(0, 10000)

    map_grid       = {}
    coin_tiles     = set()
    medkit_tiles   = set()
    bullet_tiles   = set()
    lightning_tiles = set()
    spawner_tiles  = set()
    coin_spawn_chance = 0.03

    SPAWNER_SPAWN_CHANCE             = 0.008
    SPAWNER_MIN_DISTANCE_FROM_PLAYER = 8
    ENEMY_SPAWN_INTERVAL             = 3000
    MAX_ENEMIES_PER_SPAWNER          = 3

    BOSS_REQUIRED_COINS  = 100
    BOSS_REQUIRED_KILLS  = 30
    BOSS_MAX_HEALTH      = 80
    BOSS_MOVE_SPEED      = 1.4 / cell_size
    BOSS_ATTACK_REACH    = 1.9
    BOSS_HIT_RADIUS      = 1.5
    BOSS_SLASH_REACH     = 2.2
    BOSS_MELEE_DAMAGE    = 2
    BOSS_RANGED_DAMAGE   = 2
    BOSS_INTRO_RUMBLE1_MS   = 1700
    BOSS_INTRO_DIALOGUE_MS  = 1800
    BOSS_INTRO_RUMBLE2_MS   = 1700

    LIGHTNING_COST       = 10
    BASE_SPEED           = 5
    speed_boost_active   = False
    speed_boost_multiplier = 2.0
    speed_boost_end_time = 0
    SPEED_BOOST_DURATION = 5000

    enemy_img   = pygame.transform.scale(mole_img_orig, (square_size, square_size))
    boss_size   = int(square_size * 3.2)
    boss_img    = pygame.transform.scale(mole_img_orig, (boss_size, boss_size))
    enemy_speed = 2.5 / cell_size
    enemy_positions    = []
    enemy_spawn_timers = {}
    enemy_health       = []
    boss_spawned       = False
    boss_defeated      = False
    boss_x, boss_y     = 0.0, 0.0
    boss_health        = BOSS_MAX_HEALTH
    boss_attack_cooldown = 0
    boss_intro_active  = False
    boss_intro_phase   = 0
    boss_intro_phase_start = 0

    enemy_source_spawner = {}

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
    boss_hit_this_swing = False
    enemy_slash_frames = []
    enemy_slash_times  = []

    PLAYER_SLASH_REACH = 1.5
    ENEMY_ATTACK_REACH = 1.2

    # ── End-state timing ────────────────────────────────────────────────
    end_state_start = 0   # ticks when we entered "dead" or "win"
    END_STATE_WAIT  = 2600  # ms to show the screen before quitting

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
                pygame.draw.rect(surface, (70,70,70),   (ix, iy+REVOLVER_ICON_SIZE+4, bar_w, 6))
                pygame.draw.rect(surface, (180,140,40), (ix, iy+REVOLVER_ICON_SIZE+4, int(bar_w*progress), 6))
                draw_text(surface, f"{coin_count}/{REVOLVER_COST}", 17,
                        ix + REVOLVER_ICON_SIZE//2, iy+REVOLVER_ICON_SIZE+18, (150,150,150))
        else:
            if equipped:
                pygame.draw.rect(surface, (255,100,50), (ix-3, iy-3, REVOLVER_ICON_SIZE+6, REVOLVER_ICON_SIZE+6), 3)
            surface.blit(revolver_icon, (ix, iy))
            pip_r   = 5
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

    def draw_boss_health_bar(surface, w, hp, hp_max):
        bar_w = min(560, w - 80)
        bar_h = 26
        x = (w - bar_w) // 2
        y = 14
        pygame.draw.rect(surface, (35, 35, 35), (x, y, bar_w, bar_h))
        fill_w = int(bar_w * max(0.0, min(1.0, hp / hp_max)))
        pygame.draw.rect(surface, (190, 35, 35), (x, y, fill_w, bar_h))
        pygame.draw.rect(surface, (240, 240, 240), (x, y, bar_w, bar_h), 2)
        draw_text(surface, "SUPER MEGA MOLE", 20, w // 2, y + bar_h // 2, (255, 255, 255))

    def draw_dialogue_box(surface, w, h, text):
        box_w = min(640, w - 80)
        box_h = 110
        x = (w - box_w) // 2
        y = h - box_h - 30
        pygame.draw.rect(surface, (22, 22, 22), (x, y, box_w, box_h))
        pygame.draw.rect(surface, (232, 232, 232), (x, y, box_w, box_h), 4)
        pygame.draw.rect(surface, (80, 80, 80), (x + 8, y + 8, box_w - 16, box_h - 16), 2)
        draw_text(surface, text, 36, x + box_w // 2, y + box_h // 2, (255, 255, 255))

    def count_enemies_from_spawner(spawner_pos):
        count = 0
        for idx, source in enemy_source_spawner.items():
            if source == spawner_pos and idx < len(enemy_positions):
                count += 1
        return count

    def remove_enemy(idx):
        if idx < len(enemy_positions):
            enemy_positions.pop(idx)
            if idx < len(enemy_health):
                enemy_health.pop(idx)
            if idx < len(enemy_slash_frames):
                enemy_slash_frames.pop(idx)
            if idx < len(enemy_slash_times):
                enemy_slash_times.pop(idx)
            new_source = {}
            for old_idx, source in enemy_source_spawner.items():
                if old_idx < idx:
                    new_source[old_idx] = source
                elif old_idx > idx:
                    new_source[old_idx - 1] = source
            enemy_source_spawner.clear()
            enemy_source_spawner.update(new_source)

    # ── Load start-screen music immediately ─────────────────────────────
    pygame.mixer.music.load("assets/loading.ogg")
    pygame.mixer.music.play(-1)

    coin_count = 0
    coins_earned_total = 0
    kill_count = 0
    last_dir   = 'down'
    dt = 1/60

    # ── Helper: rebuild layout rects when window size changes ───────────
    def rebuild_ui_rects(play_rect, settings_rect, slider_rect_music, slider_rect_sfx, music_knob_x, sfx_knob_x, back_rect):
        play_rect         = pygame.Rect(width//2-100, height//2-40,  200, 50)
        settings_rect     = pygame.Rect(width//2-100, height//2+30,  200, 50)
        slider_rect_music = pygame.Rect(width//2-150, height//2-60,  300, 20)
        slider_rect_sfx   = pygame.Rect(width//2-150, height//2+20,  300, 20)
        music_knob_x      = int(slider_rect_music.x + music_volume * slider_rect_music.width)
        sfx_knob_x        = int(slider_rect_sfx.x   + sfx_volume   * slider_rect_sfx.width)
        back_rect         = pygame.Rect(width//2-60,  height//2+80,  120, 40)

    # ════════════════════════════════════════════════════════════════════
    # MAIN LOOP
    # ════════════════════════════════════════════════════════════════════
    while running:
        current_time = pygame.time.get_ticks()

        # ── Shared event pre-pass (QUIT + VIDEORESIZE always handled) ────
        space_pressed_this_frame = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                if sys.platform == "emscripten":
                    screen = pygame.display.set_mode((800, 600))  # fixed size
                else:
                    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                cols = width // cell_size
                rows = height // cell_size
                rebuild_ui_rects(play_rect, settings_rect, slider_rect_music, slider_rect_sfx, music_knob_x, sfx_knob_x, back_rect)

        # ════════════════════════════════════════════════════════════════
        # STATUS: start
        # ════════════════════════════════════════════════════════════════
        if status == "start":
            screen.fill((30, 30, 30))
            draw_text(screen, "Mole in da hole", 60, width//2, height//2-120)
            pygame.draw.rect(screen, (70, 130, 180), play_rect)
            draw_text(screen, "Play",     40, width//2, height//2-15)
            pygame.draw.rect(screen, (120, 120, 120), settings_rect)
            draw_text(screen, "Settings", 40, width//2, height//2+55)

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if play_rect.collidepoint(mx, my):
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("assets/main.ogg")
                        pygame.mixer.music.play(-1)
                        status = "game"
                    elif settings_rect.collidepoint(mx, my):
                        settings_origin = "start"
                        status = "settings"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        if sys.platform != "emscripten":
                            pygame.display.toggle_fullscreen()

        # ════════════════════════════════════════════════════════════════
        # STATUS: settings
        # ════════════════════════════════════════════════════════════════
        elif status == "settings":
            screen.fill((30, 30, 30))
            draw_text(screen, "Settings",     48, width//2, height//2-120)
            draw_text(screen, "Music Volume", 32, width//2, height//2-80)
            draw_text(screen, "SFX Volume",   32, width//2, height//2)
            pygame.draw.rect(screen, (120,120,120), slider_rect_music)
            pygame.draw.rect(screen, (120,120,120), slider_rect_sfx)
            pygame.draw.circle(screen, (70,130,180), (music_knob_x, slider_rect_music.y+10), knob_radius)
            pygame.draw.circle(screen, (70,130,180), (sfx_knob_x,   slider_rect_sfx.y+10),   knob_radius)
            pygame.draw.rect(screen, (70,130,180), back_rect)
            draw_text(screen, "Back", 32, back_rect.centerx, back_rect.centery)

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if (music_knob_x-knob_radius <= mx <= music_knob_x+knob_radius and
                            slider_rect_music.y <= my <= slider_rect_music.y+20):
                        dragging_music = True
                    if (sfx_knob_x-knob_radius <= mx <= sfx_knob_x+knob_radius and
                            slider_rect_sfx.y <= my <= slider_rect_sfx.y+20):
                        dragging_sfx = True
                    if back_rect.collidepoint(mx, my):
                        status = settings_origin
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging_music = False
                    dragging_sfx   = False
                elif event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    if dragging_music:
                        music_knob_x = max(slider_rect_music.x,
                                        min(mx, slider_rect_music.x + slider_rect_music.width))
                        music_volume = (music_knob_x - slider_rect_music.x) / slider_rect_music.width
                    if dragging_sfx:
                        sfx_knob_x = max(slider_rect_sfx.x,
                                        min(mx, slider_rect_sfx.x + slider_rect_sfx.width))
                        sfx_volume = (sfx_knob_x - slider_rect_sfx.x) / slider_rect_sfx.width
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        status = settings_origin
                    elif event.key == pygame.K_f:
                        if sys.platform != "emscripten":
                            pygame.display.toggle_fullscreen()

        # ════════════════════════════════════════════════════════════════
        # STATUS: game
        # ════════════════════════════════════════════════════════════════
        elif status == "game":
            glow_t += dt

            # ── Game-specific events ─────────────────────────────────────
            for event in events:
                if event.type == pygame.KEYDOWN:
                    konami_map = {
                        pygame.K_UP: "up", pygame.K_DOWN: "down",
                        pygame.K_LEFT: "left", pygame.K_RIGHT: "right",
                        pygame.K_b: "b", pygame.K_a: "a",
                    }
                    konami_input = konami_map.get(event.key)
                    if konami_input:
                        konami_buffer.append(konami_input)
                        if len(konami_buffer) > len(KONAMI_CODE):
                            konami_buffer.pop(0)
                        if konami_buffer == KONAMI_CODE:
                            coin_count += 1000
                            coins_earned_total += 1000
                            kill_count = max(kill_count, BOSS_REQUIRED_KILLS)
                            coins_earned_total = max(coins_earned_total, BOSS_REQUIRED_COINS)
                            buy_prompt_text  = "KONAMI! +1000 coins, boss unlocked"
                            buy_prompt_until = current_time + 1800
                            konami_buffer.clear()
                    if event.key == pygame.K_f:
                        if sys.platform != "emscripten":
                            pygame.display.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        settings_origin = "game"
                        status = "settings"
                    elif event.key == pygame.K_e:
                        if not revolver_unlocked and coin_count >= REVOLVER_COST:
                            revolver_unlocked = True
                            revolver_equipped = True
                            coin_count  -= REVOLVER_COST
                            bullets      = REVOLVER_MAX_BULLETS
                            buy_prompt_text  = "Revolver unlocked!"
                            buy_prompt_until = current_time + 2200
                        elif not revolver_unlocked:
                            buy_prompt_text  = f"Need {REVOLVER_COST} coins to buy!"
                            buy_prompt_until = current_time + 1200
                    elif event.key == pygame.K_1:
                        if revolver_unlocked:
                            revolver_equipped = not revolver_equipped
                    elif event.key == pygame.K_SPACE:
                        space_pressed_this_frame = True

            keys = pygame.key.get_pressed()

            # ── Check speed boost expiration ─────────────────────────────
            if speed_boost_active and current_time > speed_boost_end_time:
                speed_boost_active = False

            # ── Melee ────────────────────────────────────────────────────
            if space_pressed_this_frame and not revolver_equipped and player_slash_frame is None:
                player_slash_frame = 0
                player_slash_time  = current_time
                player_slash_hit_this_swing = set()
                boss_hit_this_swing = False

            # ── Shoot ────────────────────────────────────────────────────
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

            # ── Movement ─────────────────────────────────────────────────
            current_speed = speed * (speed_boost_multiplier if speed_boost_active else 1.0)
            dx, dy  = 0.0, 0.0
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
                    play_sound("assets/coin-collect.ogg")
                    coin_count += 1
                    coins_earned_total += 1
                if ptile in medkit_tiles:
                    medkit_tiles.remove(ptile)
                    health = min(max_health, health + 2)
                if ptile in bullet_tiles:
                    bullet_tiles.remove(ptile)
                    if revolver_unlocked:
                        bullets = REVOLVER_MAX_BULLETS
                        play_sound("assets/eagle.ogg")
                if ptile in lightning_tiles:
                    if coin_count >= LIGHTNING_COST:
                        lightning_tiles.remove(ptile)
                        coin_count -= LIGHTNING_COST
                        speed_boost_active   = True
                        speed_boost_end_time = current_time + SPEED_BOOST_DURATION
                        play_sound("assets/coin-collect.ogg")
                        buy_prompt_text  = "SPEED BOOST!"
                        buy_prompt_until = current_time + 1500
                    else:
                        buy_prompt_text  = f"Need {LIGHTNING_COST} coins!"
                        buy_prompt_until = current_time + 1000

            cam_x = world_x - cols / 2
            cam_y = world_y - rows / 2
            if shake_time > current_time:
                cam_x += random.uniform(-shake_intensity, shake_intensity)
                cam_y += random.uniform(-shake_intensity, shake_intensity)
            if boss_intro_active and boss_intro_phase in (0, 2):
                intro_shake = 0.28 if boss_intro_phase == 0 else 0.42
                cam_x += random.uniform(-intro_shake, intro_shake)
                cam_y += random.uniform(-intro_shake, intro_shake)

            tile_left   = int(cam_x) - 1
            tile_top    = int(cam_y) - 1
            tile_right  = tile_left + cols + 3
            tile_bottom = tile_top  + rows + 3
            ensure_map_area(tile_top, tile_left, tile_bottom, tile_right)

            trail.append((world_x, world_y))
            if len(trail) > trail_length:
                trail.pop(0)

            coin_frame = int((current_time / 1000 / coin_anim_speed) % len(coin_imgs))

            # ── Boss intro / unlock ───────────────────────────────────────
            if (not boss_spawned and not boss_defeated and not boss_intro_active
                    and coins_earned_total >= BOSS_REQUIRED_COINS
                    and kill_count >= BOSS_REQUIRED_KILLS):
                boss_intro_active      = True
                boss_intro_phase       = 0
                boss_intro_phase_start = current_time

            if boss_intro_active:
                phase_elapsed = current_time - boss_intro_phase_start
                if boss_intro_phase == 0 and phase_elapsed >= BOSS_INTRO_RUMBLE1_MS:
                    boss_intro_phase       = 1
                    boss_intro_phase_start = current_time
                elif boss_intro_phase == 1 and phase_elapsed >= BOSS_INTRO_DIALOGUE_MS:
                    boss_intro_phase       = 2
                    boss_intro_phase_start = current_time
                elif boss_intro_phase == 2 and phase_elapsed >= BOSS_INTRO_RUMBLE2_MS:
                    boss_intro_active = False
                    boss_spawned      = True
                    boss_health       = BOSS_MAX_HEALTH
                    if spawner_tiles:
                        srow, scol = random.choice(tuple(spawner_tiles))
                        boss_x, boss_y = float(scol), float(srow)
                    else:
                        boss_x = world_x + random.choice([-1, 1]) * 8
                        boss_y = world_y + random.choice([-1, 1]) * 8
                    enemy_positions.clear()
                    enemy_health.clear()
                    enemy_slash_frames.clear()
                    enemy_slash_times.clear()
                    enemy_source_spawner.clear()
                    buy_prompt_text  = "The SUPER MEGA MOLE has spawned!"
                    buy_prompt_until = current_time + 2400

            # ── Spawner logic ─────────────────────────────────────────────
            if not boss_spawned and not boss_intro_active:
                for spawner_pos in list(spawner_tiles):
                    last_spawn = enemy_spawn_timers.get(spawner_pos, 0)
                    if current_time - last_spawn > ENEMY_SPAWN_INTERVAL:
                        current_count = count_enemies_from_spawner(spawner_pos)
                        if current_count < MAX_ENEMIES_PER_SPAWNER:
                            spawn_col, spawn_row = spawner_pos[1], spawner_pos[0]
                            offset_x = random.choice([-1, 1]) * random.uniform(1, 2)
                            offset_y = random.choice([-1, 1]) * random.uniform(1, 2)
                            enemy_positions.append([spawn_col + offset_x, spawn_row + offset_y])
                            enemy_health.append(1)
                            enemy_slash_frames.append(None)
                            enemy_slash_times.append(0)
                            enemy_source_spawner[len(enemy_positions) - 1] = spawner_pos
                            enemy_spawn_timers[spawner_pos] = current_time

            # ── Move bullets ──────────────────────────────────────────────
            dead_enemies = set()
            dead_bullets = []
            for bi, b in enumerate(active_bullets):
                b[0] += b[2] * BULLET_SPEED
                b[1] += b[3] * BULLET_SPEED
                b[4] += BULLET_SPEED
                if b[4] > BULLET_RANGE or map_grid.get((int(b[1]), int(b[0])), 'air') == 'rock':
                    dead_bullets.append(bi)
                    continue
                hit_enemy = False
                for i in range(len(enemy_positions)):
                    ex, ey = enemy_positions[i]
                    if math.hypot(b[0]-ex, b[1]-ey) < BULLET_RADIUS:
                        enemy_health[i] -= 1
                        if enemy_health[i] <= 0:
                            dead_enemies.add(i)
                        dead_bullets.append(bi)
                        play_sound("assets/hurt.ogg")
                        hit_enemy = True
                        break
                if hit_enemy:
                    continue
                if boss_spawned and not boss_defeated:
                    if math.hypot(b[0] - boss_x, b[1] - boss_y) < BOSS_HIT_RADIUS:
                        boss_health -= BOSS_RANGED_DAMAGE
                        dead_bullets.append(bi)
                        play_sound("assets/hurt.ogg")
            for bi in sorted(set(dead_bullets), reverse=True):
                active_bullets.pop(bi)

            # ── Draw tiles ────────────────────────────────────────────────
            for row in range(tile_top, tile_bottom):
                for col in range(tile_left, tile_right):
                    tile = map_grid[(row, col)]
                    ipx  = int((col - cam_x) * cell_size)
                    ipy  = int((row - cam_y) * cell_size)
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
                        draw_text(screen, f"{LIGHTNING_COST}", 14, ipx + cell_size//2, ipy - 8, (255, 255, 0))
                    if (row, col) in spawner_tiles:
                        screen.blit(spawner_img, (ipx, ipy))
                        pulse = int(100 + 100 * math.sin(glow_t * 3))
                        pygame.draw.circle(screen, (255, 0, 0, pulse),
                                        (ipx + cell_size//2, ipy + cell_size//2), 5)

            # ── Draw bullets ──────────────────────────────────────────────
            for b in active_bullets:
                bsx, bsy = world_to_screen(b[0], b[1], cam_x, cam_y)
                pygame.draw.circle(screen, (255, 240, 100), (int(bsx), int(bsy)), BULLET_SIZE_PX)
                pygame.draw.circle(screen, (200, 150,  20), (int(bsx), int(bsy)), BULLET_SIZE_PX - 2)

            # ── Enemy AI + damage ─────────────────────────────────────────
            for i in range(len(enemy_positions)):
                if i in dead_enemies:
                    continue
                ex, ey = enemy_positions[i]
                ddx  = world_x - ex
                ddy  = world_y - ey
                dist = math.hypot(ddx, ddy)
                if dist > 0.1:
                    move_x = enemy_speed * ddx / dist
                    move_y = enemy_speed * ddy / dist
                    nex, ney = ex + move_x, ey + move_y
                    if map_grid.get((int(ney), int(nex)), None) != 'rock':
                        enemy_positions[i][0] = nex
                        enemy_positions[i][1] = ney
                if dist < ENEMY_ATTACK_REACH and health > 0:
                    if current_time > enemy_attack_cooldown:
                        health -= 1
                        enemy_attack_cooldown = current_time + 1000
                        while len(enemy_slash_frames) <= i:
                            enemy_slash_frames.append(None)
                            enemy_slash_times.append(0)
                        enemy_slash_frames[i] = 0
                        enemy_slash_times[i]  = current_time
                        shake_time      = current_time + 200
                        shake_intensity = 0.15
                        play_sound("assets/hurt.ogg")
                if (player_slash_frame is not None
                        and player_slash_frame < 6
                        and i not in player_slash_hit_this_swing
                        and dist < PLAYER_SLASH_REACH):
                    player_slash_hit_this_swing.add(i)
                    enemy_health[i] -= 1
                    if enemy_health[i] <= 0:
                        dead_enemies.add(i)
                    play_sound("assets/hurt.ogg")

            if boss_spawned and not boss_defeated:
                bdx   = world_x - boss_x
                bdy   = world_y - boss_y
                bdist = math.hypot(bdx, bdy)
                if bdist > 0.1:
                    move_x = BOSS_MOVE_SPEED * bdx / bdist
                    move_y = BOSS_MOVE_SPEED * bdy / bdist
                    next_boss_x = boss_x + move_x
                    next_boss_y = boss_y + move_y
                    if map_grid.get((int(next_boss_y), int(next_boss_x)), None) != 'rock':
                        boss_x = next_boss_x
                        boss_y = next_boss_y
                if bdist < BOSS_ATTACK_REACH and health > 0 and current_time > boss_attack_cooldown:
                    health -= 2
                    boss_attack_cooldown = current_time + 1200
                    shake_time      = current_time + 260
                    shake_intensity = 0.22
                    play_sound("assets/hurt.ogg")
                if (player_slash_frame is not None
                        and player_slash_frame < 6
                        and not boss_hit_this_swing
                        and bdist < BOSS_SLASH_REACH):
                    boss_health     -= BOSS_MELEE_DAMAGE
                    boss_hit_this_swing = True
                    play_sound("assets/hurt.ogg")
                if boss_health <= 0:
                    boss_health   = 0
                    boss_defeated = True
                    boss_spawned  = False

            # ── Remove dead enemies ───────────────────────────────────────
            for i in sorted(dead_enemies, reverse=True):
                source = enemy_source_spawner.get(i)
                remove_enemy(i)
                kill_count        += 1
                coin_count        += 1
                coins_earned_total += 1
                if source in enemy_spawn_timers:
                    enemy_spawn_timers[source] = max(enemy_spawn_timers[source], current_time)

            # ── Draw enemies ──────────────────────────────────────────────
            for i in range(len(enemy_positions)):
                ex, ey = enemy_positions[i]
                esx, esy = world_to_screen(ex, ey, cam_x, cam_y)
                screen.blit(enemy_img, (int(esx), int(esy)))
                while len(enemy_slash_frames) <= i:
                    enemy_slash_frames.append(None)
                    enemy_slash_times.append(0)
                if enemy_slash_frames[i] is not None:
                    if current_time - enemy_slash_times[i] > 50:
                        enemy_slash_frames[i] += 1
                        enemy_slash_times[i]   = current_time
                    if enemy_slash_frames[i] < 6:
                        screen.blit(slash_frames[enemy_slash_frames[i]], (int(esx), int(esy)))
                    else:
                        enemy_slash_frames[i] = None

            if boss_spawned and not boss_defeated:
                bsx, bsy = world_to_screen(boss_x, boss_y, cam_x, cam_y)
                screen.blit(boss_img, (int(bsx - boss_size // 2), int(bsy - boss_size // 2)))

            # ── Trail ─────────────────────────────────────────────────────
            for idx, (tx, ty) in enumerate(trail):
                alpha = int(255 * (idx+1) / trail_length)
                spx, spy = world_to_screen(tx, ty, cam_x, cam_y)
                soil = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
                soil.fill((139, 69, 19, alpha))
                screen.blit(soil, (int(spx), int(spy)))

            # ── Mole ──────────────────────────────────────────────────────
            mole_sx, mole_sy = world_to_screen(world_x, world_y, cam_x, cam_y)
            screen.blit(mole_img, (int(mole_sx), int(mole_sy)))

            # ── Player slash ──────────────────────────────────────────────
            if player_slash_frame is not None:
                if current_time - player_slash_time > 50:
                    player_slash_frame += 1
                    player_slash_time   = current_time
                if player_slash_frame < 6:
                    screen.blit(slash_frames[player_slash_frame], (int(mole_sx), int(mole_sy)))
                else:
                    player_slash_frame = None

            # ── WASD hints ────────────────────────────────────────────────
            key_x = 40
            key_y = height - 120
            for key_const, img, ox, oy in [
                (pygame.K_w, w_key_img, key_size,   0),
                (pygame.K_a, a_key_img, 0,          key_size),
                (pygame.K_s, s_key_img, key_size,   key_size),
                (pygame.K_d, d_key_img, key_size*2, key_size),
            ]:
                ic = img.copy()
                ic.set_alpha(255 if keys[key_const] else 100)
                screen.blit(ic, (key_x+ox, key_y+oy))

            # ── HUD ───────────────────────────────────────────────────────
            draw_text(screen, f"Coins: {coin_count}", 32, width-100, 40,  (255,223,0))
            draw_text(screen, f"Kills: {kill_count}", 26, width-95,  76,  (235,235,235))

            if not boss_spawned and not boss_defeated and not boss_intro_active:
                obj = (f"Boss unlock: {coins_earned_total}/{BOSS_REQUIRED_COINS} coins, "
                    f"{kill_count}/{BOSS_REQUIRED_KILLS} kills")
                draw_text(screen, obj, 22, width // 2, 30, (210, 210, 210))
            if boss_spawned and not boss_defeated:
                draw_boss_health_bar(screen, width, boss_health, BOSS_MAX_HEALTH)

            h_draw = health
            for i in range(3):
                himg = w_heart_img if h_draw >= 2 else (half_heart_img if h_draw == 1 else empty_heart_img)
                screen.blit(himg, (40 + i*(heart_size+8), 40))
                h_draw -= 2

            draw_revolver_hud(screen, coin_count, revolver_unlocked, revolver_equipped,
                            bullets, width, height, glow_t)
            draw_speed_hud(screen, width, height, glow_t)

            if current_time < buy_prompt_until:
                draw_text(screen, buy_prompt_text, 28, width//2, height//2 - 60, (255, 215, 0))

            if boss_intro_active and boss_intro_phase == 1:
                draw_dialogue_box(screen, width, height, "I feel a rumble...")

            # ── Transition to end states ──────────────────────────────────
            if boss_defeated:
                status         = "win"
                end_state_start = current_time
            elif health <= 0:
                status         = "dead"
                end_state_start = current_time

        # ════════════════════════════════════════════════════════════════
        # STATUS: win
        # ════════════════════════════════════════════════════════════════
        elif status == "win":
            # Keep game world visible underneath, then overlay
            fade = pygame.Surface((width, height), pygame.SRCALPHA)
            fade.fill((40, 90, 40, 190))
            screen.blit(fade, (0, 0))
            draw_text(screen, "BOSS DOWN", 88, width//2, height//2 - 18, (255, 255, 255))
            draw_text(screen, "You beat the Super Mega Mole", 36, width//2, height//2 + 42, (255, 230, 170))
            if current_time - end_state_start >= END_STATE_WAIT:
                running = False

        # ════════════════════════════════════════════════════════════════
        # STATUS: dead
        # ════════════════════════════════════════════════════════════════
        elif status == "dead":
            fade = pygame.Surface((width, height), pygame.SRCALPHA)
            fade.fill((80, 80, 80, 200))
            screen.blit(fade, (0, 0))
            surf = pygame.transform.smoothscale(screen, (width//2, height//2))
            surf = pygame.transform.smoothscale(surf, (width, height))
            screen.blit(surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            draw_text(screen, "WASTED", 96, width//2, height//2, (220, 0, 40))
            if current_time - end_state_start >= END_STATE_WAIT:
                running = False

        pygame.display.flip()
        dt = clock.tick(60) / 1000.0
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())