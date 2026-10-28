# ui/effects.py — Hiệu ứng hình ảnh nền vũ trụ, Tinh vân, Sao băng, Hạt va đập (Impact Sparks)
import math
import random
try:
    import pyray as rl
except ImportError:
    from raylib import pyray as rl

from config import BLOCK_SKINS, get_skin_spark_rgb
from app_state import ctx
from ui.widgets import draw_star_circle

# ── Khởi tạo Bộ đệm Sao 3D (3D Starfield) ──
STARS = []
for i in range(140):
    yaw = (i * 137.5) * (math.pi / 180.0)
    pitch = ((i % 50) - 25) * (math.pi / 50.0)
    dist = 36.0 + (i % 20) * 1.6
    sx = dist * math.cos(pitch) * math.sin(yaw)
    sy = dist * math.sin(pitch)
    sz = dist * math.cos(pitch) * math.cos(yaw)
    ssz = 0.14 + (i % 4) * 0.07
    spd = 1.2 + (i % 5) * 0.5
    phase = (i * 0.73) % (2.0 * math.pi)
    if i % 4 == 0:
        base_col = (175, 235, 255)  # Cyan tinh vân
    elif i % 4 == 1:
        base_col = (255, 225, 150)  # Vàng ánh kim
    elif i % 4 == 2:
        base_col = (225, 200, 255)  # Tím tử quang
    else:
        base_col = (255, 255, 255)  # Trắng tinh khiết
    STARS.append((sx, sy, sz, ssz, spd, phase, base_col))

STAR_CACHE = []

# 24 Hạt bụi sao vũ trụ 3D bồng bềnh không trọng lực
STARDUST_3D = []
_rnd3 = random.Random(1337)
for i in range(24):
    ox = _rnd3.uniform(-4.5, 14.5)
    oy = _rnd3.uniform(-1.5, 3.2)
    oz = _rnd3.uniform(-4.5, 14.5)
    spd = _rnd3.uniform(0.6, 1.5)
    phase = _rnd3.uniform(0.0, 2.0 * math.pi)
    col_type = i % 2
    STARDUST_3D.append((ox, oy, oz, spd, phase, col_type))

STARDUST_CACHE = []
cached_center = (-999.0, -999.0)

def update_star_cache_if_needed():
    """Tái sử dụng bộ đệm Vector3 của ngôi sao, triệt tiêu rác bộ nhớ (GC)"""
    global cached_center, STAR_CACHE, STARDUST_CACHE
    center_c = (ctx.game.cols - 1) / 2.0
    center_r = (ctx.game.rows - 1) / 2.0
    if cached_center != (center_c, center_r) or not STAR_CACHE:
        cached_center = (center_c, center_r)
        STAR_CACHE = []
        for sx, sy, sz, ssz, spd, phase, base_col in STARS:
            star_vec = rl.Vector3(center_c + sx, sy, center_r + sz)
            STAR_CACHE.append((star_vec, ssz, spd, phase, base_col))
        STARDUST_CACHE = []
        for ox, oy, oz, spd, phase, col_type in STARDUST_3D:
            dust_vec = rl.Vector3(center_c + ox, oy, center_r + oz)
            STARDUST_CACHE.append((dust_vec, ox, oy, oz, spd, phase, col_type))


def draw_starfield():
    """Vẽ bầu trời sao vũ trụ 3D lấp lánh và bụi sao lơ lửng"""
    update_star_cache_if_needed()

    for star_pos, ssz, spd, phase, base_col in STAR_CACHE:
        twinkle = 0.5 + 0.5 * math.sin(ctx.spin_timer * spd + phase)
        alpha = int(110 + 145 * twinkle)
        col = rl.Color(base_col[0], base_col[1], base_col[2], alpha)
        rl.draw_cube(star_pos, ssz, ssz, ssz, col)

    center_c = cached_center[0]
    center_r = cached_center[1]
    for dust_vec, ox, oy, oz, spd, phase, col_type in STARDUST_CACHE:
        bob_y = oy + math.sin(ctx.spin_timer * spd + phase) * 0.28
        dust_vec.x = center_c + ox
        dust_vec.y = bob_y
        dust_vec.z = center_r + oz
        sparkle = 0.5 + 0.5 * math.sin(ctx.spin_timer * spd * 1.6 + phase)
        alpha = int(75 + 140 * sparkle)
        col = rl.Color(165, 240, 255, alpha) if col_type == 0 else rl.Color(255, 220, 140, alpha)
        rl.draw_cube(dust_vec, 0.08, 0.08, 0.08, col)


# ── Hệ thống Hạt va đập (Impact Spark & Dust Particles) ──
particles = []

def spawn_impact_sparks(x, z, count=16, is_gold=True):
    """Phát ra chùm tia lửa & bụi năng lượng khi khối đập xuống sàn, tự động lấy màu spark_col của Skin hiện tại"""
    base_spark_col = get_skin_spark_rgb(ctx.current_skin_idx, ctx.spin_timer)
    for _ in range(count):
        ang = random.uniform(0.0, 2.0 * math.pi)
        spd = random.uniform(1.2, 3.2)
        vx = math.cos(ang) * spd
        vz = math.sin(ang) * spd
        vy = random.uniform(1.2, 3.2)
        life = random.uniform(0.28, 0.52)
        particles.append({
            "x": x, "y": 0.05, "z": z,
            "vx": vx, "vy": vy, "vz": vz,
            "life": life, "max_life": life,
            "sz": random.uniform(0.08, 0.14),
            "col": base_spark_col
        })


def update_and_draw_particles(dt):
    """Cập nhật vật lý và vẽ các hạt phát sáng trong không gian 3D"""
    alive = []
    for p in particles:
        p["life"] -= dt
        if p["life"] <= 0:
            continue
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt
        p["z"] += p["vz"] * dt
        p["vy"] -= 9.8 * dt
        ratio = p["life"] / p["max_life"]
        alpha = int(255 * ratio)
        col = rl.Color(p["col"][0], p["col"][1], p["col"][2], alpha)
        sz = p["sz"] * (0.4 + 0.6 * ratio)
        rl.draw_cube(rl.Vector3(p["x"], max(0.02, p["y"]), p["z"]), sz, sz, sz, col)
        alive.append(p)
    particles[:] = alive


# ── Bầu trời Không gian Vũ trụ Sâu thẳm 2D ──
COSMIC_STARS_2D = []
_rnd = random.Random(42)
for i in range(180):
    nx = _rnd.random()
    ny = _rnd.random()
    sz_rnd = _rnd.random()
    if sz_rnd < 0.72:
        sz = 1
    elif sz_rnd < 0.92:
        sz = 2
    else:
        sz = 3
    spd = _rnd.uniform(1.2, 3.8)
    phase = _rnd.uniform(0.0, 2.0 * math.pi)
    col_t = i % 4
    if col_t == 0:
        base_rgb = (255, 255, 255)  # Trắng kim cương
    elif col_t == 1:
        base_rgb = (175, 235, 255)  # Xanh băng tinh vân
    elif col_t == 2:
        base_rgb = (255, 225, 150)  # Vàng ánh sao xa
    else:
        base_rgb = (220, 195, 255)  # Tím tử quang
    has_flare = (sz == 3 and i % 2 == 0)
    COSMIC_STARS_2D.append((nx, ny, sz, spd, phase, base_rgb, has_flare))

shooting_star = {
    "active": False,
    "timer": 1.8,
    "x": 0.0, "y": 0.0,
    "vx": 0.0, "vy": 0.0,
    "len": 0.0,
    "life": 0.0,
    "max_life": 0.0
}


def draw_nebula_cloud(cx, cy, radius, col1, col2):
    """Vẽ đám mây tinh vân phát quang mềm mại tương thích với cả PyRay Vector2 và C API"""
    if hasattr(rl, "draw_circle_gradient"):
        try:
            rl.draw_circle_gradient(rl.Vector2(float(cx), float(cy)), float(radius), col1, col2)
        except TypeError:
            try:
                rl.draw_circle_gradient(int(cx), int(cy), float(radius), col1, col2)
            except Exception:
                pass
        except Exception:
            pass


def draw_cosmic_space_backdrop(w, h, dt):
    """Vẽ phông nền vũ trụ đa tầng với dải thiên hà, tinh vân phát quang, sao 2D lấp lánh và sao băng"""
    global shooting_star

    # 1. Gradient bầu trời không gian sâu thẳm
    if hasattr(rl, "draw_rectangle_gradient_v"):
        rl.draw_rectangle_gradient_v(0, 0, w, h, rl.Color(3, 5, 14, 255), rl.Color(8, 14, 28, 255))
    else:
        rl.draw_rectangle(0, 0, w, h, rl.Color(4, 7, 18, 255))

    # 2. Các cụm mây Tinh vân Vũ trụ (Nebula Glow Clouds)
    r1 = float(w * 0.44 + math.sin(ctx.spin_timer * 0.25) * 16.0)
    draw_nebula_cloud(w * 0.82, h * 0.24, r1, rl.Color(82, 26, 128, 75), rl.Color(6, 4, 16, 0))

    r2 = float(w * 0.40 + math.cos(ctx.spin_timer * 0.20) * 14.0)
    draw_nebula_cloud(w * 0.16, h * 0.78, r2, rl.Color(16, 75, 108, 65), rl.Color(4, 10, 20, 0))

    r3 = float(w * 0.36 + math.sin(ctx.spin_timer * 0.16 + 1.0) * 10.0)
    draw_nebula_cloud(w * 0.52, h * 0.46, r3, rl.Color(44, 22, 78, 48), rl.Color(5, 6, 16, 0))

    # 3. Dải sao vũ trụ 2D đa sắc
    for nx, ny, sz, spd, phase, base_rgb, has_flare in COSMIC_STARS_2D:
        sx = int(nx * w)
        sy = int(ny * h)
        twinkle = 0.42 + 0.58 * math.sin(ctx.spin_timer * spd + phase)
        alpha = int(90 + 165 * twinkle)
        col = rl.Color(base_rgb[0], base_rgb[1], base_rgb[2], alpha)

        if sz == 1:
            rl.draw_pixel(sx, sy, col)
        elif sz == 2:
            rl.draw_rectangle(sx, sy, 2, 2, col)
        else:
            rl.draw_rectangle(sx - 1, sy - 1, 3, 3, col)
            if has_flare:
                flare_a = int(alpha * 0.60)
                f_col = rl.Color(base_rgb[0], base_rgb[1], base_rgb[2], flare_a)
                rl.draw_pixel(sx - 2, sy, f_col)
                rl.draw_pixel(sx + 2, sy, f_col)
                rl.draw_pixel(sx, sy - 2, f_col)
                rl.draw_pixel(sx, sy + 2, f_col)
                halo_a = int(alpha * 0.14)
                draw_star_circle(sx, sy, 5.0, rl.Color(base_rgb[0], base_rgb[1], base_rgb[2], halo_a))

    # 4. Sao Băng lướt qua bầu trời (Cosmic Shooting Star)
    if not shooting_star["active"]:
        shooting_star["timer"] -= dt
        if shooting_star["timer"] <= 0:
            shooting_star["active"] = True
            shooting_star["x"] = random.uniform(w * 0.30, w * 0.95)
            shooting_star["y"] = random.uniform(-10.0, h * 0.35)
            spd = random.uniform(620.0, 900.0)
            ang = math.radians(random.uniform(132.0, 152.0))
            shooting_star["vx"] = math.cos(ang) * spd
            shooting_star["vy"] = math.sin(ang) * spd
            shooting_star["len"] = random.uniform(55.0, 95.0)
            life = random.uniform(0.40, 0.65)
            shooting_star["life"] = life
            shooting_star["max_life"] = life
    else:
        shooting_star["life"] -= dt
        shooting_star["x"] += shooting_star["vx"] * dt
        shooting_star["y"] += shooting_star["vy"] * dt
        prog = shooting_star["life"] / shooting_star["max_life"]
        if prog <= 0:
            shooting_star["active"] = False
            shooting_star["timer"] = random.uniform(4.5, 8.0)
        else:
            alpha = int(255 * math.sin(prog * math.pi))
            spd_val = math.hypot(shooting_star["vx"], shooting_star["vy"])
            if spd_val > 0:
                dx = (shooting_star["vx"] / spd_val) * shooting_star["len"]
                dy = (shooting_star["vy"] / spd_val) * shooting_star["len"]
                s_pos = rl.Vector2(float(shooting_star["x"] - dx), float(shooting_star["y"] - dy))
                h_pos = rl.Vector2(float(shooting_star["x"]), float(shooting_star["y"]))
                m_col = rl.Color(255, 255, 255, alpha)
                try:
                    if hasattr(rl, "draw_line_ex"):
                        rl.draw_line_ex(s_pos, h_pos, 2.2, m_col)
                    else:
                        rl.draw_line(int(s_pos.x), int(s_pos.y), int(h_pos.x), int(h_pos.y), m_col)
                except Exception:
                    pass
                draw_star_circle(h_pos.x, h_pos.y, 2.2, m_col)
