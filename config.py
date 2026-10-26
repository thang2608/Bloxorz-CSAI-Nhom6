# config.py — Hằng số cấu hình, Bảng màu Theme và State Enums
try:
    import pyray as rl
except ImportError:
    from raylib import pyray as rl

# Kích thước cửa sổ
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 740
TARGET_FPS = 60

# Các trạng thái màn hình (Game State Machine)
STATE_MENU = 0
STATE_LEVEL_SELECT = 1
STATE_HOW_TO_PLAY = 2
STATE_PLAYING = 3
STATE_TUTORIAL_STAGE1 = 4   # Giai đoạn 1: Mục tiêu + Điều khiển
STATE_TUTORIAL_STAGE2 = 5   # Giai đoạn 2: Lưới 6 thẻ cơ chế
STATE_TUTORIAL_PRACTICE = 6 # Đang thực hành bản đồ mini 3D

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

# Bảng mã ký tự ASCII + Tiếng Việt có dấu đầy đủ
chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 `~!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?")
vn_chars = "aáàảãạăắằẳẵặâấầẩẫậeéèẻẽẹêếềểễệiíìỉĩịoóòỏõọôốồổỗộơớờởỡợuúùủũụưứừửữựyýỳỷỹỵdđ"
vn_chars += vn_chars.upper()
chars.update(vn_chars)
chars.update("·–—•+-/()▼▲✓↑↓←→")
VIETNAMESE_CODEPOINTS = sorted(list(set(ord(c) for c in chars)))

# Bảng màu Sang trọng (Cyber-Slate & Imperial Gold)
BG_COLOR = rl.Color(5, 10, 16, 255)
CYBER_BG = rl.Color(12, 22, 32, 255)
GOLD_ACCENT = rl.Color(255, 215, 80, 255)
ACCENT_CYAN = rl.Color(0, 240, 245, 255)

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

BLOCK_COLOR = rl.Color(240, 140, 30, 255)
BLOCK_WIRE = rl.Color(255, 205, 110, 240)

# Khối phân thân
MINI_ACTIVE = rl.Color(255, 195, 45, 255)
MINI_ACTIVE_WIRE = rl.Color(255, 240, 160, 255)
MINI_IDLE = rl.Color(240, 140, 30, 255)
MINI_IDLE_WIRE = rl.Color(255, 205, 110, 240)

# Công tắc (Switches)
SWITCH_SOFT_COL = rl.Color(46, 225, 125, 255)
SWITCH_HEAVY_COL = rl.Color(255, 75, 85, 255)
SWITCH_SPLIT_COL = rl.Color(0, 230, 245, 255)
