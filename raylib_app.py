# raylib_app.py — Game Bloxorz 3D Hoàn Chỉnh: Đầy đủ Menu Chính, Chọn Màn 1-12, Hướng Dẫn & Điều Khiển 3D
"""
HƯỚNG DẪN CHẠY:
    python raylib_app.py

TÍNH NĂNG:
- Menu chính chuyên nghiệp với hiệu ứng 3D xoay nền mượt mà
- Bảng chọn 12 màn chơi trực quan (Click chuột vào màn bất kỳ để chơi)
- Bảng hướng dẫn luật chơi chi tiết (Sàn cam, Công tắc X, Phân thân, Cầu nối)
- Đồ họa 3D sắc nét trên chip Apple Silicon M-series (GLSL 4.10 Metal)
- Phím ESC hoặc nút [MENU] để tạm dừng và quay về Menu bất kỳ lúc nào
- Hoàn tác bước đi [Z], Chơi lại [R], Đổi khối phân thân [Space], Xoay 360° bằng Trackpad
"""

import os
import sys
import math
import random
import traceback

# Đoạn này là tạo biến cho các thuật toán A*
from solvers import AVAILABLE_SOLVERS

solver_names = list(AVAILABLE_SOLVERS.keys())
current_solver_idx = 0           # 0: A*, 1: BFS, 2: DFS,...
ai_move_queue = []               # Hàng đợi bước đi
ai_stats = None                  # Lưu thống kê: số bước, số node duyệt
show_solvers_dropdown = False    # Biến bật/tắt menu xổ xuống của SOLVERS

def crash_handler(exc_type, exc_value, exc_traceback):
    """Ghi lại lỗi crash ra file crash_log.txt để kiểm tra tức thì nếu có sự cố"""
    try:
        with open("crash_log.txt", "w", encoding="utf-8") as f:
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
    except Exception:
        pass
    print("\n" + "=" * 60)
    print("PHAT HIEN LOI CRASH:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("=" * 60 + "\n")


sys.excepthook = crash_handler

try:
    import pyray as rl
except ImportError:
    try:
        from raylib import pyray as rl
    except ImportError:
        print("\n" + "=" * 60)
        print("CHƯA CÀI ĐẶT THƯ VIỆN RAYLIB!")
        print("Vui lòng mở Terminal và gõ lệnh sau để cài đặt:")
        print("    pip install raylib")
        print("=" * 60 + "\n")
        sys.exit(1)

from game import BloxorzGame
from levels import LEVELS

# Danh sách tên 12 màn chơi tiếng Việt chuẩn có dấu
LEVEL_NAMES_VI = [
    "Khởi Đầu Kinh Điển",
    "Sàn Cam Dễ Vỡ",
    "Cầu & Công Tắc Mềm",
    "Công Tắc Nặng (Chữ X)",
    "Phân Thân & Hợp Nhất",
    "Cầu Kép Đảo Chiều",
    "Thử Thách Bậc Thầy",
    "Đảo Nổi & Hai Nhịp Cầu",
    "Phân Thân Cách Trở",
    "Ván Cờ Sàn Cam & Khóa X",
    "Ba Cầu Liên Hoàn",
    "Đỉnh Cao Đại Bậc Thầy"
]

# Các trạng thái màn hình (Game State Machine)
STATE_MENU = 0
STATE_LEVEL_SELECT = 1
STATE_HOW_TO_PLAY = 2
STATE_PLAYING = 3

current_state = STATE_MENU

# ── 1. Khởi tạo Cửa sổ Raylib ─────────────────────────────────
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 740

rl.set_config_flags(rl.FLAG_MSAA_4X_HINT | rl.FLAG_WINDOW_RESIZABLE)
rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Bloxorz 3D — Deluxe Edition")
rl.set_exit_key(0)  # Vô hiệu hóa phím ESC thoát cửa sổ mặc định của Raylib
rl.set_target_fps(60)

# ── Khởi tạo Hệ thống Phông chữ Vector Anti-Aliased Hỗ trợ Tiếng Việt Đầy Đủ ──
ui_font_bold = None
ui_font_regular = None

# Bảng mã ký tự ASCII + Tiếng Việt có dấu đầy đủ
chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 `~!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?")
vn_chars = "aáàảãạăắằẳẵặâấầẩẫậeéèẻẽẹêếềểễệiíìỉĩịoóòỏõọôốồổỗộơớờởỡợuúùủũụưứừửữựyýỳỷỹỵdđ"
vn_chars += vn_chars.upper()
chars.update(vn_chars)
chars.update("·–—•+-/()▼▲")
VIETNAMESE_CODEPOINTS = sorted(list(set(ord(c) for c in chars)))


def init_fonts():
    """Nạp phông chữ vector độ nét cao hỗ trợ 100% Tiếng Việt có dấu, triệt tiêu lỗi dấu hỏi chấm"""
    global ui_font_bold, ui_font_regular

    font_bold_candidates = [
        # Đường dẫn trên Windows
        b"C:/Windows/Fonts/arialbd.ttf",
        b"C:/Windows/Fonts/segoeuib.ttf",
        # Đường dẫn trên macOS
        b"/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        b"/System/Library/Fonts/Supplemental/Trebuchet MS Bold.ttf",
    ]
    font_reg_candidates = [
        # Đường dẫn trên Windows
        b"C:/Windows/Fonts/arial.ttf",
        b"C:/Windows/Fonts/segoeui.ttf",
        # Đường dẫn trên macOS
        b"/System/Library/Fonts/Supplemental/Arial.ttf",
        b"/System/Library/Fonts/Supplemental/Trebuchet MS.ttf",
    ]

    try:
        from raylib import _raylib_cffi
        ffi = _raylib_cffi.ffi
        lib = _raylib_cffi.lib
        c_arr = ffi.new("int[]", VIETNAMESE_CODEPOINTS)
        num_cp = len(VIETNAMESE_CODEPOINTS)

        for p in font_bold_candidates:
            if os.path.exists(p.decode("utf-8")):
                try:
                    ui_font_bold = lib.LoadFontEx(p, 56, c_arr, num_cp)
                    rl.set_texture_filter(ui_font_bold.texture, rl.TEXTURE_FILTER_BILINEAR)
                    break
                except Exception:
                    pass

        for p in font_reg_candidates:
            if os.path.exists(p.decode("utf-8")):
                try:
                    ui_font_regular = lib.LoadFontEx(p, 40, c_arr, num_cp)
                    rl.set_texture_filter(ui_font_regular.texture, rl.TEXTURE_FILTER_BILINEAR)
                    break
                except Exception:
                    pass
    except Exception:
        # Fallback nếu không có CFFI
        pass


init_fonts()


def measure_text_ui(text, font_size, is_bold=False):
    """Đo chiều rộng text chính xác theo font TTF hoặc font mặc định"""
    font = ui_font_bold if (is_bold and ui_font_bold) else (ui_font_regular or ui_font_bold)
    if font is not None and hasattr(rl, "measure_text_ex"):
        try:
            vec = rl.measure_text_ex(font, str(text), float(font_size), 1.0)
            return int(vec.x)
        except Exception:
            pass
    return rl.measure_text(str(text), int(font_size))


def draw_text_ui(text, x, y, font_size, color, is_bold=False, shadow=False, shadow_color=None, glow=False, glow_color=None):
    """Vẽ chữ chất lượng cao Anti-Aliased kèm hiệu ứng đổ bóng 3D & phát quang Neon"""
    font = ui_font_bold if (is_bold and ui_font_bold) else (ui_font_regular or ui_font_bold)
    s_text = str(text)

    # 1. Hào quang Neon (Glow Aura)
    if glow:
        cr = getattr(color, 'r', color[0] if isinstance(color, (list, tuple)) else 255)
        cg = getattr(color, 'g', color[1] if isinstance(color, (list, tuple)) else 255)
        cb = getattr(color, 'b', color[2] if isinstance(color, (list, tuple)) else 255)
        g_col = glow_color if glow_color is not None else rl.Color(cr, cg, cb, 35)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            if font is not None and hasattr(rl, "draw_text_ex"):
                try:
                    rl.draw_text_ex(font, s_text, rl.Vector2(float(x + dx), float(y + dy)), float(font_size), 1.0, g_col)
                    continue
                except Exception:
                    pass
            rl.draw_text(s_text, int(x + dx), int(y + dy), int(font_size), g_col)

    # 2. Đổ bóng chiều sâu 3D (Drop Shadow)
    if shadow:
        sh_col = shadow_color if shadow_color is not None else rl.Color(0, 0, 0, 160)
        sh_offset = 2 if font_size >= 24 else 1
        if font is not None and hasattr(rl, "draw_text_ex"):
            try:
                rl.draw_text_ex(font, s_text, rl.Vector2(float(x + sh_offset), float(y + sh_offset)), float(font_size), 1.0, sh_col)
            except Exception:
                rl.draw_text(s_text, int(x + sh_offset), int(y + sh_offset), int(font_size), sh_col)
        else:
            rl.draw_text(s_text, int(x + sh_offset), int(y + sh_offset), int(font_size), sh_col)

    # 3. Lớp chữ chính siêu nét
    if font is not None and hasattr(rl, "draw_text_ex"):
        try:
            rl.draw_text_ex(font, s_text, rl.Vector2(float(x), float(y)), float(font_size), 1.0, color)
            return
        except Exception:
            pass
    rl.draw_text(s_text, int(x), int(y), int(font_size), color)

# ── 2. Bảng màu Sang trọng (Cyber-Slate & Imperial Gold) ───────
BG_COLOR = rl.Color(5, 10, 16, 255)
WIRE_COLOR = rl.Color(28, 42, 52, 180)

TILE_TOP_A = rl.Color(76, 100, 116, 255)
TILE_TOP_B = rl.Color(58, 78, 92, 255)
PEDESTAL_COLOR = rl.Color(22, 30, 38, 255)

FRAGILE_TOP = rl.Color(245, 115, 30, 255)
FRAGILE_BASE = rl.Color(95, 38, 14, 255)
FRAGILE_CORE = rl.Color(255, 170, 40, 255)

BRIDGE_TOP = rl.Color(135, 160, 255, 230)
BRIDGE_BASE = rl.Color(55, 68, 155, 200)

GOAL_HOLE = rl.Color(2, 5, 8, 255)
GOAL_RIM = rl.Color(0, 245, 255, 255)
GOAL_BEAM = rl.Color(0, 235, 245, 45)
GOAL_BEAM_WIRE = rl.Color(0, 240, 245, 140)

BLOCK_COLOR = rl.Color(238, 168, 38, 255)
BLOCK_WIRE = rl.Color(255, 218, 95, 240)

MINI_ACTIVE = rl.Color(0, 240, 245, 255)
MINI_ACTIVE_WIRE = rl.Color(180, 255, 255, 255)
MINI_IDLE = rl.Color(180, 135, 235, 255)
MINI_IDLE_WIRE = rl.Color(220, 190, 255, 220)

# ── 3. Quản lý Game, Camera & Bầu trời sao Vũ trụ ───────────────
game = BloxorzGame(0)

# Hệ thống Camera Orbital giảm chấn siêu mượt (Smooth Damping)
target_yaw = -25.0
target_pitch = 48.0
target_dist = 18.0
cam_yaw = -25.0
cam_pitch = 48.0
cam_dist = 18.0

camera = rl.Camera3D()
camera.up = rl.Vector3(0.0, 1.0, 0.0)
camera.fovy = 45.0
camera.projection = rl.CAMERA_PERSPECTIVE

spin_timer = 0.0

# 140 ngôi sao vũ trụ 3D lấp lánh đa tầng sâu thị sai (Tối ưu hóa triệt để, không giật lag)
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

# 24 Hạt bụi sao vũ trụ 3D bồng bềnh không trọng lực quanh đảo nổi (Zero-G Cosmic Stardust)
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
    """Tái sử dụng bộ đệm Vector3 của ngôi sao, triệt tiêu 100% rác bộ nhớ (GC) gây giật màn hình"""
    global cached_center, STAR_CACHE, STARDUST_CACHE
    center_c = (game.cols - 1) / 2.0
    center_r = (game.rows - 1) / 2.0
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


# Hệ thống Hạt va đập (Impact Spark & Dust Particles)
particles = []


def spawn_impact_sparks(x, z, count=16, is_gold=True):
    """Phát ra chùm tia lửa & bụi năng lượng khi khối đập xuống sàn"""
    for _ in range(count):
        ang = random.uniform(0.0, 2.0 * math.pi)
        spd = random.uniform(1.2, 3.2)
        vx = math.cos(ang) * spd
        vz = math.sin(ang) * spd
        vy = random.uniform(1.2, 3.2)
        life = random.uniform(0.28, 0.52)
        col = (255, 220, 90) if is_gold else (0, 245, 255)
        particles.append({
            "x": x, "y": 0.05, "z": z,
            "vx": vx, "vy": vy, "vz": vz,
            "life": life, "max_life": life,
            "sz": random.uniform(0.08, 0.14),
            "col": col
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


def draw_starfield():
    """Vẽ bầu trời sao vũ trụ 3D lấp lánh và bụi sao lơ lửng với bộ đệm tọa độ tối ưu mượt mà 60 FPS"""
    update_star_cache_if_needed()

    # 1. 140 Ngôi sao vũ trụ thị sai trong không gian 3D (Đã lưu sẵn Vector3 trong RAM, 0% rác GC)
    for star_pos, ssz, spd, phase, base_col in STAR_CACHE:
        twinkle = 0.5 + 0.5 * math.sin(spin_timer * spd + phase)
        alpha = int(110 + 145 * twinkle)
        col = rl.Color(base_col[0], base_col[1], base_col[2], alpha)
        rl.draw_cube(star_pos, ssz, ssz, ssz, col)

    # 2. 24 Hạt bụi sao vũ trụ 3D bồng bềnh không trọng lực quanh đảo nổi
    center_c = cached_center[0]
    center_r = cached_center[1]
    for dust_vec, ox, oy, oz, spd, phase, col_type in STARDUST_CACHE:
        bob_y = oy + math.sin(spin_timer * spd + phase) * 0.28
        dust_vec.x = center_c + ox
        dust_vec.y = bob_y
        dust_vec.z = center_r + oz
        sparkle = 0.5 + 0.5 * math.sin(spin_timer * spd * 1.6 + phase)
        alpha = int(75 + 140 * sparkle)
        col = rl.Color(165, 240, 255, alpha) if col_type == 0 else rl.Color(255, 220, 140, alpha)
        rl.draw_cube(dust_vec, 0.08, 0.08, 0.08, col)


# ── Hoạt ảnh Lật Vật lý 3D quanh Cạnh Đáy (3D Edge-Pivot Tumble) ──
roll_animating = False
anim_time = 0.0
anim_duration = 0.14
roll_angle = 0.0
roll_y_offset = 0.0
roll_info = {}
buffered_move = None


def grid_to_world(r, c, y=0.0):
    """Hệ tọa độ chuẩn: X=c (ngang), Y=y (cao), Z=r (dọc)"""
    return rl.Vector3(float(c), float(y), float(r))


def get_block_target_transform():
    """Tính toán kích thước và vị trí của khối hộp ở trạng thái tĩnh"""
    if not game.is_split:
        (r1, c1), (r2, c2) = game.block.state
        if game.block.is_standing():
            scale = rl.Vector3(0.92, 1.92, 0.92)
            y_base = 0.35 if game.status == "WON" else 0.96
            pos = grid_to_world(r1, c1, y=y_base)
        elif game.block.is_horizontal():
            scale = rl.Vector3(1.92, 0.92, 0.92)
            pos = grid_to_world(r1, (c1 + c2) / 2.0, y=0.46)
        else: # is_vertical
            scale = rl.Vector3(0.92, 0.92, 1.92)
            pos = grid_to_world((r1 + r2) / 2.0, c1, y=0.46)
        return pos, scale
    return None, None


def reset_camera():
    """Căn chỉnh camera tự động bao quát chính giữa bàn cờ"""
    global cam_yaw, cam_pitch, cam_dist, target_yaw, target_pitch, target_dist
    target_yaw = -25.0
    target_pitch = 48.0
    target_dist = max(game.rows, game.cols) * 1.48 + 4.0
    cam_yaw = target_yaw
    cam_pitch = target_pitch
    cam_dist = target_dist


def compute_roll_params_block(state, is_standing, is_horizontal, is_vertical, move_dir):
    """Tính toán trục quay và cạnh lật trên mặt sàn cho khối 1x1x2"""
    (r1, c1), (r2, c2) = state
    if is_standing:
        r, c = r1, c1
        old_pos = grid_to_world(r, c, y=0.96)
        old_size = rl.Vector3(0.92, 1.92, 0.92)
        if move_dir == "RIGHT":
            pivot = rl.Vector3(float(c) + 0.5, 0.0, float(r))
            axis = rl.Vector3(0.0, 0.0, -1.0)
        elif move_dir == "LEFT":
            pivot = rl.Vector3(float(c) - 0.5, 0.0, float(r))
            axis = rl.Vector3(0.0, 0.0, 1.0)
        elif move_dir == "UP":
            pivot = rl.Vector3(float(c), 0.0, float(r) - 0.5)
            axis = rl.Vector3(-1.0, 0.0, 0.0)
        else: # DOWN
            pivot = rl.Vector3(float(c), 0.0, float(r) + 0.5)
            axis = rl.Vector3(1.0, 0.0, 0.0)
    elif is_horizontal:
        r = r1
        min_c = min(c1, c2)
        max_c = max(c1, c2)
        center_c = (min_c + max_c) / 2.0
        old_pos = grid_to_world(r, center_c, y=0.46)
        old_size = rl.Vector3(1.92, 0.92, 0.92)
        if move_dir == "RIGHT":
            pivot = rl.Vector3(float(max_c) + 0.5, 0.0, float(r))
            axis = rl.Vector3(0.0, 0.0, -1.0)
        elif move_dir == "LEFT":
            pivot = rl.Vector3(float(min_c) - 0.5, 0.0, float(r))
            axis = rl.Vector3(0.0, 0.0, 1.0)
        elif move_dir == "UP":
            pivot = rl.Vector3(float(center_c), 0.0, float(r) - 0.5)
            axis = rl.Vector3(-1.0, 0.0, 0.0)
        else: # DOWN
            pivot = rl.Vector3(float(center_c), 0.0, float(r) + 0.5)
            axis = rl.Vector3(1.0, 0.0, 0.0)
    else: # is_vertical
        c = c1
        min_r = min(r1, r2)
        max_r = max(r1, r2)
        center_r = (min_r + max_r) / 2.0
        old_pos = grid_to_world(center_r, c, y=0.46)
        old_size = rl.Vector3(0.92, 0.92, 1.92)
        if move_dir == "RIGHT":
            pivot = rl.Vector3(float(c) + 0.5, 0.0, float(center_r))
            axis = rl.Vector3(0.0, 0.0, -1.0)
        elif move_dir == "LEFT":
            pivot = rl.Vector3(float(c) - 0.5, 0.0, float(center_r))
            axis = rl.Vector3(0.0, 0.0, 1.0)
        elif move_dir == "UP":
            pivot = rl.Vector3(float(c), 0.0, float(min_r) - 0.5)
            axis = rl.Vector3(-1.0, 0.0, 0.0)
        else: # DOWN
            pivot = rl.Vector3(float(c), 0.0, float(max_r) + 0.5)
            axis = rl.Vector3(1.0, 0.0, 0.0)
    return old_pos, old_size, pivot, axis


def compute_roll_params_mini(r, c, move_dir):
    """Tính toán trục quay và cạnh lật trên mặt sàn cho khối nhỏ 1x1x1"""
    old_pos = grid_to_world(r, c, y=0.46)
    old_size = rl.Vector3(0.92, 0.92, 0.92)
    if move_dir == "RIGHT":
        pivot = rl.Vector3(float(c) + 0.5, 0.0, float(r))
        axis = rl.Vector3(0.0, 0.0, -1.0)
    elif move_dir == "LEFT":
        pivot = rl.Vector3(float(c) - 0.5, 0.0, float(r))
        axis = rl.Vector3(0.0, 0.0, 1.0)
    elif move_dir == "UP":
        pivot = rl.Vector3(float(c), 0.0, float(r) - 0.5)
        axis = rl.Vector3(-1.0, 0.0, 0.0)
    else: # DOWN
        pivot = rl.Vector3(float(c), 0.0, float(r) + 0.5)
        axis = rl.Vector3(1.0, 0.0, 0.0)
    return old_pos, old_size, pivot, axis


def perform_move(move_dir):
    """Thực hiện bước đi và kích hoạt hiệu ứng xoay lật 90 độ vật lý quanh mép sàn"""
    global roll_animating, anim_time, anim_duration, roll_info, buffered_move, roll_angle, roll_y_offset

    if game.status != "PLAYING":
        return

    old_is_split = game.is_split
    if not old_is_split:
        old_state = game.block.state
        old_standing = game.block.is_standing()
        old_horizontal = game.block.is_horizontal()
        old_vertical = game.block.is_vertical()
    else:
        old_mini_pos = list(game.mini_blocks[game.active_block])
        old_active_idx = game.active_block

    res = game.move(move_dir)

    if res == "SPLIT" or game.last_event == "MERGE":
        roll_animating = False
        roll_angle = 0.0
        roll_y_offset = 0.0
        return

    if not old_is_split:
        p_old, s_old, pivot, axis = compute_roll_params_block(
            old_state, old_standing, old_horizontal, old_vertical, move_dir
        )
        is_mini = False
        mini_idx = -1
    else:
        p_old, s_old, pivot, axis = compute_roll_params_mini(
            old_mini_pos[0], old_mini_pos[1], move_dir
        )
        is_mini = True
        mini_idx = old_active_idx

    anim_time = 0.0
    if game.status == "LOST":
        anim_duration = 0.48
    elif game.status == "WON":
        anim_duration = 0.38
        # Chùm pháo hoa / tia lửa mừng chiến thắng rực rỡ tại ô đích
        pos_win, _ = get_block_target_transform()
        if pos_win:
            spawn_impact_sparks(pos_win.x, pos_win.z, count=36, is_gold=False)
    else:
        anim_duration = 0.14

    roll_angle = 0.0
    roll_y_offset = 0.0
    roll_info = {
        "is_mini": is_mini,
        "mini_idx": mini_idx,
        "old_pos": p_old,
        "old_size": s_old,
        "pivot": pivot,
        "axis": axis,
        "status": game.status,
        "lost_reason": game.lost_reason,
    }
    roll_animating = True

# ── Logic Điều Khiển Thuật Toán AI (A*, BFS, DFS,...) ──────────
def trigger_ai_solve(algo_name=None):
    """Tìm đường bằng thuật toán (nếu có truyền tên) và tự động di chuyển"""
    global ai_move_queue, ai_stats, current_solver_idx, show_solvers_dropdown
    show_solvers_dropdown = False  # Đóng menu sau khi đã chọn

    if game.status != "PLAYING":
        return
    # Nếu AI đang chạy mà bấm thì dừng lại
    if ai_move_queue and algo_name is None:
        ai_move_queue.clear()
        return

    # Nếu người chơi click chọn một thuật toán cụ thể từ dropdown
    if algo_name is not None and algo_name in solver_names:
        current_solver_idx = solver_names.index(algo_name)

    chosen_algo = solver_names[current_solver_idx]
    solver_fn = AVAILABLE_SOLVERS[chosen_algo]
    
    print(f"\n[*] Đang tìm đường bằng thuật toán: {chosen_algo}...")
    result = solver_fn(game)
    if result and result.get("moves"):
        ai_move_queue = list(result["moves"])
        ai_stats = result
        print(f"[{chosen_algo}] Đã tìm thấy {len(ai_move_queue)} bước! (Duyệt {result.get('nodes_expanded', 0)} trạng thái)")
    else:
        print(f"[{chosen_algo}] Không tìm thấy đường đi tới đích!")


def cycle_solver():
    """Chuyển đổi qua lại giữa các thuật toán có sẵn (A* -> BFS -> DFS -> ...)"""
    global current_solver_idx, ai_move_queue
    ai_move_queue.clear() # Dừng AI hiện tại nếu đang chạy
    current_solver_idx = (current_solver_idx + 1) % len(solver_names)
    print(f"[*] Đã chuyển sang thuật toán: {solver_names[current_solver_idx]}")


def draw_deluxe_block(pos, size, color, wire_color, is_golden=True):
    """Vẽ khối hộp kim loại vát cạnh sang trọng với bề mặt đồng nhất, sạch sẽ"""
    # 1. Khối hộp đồng nhất màu sắc toàn bộ 6 mặt (loại bỏ hoàn toàn mảng màu vàng sáng ở giữa)
    rl.draw_cube(pos, size.x, size.y, size.z, color)
    # 2. Khung viền vát cạnh phản quang tinh tế
    rl.draw_cube_wires(pos, size.x, size.y, size.z, wire_color)

    if not is_golden:
        # Khối phân thân ngọc lam đa chiều
        rl.draw_cube_wires(pos, size.x * 0.88, size.y * 0.88, size.z * 0.88, rl.Color(220, 255, 255, 160))


def draw_contact_shadow():
    """Vẽ bóng đổ mềm chân thực dưới đáy khối hộp trên mặt sàn"""
    if game.is_split:
        for i, (mr, mc) in enumerate(game.mini_blocks):
            if roll_animating and roll_info.get("is_mini", False) and i == roll_info.get("mini_idx", -1):
                piv = roll_info.get("pivot")
                old_p = roll_info.get("old_pos")
                ax = roll_info.get("axis")
                if piv and old_p and ax:
                    rad = math.radians(roll_angle)
                    if ax.z != 0:
                        dx = old_p.x - piv.x
                        dy = old_p.y - piv.y
                        sign = -1.0 if ax.z < 0 else 1.0
                        cx = piv.x + dx * math.cos(rad) - sign * dy * math.sin(rad)
                        cz = old_p.z
                    else:
                        dz = old_p.z - piv.z
                        dy = old_p.y - piv.y
                        sign = 1.0 if ax.x > 0 else -1.0
                        cz = piv.z + dz * math.cos(rad) + sign * dy * math.sin(rad)
                        cx = old_p.x
                    sh_pos = rl.Vector3(cx, 0.005, cz)
                    rl.draw_cube(sh_pos, 0.94, 0.006, 0.94, rl.Color(0, 0, 0, 115))
                    rl.draw_cube(sh_pos, 1.20, 0.004, 1.20, rl.Color(0, 0, 0, 45))
                    continue
            shadow_pos = grid_to_world(mr, mc, y=0.005)
            rl.draw_cube(shadow_pos, 0.94, 0.006, 0.94, rl.Color(0, 0, 0, 115))
            rl.draw_cube(shadow_pos, 1.20, 0.004, 1.20, rl.Color(0, 0, 0, 45))
        return

    # Khối 1x1x2
    if roll_animating:
        p = min(1.0, anim_time / anim_duration)
        rad = math.radians(roll_angle)
        piv = roll_info.get("pivot")
        old_p = roll_info.get("old_pos")
        ax = roll_info.get("axis")
        if not piv or not old_p or not ax:
            return

        if ax.z != 0:
            dx = old_p.x - piv.x
            dy = old_p.y - piv.y
            sign = -1.0 if ax.z < 0 else 1.0
            cx = piv.x + dx * math.cos(rad) - sign * dy * math.sin(rad)
            cy = piv.y + sign * dx * math.sin(rad) + dy * math.cos(rad)
            cz = old_p.z
        else:
            dz = old_p.z - piv.z
            dy = old_p.y - piv.y
            sign = 1.0 if ax.x > 0 else -1.0
            cz = piv.z + dz * math.cos(rad) + sign * dy * math.sin(rad)
            cy = piv.y - sign * dz * math.sin(rad) + dy * math.cos(rad)
            cx = old_p.x

        if cy < 0.1 and game.status == "LOST":
            return

        height_factor = max(0.0, min(1.0, (cy - 0.46) / 0.8))
        alpha_core = int(120 * (1.0 - height_factor * 0.4))
        alpha_soft = int(50 * (1.0 - height_factor * 0.4))
        spread = 1.0 + height_factor * 0.25

        s_old = roll_info.get("old_size", rl.Vector3(1, 1, 1))
        if ax.z != 0:
            cur_w = (abs(math.cos(rad)) * s_old.x + abs(math.sin(rad)) * s_old.y) * spread
            cur_d = s_old.z * spread
        else:
            cur_w = s_old.x * spread
            cur_d = (abs(math.cos(rad)) * s_old.z + abs(math.sin(rad)) * s_old.y) * spread

        sh_pos = rl.Vector3(cx, 0.005, cz)
        rl.draw_cube(sh_pos, cur_w * 0.95, 0.006, cur_d * 0.95, rl.Color(0, 0, 0, alpha_core))
        rl.draw_cube(sh_pos, cur_w * 1.25, 0.004, cur_d * 1.25, rl.Color(0, 0, 0, alpha_soft))
    else:
        if game.status != "LOST":
            pos, scale = get_block_target_transform()
            if pos:
                sh_pos = rl.Vector3(pos.x, 0.005, pos.z)
                rl.draw_cube(sh_pos, scale.x * 0.98, 0.006, scale.z * 0.98, rl.Color(0, 0, 0, 125))
                rl.draw_cube(sh_pos, scale.x * 1.25, 0.004, scale.z * 1.25, rl.Color(0, 0, 0, 45))


def draw_rolling_block(pivot, axis, angle_deg, pos, size, color, wire_color, y_offset=0.0, is_golden=True):
    """Vẽ khối hộp đang xoay lật quanh cạnh sàn bằng biến đổi ma trận rlgl"""
    rl.rl_push_matrix()
    rl.rl_translatef(pivot.x, pivot.y + y_offset, pivot.z)
    rl.rl_rotatef(angle_deg, axis.x, axis.y, axis.z)
    rl.rl_translatef(-pivot.x, -pivot.y, -pivot.z)

    draw_deluxe_block(pos, size, color, wire_color, is_golden=is_golden)

    rl.rl_pop_matrix()


def load_and_play_level(idx):
    """Nạp màn chơi và chuyển thẳng vào gameplay"""
    global current_state, roll_animating, buffered_move, roll_angle, roll_y_offset
    roll_animating = False
    buffered_move = None
    roll_angle = 0.0
    roll_y_offset = 0.0
    ai_move_queue.clear()  # Xóa hàng đợi bước cũ để khi người chơi đổi màn chơi thì AI tự dừng lại
    game.load_level(idx)
    reset_camera()
    current_state = STATE_PLAYING


# Khởi tạo góc nhìn ban đầu
reset_camera()


# ── 4. Hàm Hỗ trợ Vẽ Nút UI Bấm Chuột ─────────────────────────
def check_button(rec):
    """Kiểm tra chuột có đang hover hoặc click vào nút không"""
    mp = rl.get_mouse_position()
    hover = rl.check_collision_point_rec(mp, rec)
    clicked = hover and rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT)
    return hover, clicked


def draw_styled_button(rec, text, font_size=18, is_hover=False, active=False, accent_col=None):
    """Vẽ nút bấm bo góc sang trọng có hiệu ứng hover phát quang & đổ bóng chữ"""
    if accent_col is None:
        accent_col = rl.Color(0, 240, 245, 255)

    ar = getattr(accent_col, 'r', accent_col[0] if isinstance(accent_col, (list, tuple)) else 0)
    ag = getattr(accent_col, 'g', accent_col[1] if isinstance(accent_col, (list, tuple)) else 240)
    ab = getattr(accent_col, 'b', accent_col[2] if isinstance(accent_col, (list, tuple)) else 245)

    if active:
        bg = rl.Color(28, 70, 88, 245)
        border = accent_col
        text_col = rl.Color(255, 255, 255, 255)
    elif is_hover:
        bg = rl.Color(34, 62, 80, 245)
        border = accent_col
        text_col = accent_col
        # Hào quang viền ngoài khi hover
        glow_rec = rl.Rectangle(rec.x - 3, rec.y - 3, rec.width + 6, rec.height + 6)
        rl.draw_rectangle_rounded(glow_rec, 0.28, 8, rl.Color(ar, ag, ab, 35))
    else:
        bg = rl.Color(16, 32, 44, 215)
        border = rl.Color(65, 90, 110, 180)
        text_col = rl.Color(215, 235, 245, 255)

    rl.draw_rectangle_rounded(rec, 0.28, 8, bg)
    rl.draw_rectangle_rounded_lines(rec, 0.28, 8, border)

    # Vệt phản chiếu ánh sáng thủy tinh (Glass Reflection Highlight)
    top_highlight = rl.Rectangle(rec.x + 2, rec.y + 2, rec.width - 4, rec.height * 0.40)
    rl.draw_rectangle_rounded(top_highlight, 0.28, 8, rl.Color(255, 255, 255, 12))

    tw = measure_text_ui(text, font_size, is_bold=True)
    tx = int(rec.x + rec.width / 2 - tw / 2)
    ty = int(rec.y + rec.height / 2 - font_size / 2)
    draw_text_ui(text, tx, ty, font_size, text_col, is_bold=True, shadow=True, glow=is_hover, glow_color=rl.Color(ar, ag, ab, 50))


# ── Bầu trời Không gian Vũ trụ Sâu thẳm (Deep-Space Cosmic Backdrop & Nebulae) ──
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
    """Vẽ đám mây tinh vân phát quang mềm mại tương thích chuẩn xác với cả PyRay Vector2 và C API"""
    if hasattr(rl, "draw_circle_gradient"):
        try:
            # PyRay API chuẩn: 4 tham số (Vector2 center, float radius, Color inner, Color outer)
            rl.draw_circle_gradient(rl.Vector2(float(cx), float(cy)), float(radius), col1, col2)
        except TypeError:
            try:
                # Fallback C-style API: 5 tham số (int cx, int cy, float radius, Color col1, Color col2)
                rl.draw_circle_gradient(int(cx), int(cy), float(radius), col1, col2)
            except Exception:
                pass
        except Exception:
            pass


def draw_star_circle(x, y, radius, col):
    """Vẽ vòng tròn phát quang hào quang sao an toàn tương thích mọi môi trường"""
    if hasattr(rl, "draw_circle"):
        try:
            rl.draw_circle(int(x), int(y), float(radius), col)
        except TypeError:
            try:
                rl.draw_circle(rl.Vector2(float(x), float(y)), float(radius), col)
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

    # 2. Các cụm mây Tinh vân Vũ trụ (Nebula Glow Clouds) huyền ảo
    # Tinh vân tử quang huyền bí (Cosmic Magenta Nebula) ở góc trên bên phải
    r1 = float(w * 0.44 + math.sin(spin_timer * 0.25) * 16.0)
    draw_nebula_cloud(w * 0.82, h * 0.24, r1, rl.Color(82, 26, 128, 75), rl.Color(6, 4, 16, 0))

    # Tinh vân thanh lam tinh khôi (Teal & Cyan Stellar Nursery) ở góc dưới bên trái
    r2 = float(w * 0.40 + math.cos(spin_timer * 0.20) * 14.0)
    draw_nebula_cloud(w * 0.16, h * 0.78, r2, rl.Color(16, 75, 108, 65), rl.Color(4, 10, 20, 0))

    # Lõi ngân hà tím sẫm (Deep Galactic Core) ở trung tâm phía sau đảo nổi
    r3 = float(w * 0.36 + math.sin(spin_timer * 0.16 + 1.0) * 10.0)
    draw_nebula_cloud(w * 0.52, h * 0.46, r3, rl.Color(44, 22, 78, 48), rl.Color(5, 6, 16, 0))

    # 3. Dải sao vũ trụ 2D đa sắc & sao phát quang chữ thập (Diffraction Spikes)
    for nx, ny, sz, spd, phase, base_rgb, has_flare in COSMIC_STARS_2D:
        sx = int(nx * w)
        sy = int(ny * h)
        twinkle = 0.42 + 0.58 * math.sin(spin_timer * spd + phase)
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

    # 4. Sao Băng lướt qua bầu trời vũ trụ (Cosmic Shooting Star / Meteor)
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


# ── 5. Hàm Vẽ Bàn cờ 3D ───────────────────────────────────────
def draw_3d_scene(dt):
    """Vẽ toàn bộ bàn cờ đa tầng, công tắc, lỗ đích và khối hộp"""
    # ── 1. Bầu trời sao vũ trụ & Tinh vân thị sai ──
    draw_starfield()

    # ── 2. Dựng các ô sàn đa tầng vát cạnh ──
    for r in range(game.rows):
        for c in range(game.cols):
            bid, binfo = game.get_bridge_at(r, c)

            # Cầu nối (Kiểm tra trước vì ô cầu nằm trên vực thẳm board == 0)
            if binfo is not None:
                if binfo["is_open"]:
                    pos_base = grid_to_world(r, c, y=-0.22)
                    pos_top = grid_to_world(r, c, y=-0.05)
                    rl.draw_cube(pos_base, 0.96, 0.28, 0.96, BRIDGE_BASE)
                    rl.draw_cube(pos_top, 0.84, 0.06, 0.84, BRIDGE_TOP)
                    rl.draw_cube_wires(pos_top, 0.84, 0.06, 0.84, rl.Color(190, 220, 255, 255))
                    # Lõi năng lượng phát quang của cầu nối
                    rl.draw_cube(grid_to_world(r, c, y=-0.035), 0.68, 0.02, 0.68, rl.Color(140, 185, 255, 130))
                else:
                    # Chốt neo cầu nối ngầm trong bóng tối vực thẳm
                    anchor_pos = grid_to_world(r, c, y=-0.42)
                    rl.draw_cube_wires(anchor_pos, 0.42, 0.08, 0.42, rl.Color(40, 58, 75, 100))
                continue

            t = game.board[r][c]
            if t == 0:
                continue

            pos_base = grid_to_world(r, c, y=-0.22)
            pos_top = grid_to_world(r, c, y=-0.05)

            # Ô lỗ đích (Sci-Fi Void Portal)
            if t == 2:
                # Miệng hố không gian sâu thẳm
                rl.draw_cube(grid_to_world(r, c, y=-0.38), 0.96, 0.16, 0.96, GOAL_HOLE)
                glow_alpha = int(185 + 70 * math.sin(spin_timer * 5.0))
                rl.draw_cube_wires(grid_to_world(r, c, y=-0.01), 0.88, 0.02, 0.88, rl.Color(0, 245, 255, glow_alpha))
                rl.draw_cube_wires(grid_to_world(r, c, y=-0.03), 0.74, 0.02, 0.74, rl.Color(0, 210, 255, glow_alpha // 2))

                # Cột sáng năng lượng lượng tử xoay tròn
                beam_pos = grid_to_world(r, c, y=2.2)
                rl.draw_cube(beam_pos, 0.28, 4.4, 0.28, GOAL_BEAM)
                rl.draw_cube_wires(beam_pos, 0.30, 4.4, 0.30, GOAL_BEAM_WIRE)

                # 3 Vòng hào quang năng lượng bay lượn từ lỗ đích lên bầu trời
                for ring_i in range(3):
                    ring_phase = (spin_timer * 1.5 + ring_i * 1.33) % 4.0
                    ring_y = ring_phase
                    ring_alpha = int(220 * (1.0 - ring_y / 4.0))
                    ring_scale = 0.36 + 0.08 * math.sin(spin_timer * 4.0 + ring_i)
                    ring_pos = grid_to_world(r, c, y=ring_y)
                    rl.draw_cylinder_wires(ring_pos, ring_scale, ring_scale, 0.03, 16, rl.Color(0, 245, 255, ring_alpha))

            # Ô cam dễ vỡ (Magma Fissure Plate)
            elif t == 3:
                y_drop = 0.0
                if game.status == "LOST" and game.broken_tile == [r, c]:
                    y_drop = roll_y_offset if roll_animating else -20.0

                magma_pulse = 0.65 + 0.35 * math.sin(spin_timer * 4.5 + (r * 1.7 + c * 2.3))
                pos_f_base = grid_to_world(r, c, y=-0.22 + y_drop)
                pos_f_top = grid_to_world(r, c, y=-0.05 + y_drop)
                rl.draw_cube(pos_f_base, 0.96, 0.28, 0.96, FRAGILE_BASE)
                rl.draw_cube(pos_f_top, 0.84, 0.06, 0.84, FRAGILE_TOP)
                rl.draw_cube_wires(pos_f_top, 0.84, 0.06, 0.84, rl.Color(255, 195, 80, 255))

                # Đường nứt nham thạch rực sáng (Magma Cracks)
                fissure_col = rl.Color(255, int(130 + 85 * magma_pulse), 35, 240)
                fissure_pos = grid_to_world(r, c, y=-0.04 + y_drop)
                rl.draw_cube(fissure_pos, 0.72, 0.02, 0.12, fissure_col)
                rl.draw_cube(fissure_pos, 0.12, 0.02, 0.72, fissure_col)
                rl.draw_cube(fissure_pos, 0.36, 0.035, 0.36, rl.Color(255, int(160 + 85 * magma_pulse), 50, 255))

            # Ô sàn thường (Caro đá phiến tương phản có rãnh viền công nghệ)
            else:
                top_col = TILE_TOP_A if (r + c) % 2 == 0 else TILE_TOP_B
                rl.draw_cube(pos_base, 0.96, 0.28, 0.96, PEDESTAL_COLOR)
                rl.draw_cube(pos_top, 0.84, 0.06, 0.84, top_col)
                rl.draw_cube_wires(pos_top, 0.84, 0.06, 0.84, WIRE_COLOR)
                # Rãnh chạm khắc chìm tinh xảo bên trong mỗi ô gạch
                groove_pos = grid_to_world(r, c, y=-0.046)
                rl.draw_cube_wires(groove_pos, 0.66, 0.01, 0.66, rl.Color(32, 46, 56, 110))

    # ── 3. Dựng các công tắc nổi 3D với hiệu ứng phát quang ──
    for sw in game.switches:
        sr, sc = sw["pos"]
        stype = sw["type"]
        spos_base = grid_to_world(sr, sc, y=0.01)
        spos_top = grid_to_world(sr, sc, y=0.05)

        if stype == "soft":
            # Công tắc tròn mềm (Đế titan + Mái vòm ngọc bích phát sáng)
            pulse_s = 0.75 + 0.25 * math.sin(spin_timer * 4.0)
            rl.draw_cylinder(spos_base, 0.38, 0.38, 0.03, 16, rl.Color(38, 52, 60, 255))
            rl.draw_cylinder(spos_top, 0.28, 0.28, 0.09, 16, rl.Color(46, int(210 + 35 * pulse_s), 125, 255))
            rl.draw_cylinder_wires(spos_top, 0.28, 0.28, 0.09, 16, rl.Color(180, 255, 210, 255))
            rl.draw_cylinder_wires(spos_base, 0.44 * pulse_s, 0.44 * pulse_s, 0.01, 16, rl.Color(50, 240, 140, int(115 * pulse_s)))

        elif stype == "heavy":
            # Công tắc nặng chữ X (Đế vuông + Chữ X hồng ngọc Ruby sang trọng)
            pulse_h = 0.75 + 0.25 * math.sin(spin_timer * 5.0)
            rl.draw_cube(spos_base, 0.76, 0.03, 0.76, rl.Color(38, 52, 60, 255))
            ruby_col = rl.Color(255, int(50 + 20 * pulse_h), int(70 + 20 * pulse_h), 255)
            rl.draw_cube(spos_top, 0.68, 0.09, 0.20, ruby_col)
            rl.draw_cube(spos_top, 0.20, 0.09, 0.68, ruby_col)
            rl.draw_cube_wires(spos_top, 0.68, 0.09, 0.20, rl.Color(255, 180, 190, 255))
            rl.draw_cube_wires(spos_top, 0.20, 0.09, 0.68, rl.Color(255, 180, 190, 255))

        elif stype == "split":
            # Công tắc phân thân (Vòng tròn ngọc lam lượng tử)
            pulse_sp = 0.75 + 0.25 * math.sin(spin_timer * 6.0)
            rl.draw_cylinder(spos_base, 0.38, 0.38, 0.03, 16, rl.Color(28, 46, 56, 255))
            rl.draw_cylinder(spos_top, 0.27, 0.27, 0.07, 16, rl.Color(0, int(220 + 35 * pulse_sp), 245, 255))
            rl.draw_cylinder_wires(spos_top, 0.27, 0.27, 0.07, 16, rl.Color(190, 255, 255, 255))
            rl.draw_cylinder_wires(spos_base, 0.44 * pulse_sp, 0.44 * pulse_sp, 0.01, 16, rl.Color(0, 240, 255, int(120 * pulse_sp)))

    # ── 4. Bóng đổ tiếp xúc mềm chân thực (Dynamic Contact Shadow) ──
    draw_contact_shadow()

    # ── 5. Dựng khối hộp Bloxorz Deluxe (Khối vàng thỏi & Khối ngọc lam) ──
    if not game.is_split:
        if roll_animating and not roll_info.get("is_mini", False):
            draw_rolling_block(
                roll_info["pivot"],
                roll_info["axis"],
                roll_angle,
                roll_info["old_pos"],
                roll_info["old_size"],
                BLOCK_COLOR,
                BLOCK_WIRE,
                roll_y_offset,
                is_golden=True
            )
        else:
            if not (game.status == "LOST" and game.lost_reason in ("FALL", "FRAGILE_BREAK", "BRIDGE_CLOSED")):
                pos, scale = get_block_target_transform()
                if pos:
                    draw_deluxe_block(pos, scale, BLOCK_COLOR, BLOCK_WIRE, is_golden=True)
    else:
        # Chế độ tách 2 khối nhỏ 1x1x1
        for i, (mr, mc) in enumerate(game.mini_blocks):
            is_active = (i == game.active_block)
            col = MINI_ACTIVE if is_active else MINI_IDLE
            wire_col = MINI_ACTIVE_WIRE if is_active else MINI_IDLE_WIRE

            if roll_animating and roll_info.get("is_mini", False) and i == roll_info.get("mini_idx", -1):
                draw_rolling_block(
                    roll_info["pivot"],
                    roll_info["axis"],
                    roll_angle,
                    roll_info["old_pos"],
                    roll_info["old_size"],
                    col,
                    wire_col,
                    roll_y_offset,
                    is_golden=False
                )
            else:
                if not (game.status == "LOST" and is_active):
                    mpos = grid_to_world(mr, mc, y=0.46)
                    draw_deluxe_block(mpos, rl.Vector3(0.92, 0.92, 0.92), col, wire_col, is_golden=False)

            # Vòng hào quang xoay lơ lửng trên khối đang chọn
            if is_active and not (game.status == "LOST"):
                halo_y = 1.25 + math.sin(spin_timer * 4.0) * 0.06
                halo_pos = grid_to_world(mr, mc, y=halo_y)
                rl.draw_cylinder_wires(halo_pos, 0.32, 0.32, 0.04, 16, rl.Color(0, 255, 255, 255))
                rl.draw_cylinder_wires(halo_pos, 0.40, 0.40, 0.02, 16, rl.Color(0, 220, 255, 140))

    # ── 6. Hiệu ứng hạt va đập & tia lửa phát sáng trong không gian 3D ──
    update_and_draw_particles(dt)


# ── 6. Giao diện Màn hình MENU CHÍNH ──────────────────────────
def draw_menu_screen(w, h):
    """Màn hình Menu chính khởi đầu game"""
    global current_state

    # Lớp phủ mờ nền tối
    rl.draw_rectangle(0, 0, w, h, rl.Color(8, 16, 22, 215))

    # Tiêu đề Game hoành tráng phong cách Neon Hoàng Gia
    t_logo = "BLOXORZ 3D"
    w_logo = measure_text_ui(t_logo, 62, is_bold=True)
    draw_text_ui(
        t_logo,
        w // 2 - w_logo // 2,
        90,
        62,
        rl.Color(255, 215, 80, 255),
        is_bold=True,
        shadow=True,
        shadow_color=rl.Color(0, 0, 0, 220),
        glow=True,
        glow_color=rl.Color(255, 195, 50, 50)
    )

    # Cụm nút Menu chính
    btn_w, btn_h = 380, 54
    start_y = 195
    gap = 70

    play_label = "TIẾP TỤC CHƠI" if game.moves > 0 else "BẮT ĐẦU CHƠI"
    btn_play_rec = rl.Rectangle(w // 2 - btn_w // 2, start_y, btn_w, btn_h)
    btn_lvl_rec = rl.Rectangle(w // 2 - btn_w // 2, start_y + gap, btn_w, btn_h)
    btn_help_rec = rl.Rectangle(w // 2 - btn_w // 2, start_y + gap * 2, btn_w, btn_h)
    btn_exit_rec = rl.Rectangle(w // 2 - btn_w // 2, start_y + gap * 3, btn_w, btn_h)

    # 1. Nút Vào chơi
    h_play, c_play = check_button(btn_play_rec)
    draw_styled_button(btn_play_rec, play_label, 19, h_play, accent_col=rl.Color(65, 245, 160, 255))
    if c_play:
        current_state = STATE_PLAYING

    # 2. Nút Chọn màn (1 - 12)
    h_lvl, c_lvl = check_button(btn_lvl_rec)
    draw_styled_button(btn_lvl_rec, "CHỌN MÀN CHƠI (1 - 12)", 18, h_lvl, accent_col=rl.Color(0, 240, 245, 255))
    if c_lvl:
        current_state = STATE_LEVEL_SELECT

    # 3. Nút Hướng dẫn
    h_help, c_help = check_button(btn_help_rec)
    draw_styled_button(btn_help_rec, "HƯỚNG DẪN LUẬT CHƠI", 18, h_help, accent_col=rl.Color(255, 195, 80, 255))
    if c_help:
        current_state = STATE_HOW_TO_PLAY

    # 4. Nút Thoát
    h_exit, c_exit = check_button(btn_exit_rec)
    draw_styled_button(btn_exit_rec, "THOÁT TRÒ CHƠI", 18, h_exit, accent_col=rl.Color(255, 80, 85, 255))
    if c_exit:
        rl.close_window()
        sys.exit(0)

    # Dòng chỉ dẫn nhỏ phía dưới dạng thanh badge
    hint = "Dùng Chuột để chọn  ·  Nhấn [ESC] để vào / ra Menu bất kỳ lúc nào"
    w_hint = measure_text_ui(hint, 13)
    hint_pill = rl.Rectangle(w // 2 - w_hint // 2 - 14, h - 48, w_hint + 28, 26)
    rl.draw_rectangle_rounded(hint_pill, 0.45, 8, rl.Color(14, 28, 38, 190))
    rl.draw_rectangle_rounded_lines(hint_pill, 0.45, 8, rl.Color(60, 85, 105, 140))
    draw_text_ui(hint, w // 2 - w_hint // 2, h - 42, 13, rl.Color(165, 195, 210, 220))


# ── 7. Giao diện Màn hình CHỌN MÀN (1 - 12) ───────────────────
def draw_level_select_screen(w, h):
    """Màn hình lưới 12 màn chơi trực quan với thẻ bài Glassmorphic cao cấp"""
    global current_state

    rl.draw_rectangle(0, 0, w, h, rl.Color(8, 16, 22, 235))

    title = "CHỌN MÀN CHƠI (1 - 12)"
    wt = measure_text_ui(title, 34, is_bold=True)
    draw_text_ui(title, w // 2 - wt // 2, 40, 34, rl.Color(255, 215, 80, 255), is_bold=True, shadow=True, glow=True)

    subtitle = "Nhấp chuột vào màn bất kỳ để bắt đầu thử thách"
    wsub = measure_text_ui(subtitle, 15)
    draw_text_ui(subtitle, w // 2 - wsub // 2, 84, 15, rl.Color(0, 235, 245, 220))

    # Lưới 4 cột x 3 hàng = 12 màn
    cols = 4
    rows = 3
    card_w = 230
    card_h = 92
    gap_x = 24
    gap_y = 20

    total_w = cols * card_w + (cols - 1) * gap_x
    start_x = w // 2 - total_w // 2
    start_y = 135

    for i in range(len(LEVELS)):
        col_idx = i % cols
        row_idx = i // cols
        cx = start_x + col_idx * (card_w + gap_x)
        cy = start_y + row_idx * (card_h + gap_y)

        crec = rl.Rectangle(cx, cy, card_w, card_h)
        is_cur = (i == game.level_index)
        hover, clicked = check_button(crec)

        if clicked:
            load_and_play_level(i)
            return

        # Màu nền card
        if is_cur:
            bg_col = rl.Color(26, 62, 78, 245)
            border_col = rl.Color(255, 210, 75, 255)
        elif hover:
            bg_col = rl.Color(34, 62, 80, 245)
            border_col = rl.Color(0, 240, 245, 255)
            # Hào quang viền ngoài khi hover
            glow_crec = rl.Rectangle(cx - 3, cy - 3, card_w + 6, card_h + 6)
            rl.draw_rectangle_rounded(glow_crec, 0.18, 8, rl.Color(0, 240, 245, 30))
        else:
            bg_col = rl.Color(16, 32, 44, 215)
            border_col = rl.Color(65, 88, 105, 180)

        rl.draw_rectangle_rounded(crec, 0.18, 8, bg_col)
        rl.draw_rectangle_rounded_lines(crec, 0.18, 8, border_col)

        # Vệt phản chiếu ánh sáng thủy tinh (Top Glass Highlight)
        top_hl = rl.Rectangle(cx + 2, cy + 2, card_w - 4, card_h * 0.38)
        rl.draw_rectangle_rounded(top_hl, 0.18, 8, rl.Color(255, 255, 255, 10))

        # Thông tin bên trong card
        lvl_num_text = f"MÀN {i + 1:02d}"
        lvl_name_text = LEVEL_NAMES_VI[i] if i < len(LEVEL_NAMES_VI) else f"Màn {i+1}"

        pill_col = rl.Color(255, 210, 75, 255) if is_cur else rl.Color(0, 240, 245, 255)
        draw_text_ui(lvl_num_text, cx + 16, cy + 14, 16, pill_col, is_bold=True, shadow=True)
        draw_text_ui(lvl_name_text, cx + 16, cy + 38, 14, rl.Color(225, 240, 250, 255), is_bold=True)

        status_tag = "ĐANG CHƠI" if is_cur else "VÀO CHƠI"
        tag_col = rl.Color(65, 245, 160, 255) if is_cur else rl.Color(150, 185, 205, 200)
        draw_text_ui(status_tag, cx + 16, cy + 64, 12, tag_col)

    # Nút quay lại Menu
    btn_back_rec = rl.Rectangle(w // 2 - 130, h - 68, 260, 44)
    h_back, c_back = check_button(btn_back_rec)
    draw_styled_button(btn_back_rec, "< QUAY LẠI MENU", 17, h_back)
    if c_back:
        current_state = STATE_MENU


# ── 8. Giao diện Màn hình HƯỚNG DẪN LUẬT CHƠI ─────────────────
def draw_how_to_play_screen(w, h):
    """Màn hình tóm tắt cơ chế các loại ô và công tắc"""
    global current_state

    rl.draw_rectangle(0, 0, w, h, rl.Color(8, 16, 22, 235))

    card_w, card_h = 780, 560
    cx = w // 2 - card_w // 2
    cy = h // 2 - card_h // 2 - 10

    card_rec = rl.Rectangle(cx, cy, card_w, card_h)
    rl.draw_rectangle_rounded(card_rec, 0.12, 8, rl.Color(14, 28, 38, 250))
    rl.draw_rectangle_rounded_lines(card_rec, 0.12, 8, rl.Color(0, 235, 245, 160))

    title = "HƯỚNG DẪN & LUẬT CHƠI BLOXORZ"
    wt = measure_text_ui(title, 26, is_bold=True)
    draw_text_ui(title, w // 2 - wt // 2, cy + 24, 26, rl.Color(255, 215, 80, 255), is_bold=True, shadow=True, glow=True)

    # Danh sách các cơ chế cốt lõi
    rules = [
        ("MỤC TIÊU:", "Lăn khối hộp 1x1x2 đứng thẳng hoàn toàn vào ô đích màu Xanh Neon để chiến thắng.", rl.Color(0, 240, 245, 255)),
        ("SÀN CAM DỄ VỠ:", "Khối chỉ được NẰM đè lên ô cam. Đứng thẳng sẽ làm sàn vỡ và rơi xuống vực!", rl.Color(255, 140, 45, 255)),
        ("CÔNG TẮC TRÒN (MỀM):", "Chạm nhẹ bất kỳ phần nào của khối lên nút tròn đều kích hoạt đóng / mở cầu.", rl.Color(46, 225, 125, 255)),
        ("CÔNG TẮC CHỮ X (NẶNG):", "CHỈ kích hoạt khi khối ĐỨNG THẲNG trên nút. Nằm đè lên sẽ không có tác dụng!", rl.Color(255, 75, 85, 255)),
        ("CÔNG TẮC PHÂN THÂN:", "Đứng thẳng lên để tách khối làm 2 khối nhỏ 1x1x1. Bấm Space để đổi khối.", rl.Color(0, 230, 245, 255)),
        ("HỢP NHẤT KHỐI (GỘP):", "Di chuyển 2 khối nhỏ lại gần nhau sẽ tự động hợp nhất trở lại thành khối lớn.", rl.Color(185, 140, 245, 255)),
        ("ĐIỀU KHIỂN:", "[W/A/S/D]: Lăn khối  ·  [Kéo Chuột]: Xoay 3D  ·  [Z]: Hoàn tác  ·  [R]: Chơi lại", rl.Color(220, 240, 250, 255))
    ]

    item_y = cy + 76
    for tag, desc, col in rules:
        draw_text_ui(tag, cx + 38, item_y, 16, col, is_bold=True, shadow=True)
        draw_text_ui(desc, cx + 38, item_y + 22, 14, rl.Color(210, 230, 240, 255))
        item_y += 57

    # Nút Đã hiểu
    btn_ok_rec = rl.Rectangle(w // 2 - 130, cy + card_h - 58, 260, 44)
    h_ok, c_ok = check_button(btn_ok_rec)
    draw_styled_button(btn_ok_rec, "< ĐÃ HIỂU", 17, h_ok)
    if c_ok:
        current_state = STATE_MENU


# ── 9. Giao diện 2D HUD & Hiệu ứng Điện ảnh ────────────────────
def draw_cinematic_vignette(w, h):
    """Vẽ viền tối điện ảnh (Screen-Space Vignette) tạo chiều sâu tập trung"""
    if hasattr(rl, "draw_rectangle_gradient_v") and hasattr(rl, "draw_rectangle_gradient_h"):
        v_size = 96
        rl.draw_rectangle_gradient_v(0, 0, w, v_size, rl.Color(0, 0, 0, 130), rl.Color(0, 0, 0, 0))
        rl.draw_rectangle_gradient_v(0, h - v_size, w, v_size, rl.Color(0, 0, 0, 0), rl.Color(0, 0, 0, 150))
        rl.draw_rectangle_gradient_h(0, 0, v_size, h, rl.Color(0, 0, 0, 130), rl.Color(0, 0, 0, 0))
        rl.draw_rectangle_gradient_h(w - v_size, 0, v_size, h, rl.Color(0, 0, 0, 0), rl.Color(0, 0, 0, 130))


def draw_2d_hud():
    """Bảng thông tin khi đang chơi, nút Menu và Modal Thắng/Thua"""
    global current_state, roll_animating, buffered_move, ai_move_queue

    w = rl.get_screen_width()
    h = rl.get_screen_height()

    clean_name = LEVEL_NAMES_VI[game.level_index] if game.level_index < len(LEVEL_NAMES_VI) else f"Màn {game.level_index + 1}"

    # Card thông tin góc trái
    card_rect = rl.Rectangle(24, 20, 340, 96)
    rl.draw_rectangle_rounded(card_rect, 0.16, 8, rl.Color(14, 28, 38, 225))
    rl.draw_rectangle_rounded_lines(card_rect, 0.16, 8, rl.Color(0, 240, 245, 140))

    # Vệt phản chiếu ánh sáng thủy tinh (Glass highlight)
    c_hl = rl.Rectangle(26, 22, 336, 38)
    rl.draw_rectangle_rounded(c_hl, 0.16, 8, rl.Color(255, 255, 255, 10))

    draw_text_ui("BLOXORZ 3D", 40, 30, 22, rl.Color(255, 215, 80, 255), is_bold=True, shadow=True, glow=True, glow_color=rl.Color(255, 195, 50, 40))
    draw_text_ui(f"MÀN {game.level_index + 1:02d}  ·  {clean_name}", 40, 58, 14, rl.Color(220, 240, 250, 255), is_bold=True)
    draw_text_ui(f"BƯỚC ĐI: {game.moves}", 40, 82, 18, rl.Color(0, 240, 245, 255), is_bold=True, glow=True)

    # ── [NÚT SOLVERS DROPDOWN] ─────────────────────────────────
    global show_solvers_dropdown
    btn_solvers = rl.Rectangle(w - 295, 24, 135, 40)
    h_solvers, c_solvers = check_button(btn_solvers)
    
    # Nếu AI đang tự chạy thì hiện nút "DỪNG AI", ngược lại hiện "SOLVERS ▼"
    if ai_move_queue:
        solvers_label = "DỪNG AI"
        draw_styled_button(btn_solvers, solvers_label, 14, h_solvers, active=True, accent_col=rl.Color(255, 80, 85, 255))
        if c_solvers:
            ai_move_queue.clear()
    else:
        arrow = "▲" if show_solvers_dropdown else "▼"
        solvers_label = f"SOLVERS {arrow}"
        draw_styled_button(btn_solvers, solvers_label, 14, h_solvers, active=show_solvers_dropdown, accent_col=rl.Color(65, 245, 160, 255))
        if c_solvers:
            show_solvers_dropdown = not show_solvers_dropdown

    # Vẽ danh sách menu xổ xuống khi show_solvers_dropdown = True
    if show_solvers_dropdown and not ai_move_queue:
        item_h = 36
        total_menu_h = len(solver_names) * (item_h + 4) + 6
        drop_rect = rl.Rectangle(w - 295, 68, 135, total_menu_h)
        
        # Khung nền đổ bóng cho menu dropdown
        rl.draw_rectangle_rounded(drop_rect, 0.16, 6, rl.Color(14, 24, 34, 250))
        rl.draw_rectangle_rounded_lines(drop_rect, 0.16, 6, rl.Color(0, 240, 245, 180))

        # Vẽ từng thuật toán có trong hệ thống (A*, BFS, DFS,...)
        for idx, name in enumerate(solver_names):
            item_rect = rl.Rectangle(w - 290, 72 + idx * (item_h + 4), 125, item_h)
            h_item, c_item = check_button(item_rect)
            draw_styled_button(
                item_rect,
                name,
                14,
                h_item,
                accent_col=rl.Color(0, 240, 245, 255)
            )
            # Click vào thuật toán nào -> chạy ngay thuật toán đó!
            if c_item:
                trigger_ai_solve(name)

        # Tự động đóng menu nếu người chơi click chuột ra ngoài vùng menu
        if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT) and not h_solvers:
            mouse_pos = rl.get_mouse_position()
            if not rl.check_collision_point_rec(mouse_pos, drop_rect):
                show_solvers_dropdown = False

    # Nút [MENU (ESC)] ở góc trên bên phải
    btn_menu_top = rl.Rectangle(w - 150, 24, 126, 40)
    h_mtop, c_mtop = check_button(btn_menu_top)
    draw_styled_button(btn_menu_top, "MENU (ESC)", 15, h_mtop, accent_col=rl.Color(255, 215, 80, 255))
    if c_mtop:
        ai_move_queue.clear()
        current_state = STATE_MENU

    # Thanh điều khiển đáy màn hình
    bar_w = min(w - 40, 960)
    bar_rect = rl.Rectangle(w // 2 - bar_w // 2, h - 46, bar_w, 34)
    rl.draw_rectangle_rounded(bar_rect, 0.45, 8, rl.Color(14, 28, 38, 215))
    rl.draw_rectangle_rounded_lines(bar_rect, 0.45, 8, rl.Color(65, 90, 110, 160))

    ctrl_text = "[W/A/S/D]: Lăn khối  ·  [H]: AI Giải  ·  [Tab]: Đổi thuật toán  ·  [Z]: Hoàn tác  ·  [Space]: Đổi khối  ·  [R]: Chơi lại"
    text_w = measure_text_ui(ctrl_text, 13, is_bold=False)
    draw_text_ui(ctrl_text, w // 2 - text_w // 2, h - 38, 13, rl.Color(195, 225, 235, 255), is_bold=False)

    # Modal Thắng / Thua tương tác đầy đủ (chỉ hiện khi đã hoàn tất hoạt ảnh)
    if game.status in ("WON", "LOST") and not roll_animating:
        ai_move_queue.clear()
        mw, mh = 540, 204
        mrect = rl.Rectangle(w // 2 - mw // 2, h // 2 - mh // 2, mw, mh)
        rl.draw_rectangle_rounded(mrect, 0.14, 8, rl.Color(10, 22, 32, 250))

        if game.status == "WON":
            rl.draw_rectangle_rounded_lines(mrect, 0.14, 8, rl.Color(65, 245, 160, 255))
            m_glow = rl.Rectangle(w // 2 - mw // 2 - 4, h // 2 - mh // 2 - 4, mw + 8, mh + 8)
            rl.draw_rectangle_rounded(m_glow, 0.14, 8, rl.Color(65, 245, 160, 25))

            t1 = "CHIẾN THẮNG!"
            t2 = f"Chúc mừng bạn đã hoàn thành xuất sắc trong {game.moves} bước!"
            col1 = rl.Color(65, 245, 160, 255)

            # Các nút bấm trong bảng Thắng
            bw = 154
            b1 = rl.Rectangle(w // 2 - 245, h // 2 + 38, bw, 42)
            b2 = rl.Rectangle(w // 2 - 77, h // 2 + 38, bw, 42)
            b3 = rl.Rectangle(w // 2 + 91, h // 2 + 38, bw, 42)

            h1, c1 = check_button(b1)
            h2, c2 = check_button(b2)
            h3, c3 = check_button(b3)

            draw_styled_button(b1, "MÀN TIẾP (Space)", 13, h1, accent_col=rl.Color(65, 245, 160, 255))
            draw_styled_button(b2, "CHỌN MÀN", 14, h2)
            draw_styled_button(b3, "MENU CHÍNH", 14, h3)

            if c1:
                game.next_level()
                reset_camera()
                roll_animating = False
                buffered_move = None
            elif c2:
                current_state = STATE_LEVEL_SELECT
                roll_animating = False
                buffered_move = None
            elif c3:
                current_state = STATE_MENU
                roll_animating = False
                buffered_move = None

        else: # LOST
            rl.draw_rectangle_rounded_lines(mrect, 0.14, 8, rl.Color(255, 80, 85, 255))
            m_glow = rl.Rectangle(w // 2 - mw // 2 - 4, h // 2 - mh // 2 - 4, mw + 8, mh + 8)
            rl.draw_rectangle_rounded(m_glow, 0.14, 8, rl.Color(255, 80, 85, 25))

            t1 = "THẤT BẠI!"
            t2 = "Rơi khỏi sàn xuống vực thẳm!" if game.lost_reason == "FALL" else "Làm vỡ sàn cam vì dựng đứng khối!"
            col1 = rl.Color(255, 80, 85, 255)

            # Các nút bấm trong bảng Thua
            bw = 154
            b1 = rl.Rectangle(w // 2 - 245, h // 2 + 38, bw, 42)
            b2 = rl.Rectangle(w // 2 - 77, h // 2 + 38, bw, 42)
            b3 = rl.Rectangle(w // 2 + 91, h // 2 + 38, bw, 42)

            h1, c1 = check_button(b1)
            h2, c2 = check_button(b2)
            h3, c3 = check_button(b3)

            draw_styled_button(b1, "HOÀN TÁC (Z)", 14, h1, accent_col=rl.Color(0, 240, 245, 255))
            draw_styled_button(b2, "CHƠI LẠI (R)", 14, h2, accent_col=rl.Color(255, 215, 80, 255))
            draw_styled_button(b3, "MENU CHÍNH", 14, h3)

            if c1:
                if game.undo():
                    roll_animating = False
                    buffered_move = None
            elif c2:
                game.reset()
                reset_camera()
                roll_animating = False
                buffered_move = None
            elif c3:
                current_state = STATE_MENU
                roll_animating = False
                buffered_move = None

        w1 = measure_text_ui(t1, 32, is_bold=True)
        w2 = measure_text_ui(t2, 16, is_bold=False)
        draw_text_ui(t1, w // 2 - w1 // 2, h // 2 - 64, 32, col1, is_bold=True, shadow=True, glow=True)
        draw_text_ui(t2, w // 2 - w2 // 2, h // 2 - 18, 16, rl.Color(225, 240, 250, 255), is_bold=False)


# ── 10. Vòng lặp Trò chơi Chính (Main Game Loop) ───────────────
while not rl.window_should_close():
    dt = rl.get_frame_time()
    spin_timer += dt

    # ── Phím ESC: Bật/Tắt Menu nhanh ở mọi lúc ──
    if rl.is_key_pressed(rl.KEY_ESCAPE):
        ai_move_queue.clear()
        if current_state == STATE_PLAYING:
            current_state = STATE_MENU
        else:
            current_state = STATE_PLAYING

    # ── A. Xử lý Input khi ĐANG TRONG TRẬN ĐẤU (STATE_PLAYING) ──
    if current_state == STATE_PLAYING:
        # 1. Trạng thái ĐÃ CHIẾN THẮNG: người chơi nhấn phím Space, Enter hoặc N để qua màn tiếp
        if game.status == "WON" and not roll_animating:
            ai_move_queue.clear()
            if (rl.is_key_pressed(rl.KEY_SPACE) or rl.is_key_pressed(rl.KEY_ENTER) or
                rl.is_key_pressed(rl.KEY_N)):
                game.next_level()
                reset_camera()
                roll_animating = False
                buffered_move = None

        # 2. Trạng thái THẤT BẠI: phím Space/Enter/R để chơi lại, Z để hoàn tác
        elif game.status == "LOST" and not roll_animating:
            ai_move_queue.clear()
            if (rl.is_key_pressed(rl.KEY_SPACE) or rl.is_key_pressed(rl.KEY_ENTER) or
                rl.is_key_pressed(rl.KEY_R)):
                game.reset()
                reset_camera()
                roll_animating = False
                buffered_move = None
            elif rl.is_key_pressed(rl.KEY_Z) or rl.is_key_pressed(rl.KEY_BACKSPACE):
                if game.undo():
                    roll_animating = False
                    buffered_move = None

        # 3. Trạng thái ĐANG CHƠI BÌNH THƯỜNG
        else:
            target_move = None
            # Nếu người chơi tự nhấn phím lăn -> Hủy AI tự động để nhường quyền điều khiển
            if rl.is_key_pressed(rl.KEY_W) or rl.is_key_pressed(rl.KEY_UP):
                ai_move_queue.clear()
                target_move = "UP"
            elif rl.is_key_pressed(rl.KEY_S) or rl.is_key_pressed(rl.KEY_DOWN):
                ai_move_queue.clear()
                target_move = "DOWN"
            elif rl.is_key_pressed(rl.KEY_A) or rl.is_key_pressed(rl.KEY_LEFT):
                ai_move_queue.clear()
                target_move = "LEFT"
            elif rl.is_key_pressed(rl.KEY_D) or rl.is_key_pressed(rl.KEY_RIGHT):
                ai_move_queue.clear()
                target_move = "RIGHT"
            # ── [THÊM MỚI] Phím H: Kích hoạt / Tắt AI ──
            elif rl.is_key_pressed(rl.KEY_H):
                trigger_ai_solve()
            # ── [THÊM MỚI] Phím TAB: Đổi thuật toán (nếu chưa tách khối) ──
            elif rl.is_key_pressed(rl.KEY_TAB):
                if not game.is_split:
                    cycle_solver()
                else:
                    if not roll_animating:
                        game.move("SWITCH")
            elif rl.is_key_pressed(rl.KEY_SPACE):
                if game.is_split and not roll_animating:
                    game.move("SWITCH")
            elif rl.is_key_pressed(rl.KEY_Z) or rl.is_key_pressed(rl.KEY_BACKSPACE):
                ai_move_queue.clear()
                if game.undo():
                    roll_animating = False
                    buffered_move = None
            elif rl.is_key_pressed(rl.KEY_R):
                ai_move_queue.clear()
                game.reset()
                reset_camera()
                roll_animating = False
                buffered_move = None
            elif rl.is_key_pressed(rl.KEY_N):
                ai_move_queue.clear()
                game.next_level()
                reset_camera()
                roll_animating = False
                buffered_move = None
            elif rl.is_key_pressed(rl.KEY_P):
                ai_move_queue.clear()
                prev_i = (game.level_index - 1) % len(LEVELS)
                game.load_level(prev_i)
                reset_camera()
                roll_animating = False
                buffered_move = None
            elif rl.is_key_pressed(rl.KEY_C):
                reset_camera()

            if target_move:
                if not roll_animating:
                    perform_move(target_move)
                elif game.status == "PLAYING":
                    buffered_move = target_move

            # ── [THÊM MỚI] Tự động lấy bước đi từ hàng đợi AI khi khối đã lăn xong bước trước ──
            if not roll_animating and ai_move_queue and game.status == "PLAYING":
                next_ai_action = ai_move_queue.pop(0)
                if next_ai_action == "SWITCH":
                    game.move("SWITCH")
                else:
                    perform_move(next_ai_action)

        # Xoay Camera 360° bằng chuột hoặc Trackpad khi đang chơi
        if rl.is_mouse_button_down(rl.MOUSE_BUTTON_LEFT) or rl.is_mouse_button_down(rl.MOUSE_BUTTON_RIGHT):
            delta = rl.get_mouse_delta()
            target_yaw += delta.x * 0.35
            target_pitch = max(15.0, min(80.0, target_pitch - delta.y * 0.35))

        # Phím Q / E xoay góc nhìn mượt mà
        if rl.is_key_down(rl.KEY_Q):
            target_yaw -= 85.0 * dt
        if rl.is_key_down(rl.KEY_E):
            target_yaw += 85.0 * dt

        # Cuộn 2 ngón trên Trackpad để Zoom
        wheel = rl.get_mouse_wheel_move()
        if wheel != 0:
            target_dist = max(7.0, min(48.0, target_dist - wheel * 1.6))

        # Giảm chấn mượt mà (Smooth Damping Interpolation) CHỈ khi đang trong gameplay
        damping = min(1.0, dt * 14.0)
        cam_yaw += (target_yaw - cam_yaw) * damping
        cam_pitch += (target_pitch - cam_pitch) * damping
        cam_dist += (target_dist - cam_dist) * damping

    else:
        # Khi đang ở Menu / Bảng chọn màn / Hướng dẫn: Khóa Camera tĩnh tuyệt đối, chống giật rung
        default_dist = max(game.rows, game.cols) * 1.48 + 4.0
        target_yaw = -25.0
        target_pitch = 48.0
        target_dist = default_dist
        cam_yaw = -25.0
        cam_pitch = 48.0
        cam_dist = default_dist

    # ── B. Cập nhật Tọa độ Camera Orbital ──
    center_c = (game.cols - 1) / 2.0
    center_r = (game.rows - 1) / 2.0
    target_3d = rl.Vector3(center_c, 0.0, center_r)

    rad_yaw = math.radians(cam_yaw)
    rad_pitch = math.radians(cam_pitch)
    eye_x = center_c + cam_dist * math.cos(rad_pitch) * math.sin(rad_yaw)
    eye_y = cam_dist * math.sin(rad_pitch)
    eye_z = center_r + cam_dist * math.cos(rad_pitch) * math.cos(rad_yaw)

    camera.position = rl.Vector3(eye_x, eye_y, eye_z)
    camera.target = target_3d

    # ── C. Cập nhật Hoạt ảnh Lật Vật lý 3D quanh Cạnh Đáy ──
    if roll_animating:
        anim_time += dt
        p = min(1.0, anim_time / anim_duration)
        status = roll_info.get("status", "PLAYING")
        lost_reason = roll_info.get("lost_reason", None)

        if status == "LOST":
            if lost_reason == "FALL":
                if p <= 0.35:
                    e = p / 0.35
                    roll_angle = 90.0 * (e * e * (3.0 - 2.0 * e))
                    roll_y_offset = 0.0
                else:
                    p_fall = (p - 0.35) / 0.65
                    roll_angle = 90.0 + 130.0 * p_fall
                    roll_y_offset = - 22.0 * (p_fall * p_fall)
            elif lost_reason == "FRAGILE_BREAK":
                roll_angle = 0.0
                roll_y_offset = - 20.0 * (p * p)
            else: # BRIDGE_CLOSED
                roll_angle = 0.0
                roll_y_offset = - 20.0 * (p * p)
        elif status == "WON":
            if p <= 0.45:
                e = p / 0.45
                roll_angle = 90.0 * (e * e * (3.0 - 2.0 * e))
                roll_y_offset = 0.0
            else:
                roll_angle = 90.0
                p_win = (p - 0.45) / 0.55
                roll_y_offset = - 0.65 * math.sin(p_win * math.pi / 2.0)
        else: # PLAYING
            e = p * p * (3.0 - 2.0 * p)
            roll_angle = 90.0 * e
            roll_y_offset = 0.0

        if p >= 1.0:
            roll_animating = False
            roll_angle = 0.0
            roll_y_offset = 0.0

            # Kích hoạt tia lửa & bụi tiếp đất khi lăn thành công
            if game.status in ("PLAYING", "WON"):
                if not game.is_split:
                    pos, _ = get_block_target_transform()
                    if pos:
                        spawn_impact_sparks(pos.x, pos.z, count=16, is_gold=True)
                else:
                    if 0 <= game.active_block < len(game.mini_blocks):
                        mr, mc = game.mini_blocks[game.active_block]
                        spawn_impact_sparks(float(mc), float(mr), count=12, is_gold=False)

            if game.status == "PLAYING" and buffered_move is not None:
                next_m = buffered_move
                buffered_move = None
                perform_move(next_m)

    # ── D. Render Khung hình ──
    win_w = rl.get_screen_width()
    win_h = rl.get_screen_height()

    rl.begin_drawing()
    rl.clear_background(BG_COLOR)

    # 0. Vẽ Phông nền Bầu trời Vũ trụ Huyền ảo (Nebula phát quang, Sao 2D, Sao băng)
    draw_cosmic_space_backdrop(win_w, win_h, dt)

    # 1. Vẽ không gian 3D (luôn chạy nền phía sau)
    rl.begin_mode_3d(camera)
    draw_3d_scene(dt)
    rl.end_mode_3d()

    # 2. Vẽ Giao diện tương ứng với State
    if current_state == STATE_PLAYING:
        draw_cinematic_vignette(win_w, win_h)
        draw_2d_hud()
    elif current_state == STATE_MENU:
        draw_menu_screen(win_w, win_h)
    elif current_state == STATE_LEVEL_SELECT:
        draw_level_select_screen(win_w, win_h)
    elif current_state == STATE_HOW_TO_PLAY:
        draw_how_to_play_screen(win_w, win_h)

    rl.end_drawing()

rl.close_window()

