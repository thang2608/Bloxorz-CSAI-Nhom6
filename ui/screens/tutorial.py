# ui/screens/tutorial.py
"""
Bloxorz 3D - Hệ thống Hướng dẫn tương tác (Interactive Tutorial)
Bao gồm:
- 6 bản đồ mini thực hành độc lập được kiểm chứng toán học
- Giai đoạn 1: Mục tiêu & Bàn phím điều khiển (Keycap)
- Giai đoạn 2: Lưới 6 thẻ cơ chế (Thẻ bài tương tác)
- Giai đoạn 3: Bảng HUD thực hành 3D & Cô lập trạng thái (State Isolation)
"""

import math
import pyray as rl
from game import BloxorzGame
from config import (
    STATE_MENU, STATE_TUTORIAL_STAGE1, STATE_TUTORIAL_STAGE2, STATE_TUTORIAL_PRACTICE
)
from app_state import ctx
from ui.font_manager import draw_text_ui, measure_text_ui
from ui.widgets import check_button, draw_styled_button, draw_keycap, draw_star_circle
from ui.animation import get_block_target_transform
from ui.effects import spawn_impact_sparks
from audio_manager import play_sfx, notify_hover

# ── 6 Bản đồ mini thực hành tương tác (TUTORIAL_LEVELS) ─────────
TUTORIAL_LEVELS = [
    # Bài 1 — SÀN CAM DỄ VỠ
    {
        "id": 901, "name": "Sàn Cam Dễ Vỡ",
        "description": "Sàn cam chỉ chịu được khi khối nằm ngang. Đứng thẳng sẽ làm sàn vỡ!",
        "start": [2, 0],
        "board": [
            [1, 1, 3, 0, 0, 0, 0],
            [1, 1, 3, 0, 0, 0, 0],
            [1, 3, 3, 1, 1, 1, 2],
            [1, 1, 0, 0, 0, 0, 0],
        ],
        "bridges": {}, "switches": [],
    },
    # Bài 2 — CÔNG TẮC TRÒN: MỞ CẦU VĨNH VIỄN
    {
        "id": 902, "name": "Công Tắc: Mở Vĩnh Viễn",
        "description": "Công tắc tròn mở cầu vĩnh viễn. Sau khi kích hoạt lần đầu, cầu luôn mở.",
        "start": [1, 0],
        "board": [
            [0, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 0, 1, 1, 2],
            [0, 1, 1, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ],
        "bridges": {
            0: {"tiles": [[1, 3]], "initially_open": False},
        },
        "switches": [
            {"pos": [1, 2], "type": "soft", "effects": [{"action": "open", "bridge_id": 0}]},
        ],
    },
    # Bài 3 — CÔNG TẮC TRÒN: BẬT/TẮT CẦU
    {
        "id": 903, "name": "Công Tắc: Bật/Tắt Cầu",
        "description": "Mỗi lần chạm vào công tắc, trạng thái cầu sẽ luân phiên đảo ngược.",
        "start": [1, 0],
        "board": [
            [0, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 0, 1, 1, 2],
            [0, 1, 1, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ],
        "bridges": {
            0: {"tiles": [[1, 3]], "initially_open": False},
        },
        "switches": [
            {"pos": [1, 2], "type": "soft", "effects": [{"action": "toggle", "bridge_id": 0}]},
        ],
    },
    # Bài 4 — CÔNG TẮC CHỮ X (NẶNG)
    {
        "id": 904, "name": "Công Tắc Chữ X (Nặng)",
        "description": "CHỈ kích hoạt khi khối ĐỨNG THẲNG hoàn toàn trên nút chữ X.",
        "start": [1, 0],
        "board": [
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 0, 1, 1, 2],
            [1, 0, 0, 0, 0, 0, 0],
        ],
        "bridges": {
            0: {"tiles": [[2, 3]], "initially_open": False},
        },
        "switches": [
            {"pos": [2, 0], "type": "heavy", "effects": [{"action": "open", "bridge_id": 0}]},
        ],
    },
    # Bài 5 — TÁCH KHỐI (PHÂN THÂN)
    {
        "id": 905, "name": "Tách Khối (Phân Thân)",
        "description": "Đứng thẳng lên vòng tròn Cyan để tách thành 2 khối nhỏ.",
        "start": [1, 0],
        "board": [
            [0, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 2],
            [0, 0, 0, 1, 0, 1, 1, 1],
        ],
        "bridges": {
            0: {"tiles": [[2, 4]], "initially_open": False},
        },
        "switches": [
            {"pos": [1, 3], "type": "split", "split_to": [[0, 3], [2, 3]]},
            {"pos": [0, 4], "type": "soft", "effects": [{"action": "open", "bridge_id": 0}]},
        ],
    },
    # Bài 6 — HỢP NHẤT KHỐI (GỘP KHỐI)
    {
        "id": 906, "name": "Hợp Nhất Khối (Gộp)",
        "description": "Di chuyển 2 khối nhỏ đến sát cạnh nhau để tự động hợp nhất.",
        "start": [1, 0],
        "start_split": [[1, 0], [1, 5]],
        "board": [
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 2, 1, 1],
            [1, 1, 1, 1, 1, 1],
        ],
        "bridges": {}, "switches": [],
    },
]

# Thông tin 6 thẻ cơ chế (TUTORIAL_CARDS)
TUTORIAL_CARDS = [
    {"name": "Sàn Cam Dễ Vỡ",       "short": "Khối chỉ an toàn khi NẰM trên sàn cam",    "color": rl.Color(255, 140, 45, 255),  "icon": "fragile"},
    {"name": "Công Tắc: Mở Vĩnh Viễn","short": "Kích hoạt 1 lần, cầu mở mãi mãi",       "color": rl.Color(46, 225, 125, 255),  "icon": "soft_open"},
    {"name": "Công Tắc: Bật/Tắt Cầu", "short": "Mỗi lần chạm, cầu đảo trạng thái",       "color": rl.Color(0, 215, 195, 255),   "icon": "soft_toggle"},
    {"name": "Công Tắc Chữ X",        "short": "CHỈ kích hoạt khi khối ĐỨNG THẲNG",      "color": rl.Color(255, 75, 85, 255),   "icon": "heavy"},
    {"name": "Tách Khối (Phân Thân)",  "short": "Tách 1 khối thành 2, nhấn Space đổi",   "color": rl.Color(0, 230, 245, 255),   "icon": "split"},
    {"name": "Hợp Nhất (Gộp Khối)",   "short": "Di chuyển 2 khối nhỏ sát nhau để gộp",   "color": rl.Color(185, 140, 245, 255), "icon": "merge"},
]

# Gợi ý chi tiết từng bài (TUTORIAL_HINTS)
TUTORIAL_HINTS = [
    "Sàn cam chỉ chịu được khi khối nằm ngang.\nĐứng thẳng sẽ làm sàn vỡ và rơi!\nHãy điều chỉnh tư thế khối nằm ngang trước khi lăn qua.",
    "Công tắc này mở cầu vĩnh viễn.\nSau khi kích hoạt lần đầu, cầu vẫn luôn mở\ndù bạn chạm vào công tắc thêm lần nữa.",
    "Công tắc này bật và tắt cầu luân phiên.\nMỗi lần chạm vào, trạng thái cầu sẽ\nđảo ngược giữa Đóng và Mở.",
    "Công tắc chữ X đòi hỏi trọng lượng lớn:\nCHỈ kích hoạt khi khối ĐỨNG THẲNG\nhoàn toàn trên nút. Lăn vòng để đổi tư thế!",
    "Đứng thẳng lên vòng tròn Cyan để tách\nthành 2 khối nhỏ. Điều khiển Khối 1 mở cầu,\nđưa cả 2 khối qua cầu rồi chạm nhau\nđể gộp lại thành khối lớn trước khi vào đích!",
    "Di chuyển 2 khối nhỏ (dùng W/A/S/D và [Space])\nđến 2 ô nằm sát cạnh nhau (ngang hoặc dọc)\nđể tự động hợp nhất lại thành khối 1x1x2!",
]


def enter_tutorial_practice(idx):
    """Nạp bản đồ mini tutorial và cô lập trạng thái khỏi màn chơi chính"""
    ctx.current_tutorial_idx = idx
    ctx.show_tutorial_hint = False

    # Snapshot game chính nếu chưa lưu và game hiện tại không phải tutorial_game
    if ctx.main_game_snapshot is None and (ctx.tutorial_game is None or ctx.game is not ctx.tutorial_game):
        ctx.main_game_snapshot = ctx.game
        ctx.main_game_camera = (ctx.cam_yaw, ctx.cam_pitch, ctx.cam_dist)

    ctx.tutorial_game = BloxorzGame(0)
    ctx.tutorial_game.load_level(TUTORIAL_LEVELS[idx])
    ctx.game = ctx.tutorial_game

    ctx.roll_animating = False
    ctx.buffered_move = None
    ctx.roll_angle = 0.0
    ctx.roll_y_offset = 0.0
    ctx.ai_move_queue.clear()
    ctx.reset_camera()

    ctx.current_state = STATE_TUTORIAL_PRACTICE


def exit_tutorial_practice():
    """Khôi phục game chính khi thoát khỏi tutorial practice"""
    if ctx.main_game_snapshot is not None:
        ctx.game = ctx.main_game_snapshot
        ctx.main_game_snapshot = None
        if ctx.main_game_camera is not None:
            cy, cp, cd = ctx.main_game_camera
            ctx.cam_yaw, ctx.cam_pitch, ctx.cam_dist = cy, cp, cd
            ctx.target_yaw, ctx.target_pitch, ctx.target_dist = cy, cp, cd
            ctx.main_game_camera = None

    ctx.roll_animating = False
    ctx.buffered_move = None
    ctx.roll_angle = 0.0
    ctx.roll_y_offset = 0.0
    ctx.ai_move_queue.clear()
    ctx.reset_camera()


def draw_tutorial_stage1(w, h):
    """Giai đoạn 1: Mục tiêu + Điều khiển (Keycap)"""
    rl.draw_rectangle(0, 0, w, h, rl.Color(8, 16, 22, 235))

    pw, ph = min(840, w - 40), min(650, h - 30)
    px = w // 2 - pw // 2
    py = h // 2 - ph // 2 - 8

    panel = rl.Rectangle(px, py, pw, ph)
    rl.draw_rectangle_rounded(panel, 0.08, 8, rl.Color(12, 24, 34, 252))
    rl.draw_rectangle_rounded_lines(panel, 0.08, 8, rl.Color(255, 195, 80, 160))

    title = "HƯỚNG DẪN LUẬT CHƠI BLOXORZ"
    wt = measure_text_ui(title, 26, is_bold=True)
    draw_text_ui(title, w // 2 - wt // 2, py + 18, 26, rl.Color(255, 215, 80, 255), is_bold=True, shadow=True, glow=True)

    # ── A. MỤC TIÊU ──
    sec_a_y = py + 62
    draw_text_ui("A. MỤC TIÊU", px + 34, sec_a_y, 18, rl.Color(0, 240, 245, 255), is_bold=True, shadow=True)
    obj_text = "Lăn khối hộp 1x1x2 đến đúng ô đích màu xanh neon. Khối phải đứng thẳng hoàn toàn trên ô đích để chiến thắng."
    draw_text_ui(obj_text, px + 34, sec_a_y + 26, 14, rl.Color(210, 230, 240, 255))

    # Minh họa trực quan: Khối 1x1x2 đứng cạnh ô đích phát sáng màu xanh neon
    illust_x = px + 34
    illust_y = sec_a_y + 54
    # Ô sàn thường
    rl.draw_rectangle(illust_x, illust_y + 26, 40, 20, rl.Color(76, 100, 116, 255))
    rl.draw_rectangle_lines(illust_x, illust_y + 26, 40, 20, rl.Color(40, 58, 72, 255))
    # Khối 1x1x2 Bloxorz đặt đứng trên sàn
    rl.draw_rectangle(illust_x + 5, illust_y - 18, 30, 44, rl.Color(240, 140, 30, 255))
    rl.draw_rectangle_lines(illust_x + 5, illust_y - 18, 30, 44, rl.Color(255, 215, 120, 240))
    # Vạch chia 2 nửa khối 1x1x1
    rl.draw_line(illust_x + 5, illust_y + 4, illust_x + 35, illust_y + 4, rl.Color(200, 95, 15, 220))
    draw_text_ui("Khối Bloxorz 1x1x2 (Đứng thẳng)", illust_x + 48, illust_y + 2, 13, rl.Color(255, 215, 120, 255), is_bold=True)

    # Ô đích phát sáng màu xanh neon
    goal_x = illust_x + 340
    pulse_a = int(185 + 70 * math.sin(ctx.spin_timer * 4.5))
    # Ô sàn đích
    rl.draw_rectangle(goal_x, illust_y + 26, 40, 20, rl.Color(6, 12, 18, 255))
    rl.draw_rectangle_lines(goal_x, illust_y + 26, 40, 20, rl.Color(0, 245, 255, pulse_a))
    rl.draw_rectangle(goal_x + 6, illust_y + 29, 28, 14, rl.Color(0, 220, 240, int(60 + 40 * math.sin(ctx.spin_timer * 4.5))))
    rl.draw_rectangle_lines(goal_x + 6, illust_y + 29, 28, 14, rl.Color(0, 255, 255, pulse_a))
    draw_text_ui("Ô đích màu Xanh Neon (Chiến thắng)", goal_x + 48, illust_y + 26, 13, rl.Color(0, 240, 245, 255), is_bold=True)

    # ── B. ĐIỀU KHIỂN ──
    sec_b_y = illust_y + 60
    draw_text_ui("B. ĐIỀU KHIỂN", px + 34, sec_b_y, 18, rl.Color(0, 240, 245, 255), is_bold=True, shadow=True)

    kx_base = px + 38
    ky = sec_b_y + 28
    kw, kh = 38, 30
    gap = 6
    desc_offset = 186

    controls = [
        (["W", "/", "↑"],  "Lăn khối lên trên (UP)"),
        (["S", "/", "↓"],  "Lăn khối xuống dưới (DOWN)"),
        (["A", "/", "←"],  "Lăn khối sang trái (LEFT)"),
        (["D", "/", "→"],  "Lăn khối sang phải (RIGHT)"),
    ]
    for keys, desc in controls:
        kx = kx_base
        for k in keys:
            if k == "/":
                draw_text_ui("/", kx + 4, ky + 6, 14, rl.Color(130, 155, 170, 180))
                kx += 18
            else:
                draw_keycap(kx, ky, kw, kh, k)
                kx += kw + gap
        draw_text_ui(desc, kx_base + desc_offset, ky + 7, 13, rl.Color(210, 230, 240, 255))
        ky += kh + 6

    # Xoay camera
    draw_text_ui("Kéo chuột", kx_base, ky + 7, 13, rl.Color(0, 235, 245, 220), is_bold=True)
    draw_text_ui("hoặc", kx_base + 72, ky + 7, 13, rl.Color(150, 180, 195, 200))
    kx_cam = kx_base + 110
    for k in ["Q", "E"]:
        draw_keycap(kx_cam, ky, kw, kh, k)
        kx_cam += kw + gap
    draw_text_ui("& Cuộn chuột: Xoay góc nhìn 3D 360 độ & thu phóng camera", kx_cam + 4, ky + 7, 13, rl.Color(210, 230, 240, 255))
    ky += kh + 6

    # Phím Space, Z, R
    extra = [
        ("Space", "Đổi khối điều khiển khi đang ở trạng thái phân thân (is_split)"),
        ("Z / Backspace", "Hoàn tác bước đi trước đó (undo)"),
        ("R", "Chơi lại màn hiện tại (reset)"),
    ]
    for key_label, desc in extra:
        kw_sp = max(kw, measure_text_ui(key_label, 13, is_bold=True) + 18)
        draw_keycap(kx_base, ky, kw_sp, kh, key_label, font_size=12 if len(key_label) > 6 else 13)
        draw_text_ui(desc, kx_base + desc_offset, ky + 7, 13, rl.Color(210, 230, 240, 255))
        ky += kh + 6

    # ── Nút điều hướng Giai đoạn 1 ──
    btn_w_nav = 180
    btn_back_rec = rl.Rectangle(w // 2 - btn_w_nav - 20, py + ph - 54, btn_w_nav, 42)
    btn_next_rec = rl.Rectangle(w // 2 + 20, py + ph - 54, btn_w_nav, 42)

    h_back, c_back = check_button(btn_back_rec)
    if h_back:
        notify_hover("tut_s1_back")
    draw_styled_button(btn_back_rec, "< QUAY LẠI", 16, h_back)
    if c_back:
        play_sfx("ui_back")
        ctx.current_state = STATE_MENU

    h_next, c_next = check_button(btn_next_rec)
    if h_next:
        notify_hover("tut_s1_next")
    draw_styled_button(btn_next_rec, "TIẾP TỤC >", 16, h_next, accent_col=rl.Color(65, 245, 160, 255))
    if c_next:
        play_sfx("ui_select")
        ctx.current_state = STATE_TUTORIAL_STAGE2


def draw_tutorial_card_icon(cx, cy, icon_type, accent_col, t):
    """Vẽ icon minh họa đặc trưng cho mỗi cơ chế tutorial"""
    ar = getattr(accent_col, 'r', 255)
    ag = getattr(accent_col, 'g', 255)
    ab = getattr(accent_col, 'b', 255)
    pulse = 0.7 + 0.3 * math.sin(t * 3.5)
    alpha = int(220 * pulse)
    col = rl.Color(ar, ag, ab, alpha)
    col_dim = rl.Color(ar, ag, ab, int(130 * pulse))

    if icon_type == "fragile":
        rl.draw_rectangle(cx, cy + 2, 26, 14, rl.Color(245, 115, 30, 220))
        rl.draw_rectangle_lines(cx, cy + 2, 26, 14, col)
        rl.draw_line(cx + 6, cy + 4, cx + 20, cy + 14, col_dim)
        rl.draw_line(cx + 8, cy + 14, cx + 18, cy + 4, col_dim)
    elif icon_type == "soft_open":
        draw_star_circle(cx + 13, cy + 9, 9.0, col)
        draw_star_circle(cx + 13, cy + 9, 4.5, col_dim)
    elif icon_type == "soft_toggle":
        draw_star_circle(cx + 13, cy + 9, 9.0, col)
        rl.draw_circle_lines(cx + 13, cy + 9, 12.0, col_dim)
    elif icon_type == "heavy":
        rl.draw_line(cx + 4, cy + 2, cx + 22, cy + 16, col)
        rl.draw_line(cx + 22, cy + 2, cx + 4, cy + 16, col)
        rl.draw_rectangle_lines(cx + 1, cy, 24, 18, col_dim)
    elif icon_type == "split":
        rl.draw_rectangle(cx + 1, cy + 3, 10, 11, col)
        rl.draw_rectangle(cx + 15, cy + 3, 10, 11, col_dim)
    elif icon_type == "merge":
        rl.draw_rectangle(cx + 1, cy + 3, 10, 11, col_dim)
        rl.draw_rectangle(cx + 15, cy + 3, 10, 11, col_dim)
        rl.draw_line(cx + 11, cy + 8, cx + 15, cy + 8, col)


def draw_tutorial_stage2(w, h):
    """Giai đoạn 2: Lưới 6 thẻ cơ chế tương tác (3 cột x 2 hàng)"""
    rl.draw_rectangle(0, 0, w, h, rl.Color(8, 16, 22, 235))

    # Tiêu đề
    title = "TÌM HIỂU CÁC CƠ CHẾ"
    wt = measure_text_ui(title, 30, is_bold=True)
    draw_text_ui(title, w // 2 - wt // 2, 32, 30, rl.Color(255, 215, 80, 255), is_bold=True, shadow=True, glow=True)

    sub = "Chọn một cơ chế để tìm hiểu luật và trực tiếp điều khiển khối trên bản đồ mini"
    ws = measure_text_ui(sub, 14)
    draw_text_ui(sub, w // 2 - ws // 2, 70, 14, rl.Color(0, 235, 245, 220))

    # Lưới 3 cột x 2 hàng
    n_cols = 3
    card_w = min(290, (w - 80) // 3)
    card_h = 130
    gap_x = 20
    gap_y = 20
    total_w = n_cols * card_w + (n_cols - 1) * gap_x
    start_x = w // 2 - total_w // 2
    start_y = 110

    for i, card_info in enumerate(TUTORIAL_CARDS):
        col_idx = i % n_cols
        row_idx = i // n_cols
        cx = start_x + col_idx * (card_w + gap_x)
        cy = start_y + row_idx * (card_h + gap_y)

        crec = rl.Rectangle(cx, cy, card_w, card_h)
        hover, clicked = check_button(crec)
        accent = card_info["color"]
        ar = getattr(accent, 'r', 255)
        ag = getattr(accent, 'g', 255)
        ab = getattr(accent, 'b', 255)

        is_done = (i in ctx.completed_tutorials)

        if hover:
            bg = rl.Color(28, 50, 68, 250)
            border = accent
            glow_rec = rl.Rectangle(cx - 3, cy - 3, card_w + 6, card_h + 6)
            rl.draw_rectangle_rounded(glow_rec, 0.14, 8, rl.Color(ar, ag, ab, 45))
        else:
            bg = rl.Color(16, 32, 44, 230)
            border = rl.Color(ar, ag, ab, 140) if is_done else rl.Color(65, 90, 110, 180)

        rl.draw_rectangle_rounded(crec, 0.14, 8, bg)
        rl.draw_rectangle_rounded_lines(crec, 0.14, 8, border)

        # Highlight trên
        hl = rl.Rectangle(cx + 2, cy + 2, card_w - 4, card_h * 0.35)
        rl.draw_rectangle_rounded(hl, 0.14, 8, rl.Color(255, 255, 255, 10))

        # Icon
        draw_tutorial_card_icon(cx + 14, cy + 14, card_info["icon"], accent, ctx.spin_timer)

        # Tên + mô tả
        draw_text_ui(f"BÀI {i+1}: {card_info['name']}", cx + 46, cy + 14, 14, accent, is_bold=True, shadow=True)
        draw_text_ui(card_info["short"], cx + 14, cy + 44, 12, rl.Color(210, 230, 240, 240))

        # Badge trạng thái
        if is_done:
            badge_text = "ĐÃ HOÀN THÀNH"
            badge_col = rl.Color(65, 245, 120, 255)

            badge_bg = rl.Color(40, 120, 70, 70)
        else:
            badge_text = "THỰC HÀNH NGAY"
            badge_col = rl.Color(ar, ag, ab, 235)
            badge_bg = rl.Color(ar, ag, ab, 35)

        bw_badge = measure_text_ui(badge_text, 12, is_bold=True)
        badge_rec = rl.Rectangle(cx + card_w - bw_badge - 24, cy + card_h - 32, bw_badge + 16, 22)
        rl.draw_rectangle_rounded(badge_rec, 0.40, 6, badge_bg)
        rl.draw_rectangle_rounded_lines(badge_rec, 0.40, 6, badge_col)
        draw_text_ui(badge_text, int(badge_rec.x + 8), int(badge_rec.y + 4), 12, badge_col, is_bold=True)

        if hover:
            notify_hover(f"tut_s2_card_{i}")

        if clicked:
            play_sfx("ui_select")
            enter_tutorial_practice(i)
            return

    # Nút quay lại Stage 1
    btn_back = rl.Rectangle(w // 2 - 220, h - 58, 200, 42)
    h_b, c_b = check_button(btn_back)
    if h_b:
        notify_hover("tut_s2_back")
    draw_styled_button(btn_back, "< QUAY LẠI", 16, h_b)
    if c_b:
        play_sfx("ui_back")
        ctx.current_state = STATE_TUTORIAL_STAGE1

    # Nút về Menu chính
    btn_menu = rl.Rectangle(w // 2 + 20, h - 58, 200, 42)
    h_m, c_m = check_button(btn_menu)
    if h_m:
        notify_hover("tut_s2_menu")
    draw_styled_button(btn_menu, "VỀ MENU CHÍNH", 16, h_m)
    if c_m:
        play_sfx("ui_back")
        ctx.current_state = STATE_MENU


def draw_tutorial_practice_hud(w, h):
    """HUD khi đang thực hành bản đồ mini 3D (TUYỆT ĐỐI KHÔNG vẽ overlay tối toàn màn hình)"""
    idx = ctx.current_tutorial_idx
    card = TUTORIAL_CARDS[idx]
    accent = card["color"]
    ar = getattr(accent, 'r', 255)
    ag = getattr(accent, 'g', 255)
    ab = getattr(accent, 'b', 255)
    game = ctx.game

    # ── 1. Panel thông tin bài học (Góc trên bên trái) ──
    info_w = min(540, w - 200)
    info_h = 116
    info_rec = rl.Rectangle(14, 14, info_w, info_h)
    rl.draw_rectangle_rounded(info_rec, 0.14, 8, rl.Color(10, 22, 32, 235))
    rl.draw_rectangle_rounded_lines(info_rec, 0.14, 8, rl.Color(ar, ag, ab, 175))
    hl = rl.Rectangle(16, 16, info_w - 4, info_h * 0.35)
    rl.draw_rectangle_rounded(hl, 0.14, 8, rl.Color(255, 255, 255, 8))

    avail_w = info_w - 24

    lesson_title = f"BÀI {idx + 1}/6: {card['name'].upper()}"
    title_sz = 17
    while measure_text_ui(lesson_title, title_sz, is_bold=True) > avail_w and title_sz > 12:
        title_sz -= 1
    draw_text_ui(lesson_title, 26, 22, title_sz, accent, is_bold=True, shadow=True, glow=True, glow_color=rl.Color(ar, ag, ab, 45))

    desc = TUTORIAL_LEVELS[idx].get("description", "")
    desc_sz = 13
    while measure_text_ui(desc, desc_sz, is_bold=False) > avail_w and desc_sz > 10:
        desc_sz -= 1
    draw_text_ui(desc, 26, 46, desc_sz, rl.Color(210, 230, 240, 240))

    # Trạng thái trực tiếp theo thời gian thực (tự động căn chỉnh vừa vặn tuyệt đối)
    status_y = 68
    st_text = ""
    st_col = rl.Color(255, 255, 255, 255)
    st_glow = False

    if idx == 0:  # Bài 1 — Sàn cam dễ vỡ
        if not game.is_split:
            if game.block.is_standing():
                st_text = "Tư thế: ĐỨNG THẲNG — Sẽ làm vỡ sàn cam!"
                st_col = rl.Color(255, 95, 60, 255)
            else:
                st_text = "Tư thế: NẰM — An toàn khi lăn qua sàn cam!"
                st_col = rl.Color(65, 245, 160, 255)
    elif idx in (1, 2):  # Bài 2, 3 — Cầu & công tắc tròn
        has_bridge = bool(game.bridges)
        if has_bridge:
            bridge_open = any(b["is_open"] for b in game.bridges.values())
            if bridge_open:
                st_text = "TRẠNG THÁI CẦU: ĐANG MỞ"
                if idx == 1:
                    st_text += " (Vĩnh viễn)"
                st_col = rl.Color(65, 245, 160, 255)
            else:
                st_text = "TRẠNG THÁI CẦU: ĐANG ĐÓNG"
                st_col = rl.Color(255, 80, 85, 255)
            st_glow = True
    elif idx == 3:  # Bài 4 — Công tắc chữ X
        bridge_open = any(b["is_open"] for b in game.bridges.values()) if game.bridges else False
        if bridge_open:
            st_text = "CÔNG TẮC X: ĐÃ KÍCH HOẠT — CẦU ĐANG MỞ!"
            st_col = rl.Color(65, 245, 160, 255)
        else:
            is_on_switch = (not game.is_split and (2, 0) in game.block.state)
            if is_on_switch and not game.block.is_standing():
                st_text = "Chưa đủ lực! Công tắc X chỉ nhận khi khối ĐỨNG THẲNG."
                st_col = rl.Color(255, 195, 50, 255)
            else:
                st_text = "TRẠNG THÁI CẦU: ĐANG ĐÓNG (Cần đứng thẳng trên ô X)"
                st_col = rl.Color(255, 80, 85, 255)
    elif idx == 4:  # Bài 5 — Tách khối
        if game.is_split:
            st_text = f"PHÂN THÂN (Khối {game.active_block + 1})  ·  Đưa 2 khối qua cầu chạm nhau để gộp!"
            st_col = rl.Color(0, 230, 245, 255)
        else:
            st_text = "Lăn khối ĐỨNG THẲNG vào vòng tròn Cyan để tách thành 2 khối nhỏ"
            st_col = rl.Color(255, 215, 80, 255)
    elif idx == 5:  # Bài 6 — Hợp nhất khối
        if game.is_split:
            st_text = f"PHÂN THÂN (Khối {game.active_block + 1})  ·  Di chuyển 2 khối lại gần nhau để gộp!"
            st_col = rl.Color(185, 140, 245, 255)
        else:
            st_text = "ĐÃ GỘP KHỐI THÀNH CÔNG! Lăn khối lớn vào ô đích!"
            st_col = rl.Color(65, 245, 160, 255)

    if st_text:
        st_sz = 14 if idx in (1, 2) else 13
        while measure_text_ui(st_text, st_sz, is_bold=True) > avail_w and st_sz > 10:
            st_sz -= 1
        draw_text_ui(st_text, 26, status_y, st_sz, st_col, is_bold=True, glow=st_glow)

    draw_text_ui(f"BƯỚC: {game.moves}", 26, status_y + 22, 14, rl.Color(0, 240, 245, 255), is_bold=True)

    # ── 2. Cụm nút chức năng góc trên bên phải ──
    btn_hint = rl.Rectangle(w - 170, 14, 155, 36)
    h_hint, c_hint = check_button(btn_hint)
    if h_hint:
        notify_hover("tut_prac_hint")
    hint_label = "ẨN GỢI Ý (H)" if ctx.show_tutorial_hint else "GỢI Ý (H)"
    draw_styled_button(btn_hint, hint_label, 14, h_hint, active=ctx.show_tutorial_hint, accent_col=rl.Color(255, 195, 80, 255))
    if c_hint:
        play_sfx("ui_select")
        ctx.show_tutorial_hint = not ctx.show_tutorial_hint

    btn_reset = rl.Rectangle(w - 170, 56, 155, 36)
    h_rs, c_rs = check_button(btn_reset)
    if h_rs:
        notify_hover("tut_prac_reset")
    draw_styled_button(btn_reset, "CHƠI LẠI (R)", 14, h_rs)
    if c_rs:
        game.reset()
        play_sfx("reset")
        ctx.reset_camera()
        ctx.roll_animating = False
        ctx.buffered_move = None

    # Popup Gợi ý
    if ctx.show_tutorial_hint:
        hint_text = TUTORIAL_HINTS[idx]
        hint_lines = hint_text.split("\n")
        popup_h = 28 + len(hint_lines) * 20
        popup_w = 380
        popup_rec = rl.Rectangle(w - popup_w - 16, 100, popup_w, popup_h)
        rl.draw_rectangle_rounded(popup_rec, 0.12, 8, rl.Color(14, 32, 48, 250))
        rl.draw_rectangle_rounded_lines(popup_rec, 0.12, 8, rl.Color(255, 195, 80, 220))
        draw_text_ui("MẸO VƯỢT BÀI:", int(popup_rec.x) + 14, int(popup_rec.y) + 8, 14, rl.Color(255, 195, 80, 255), is_bold=True)
        ly = int(popup_rec.y) + 30
        for line in hint_lines:
            draw_text_ui(line, int(popup_rec.x) + 14, ly, 13, rl.Color(215, 235, 245, 240))
            ly += 20

    # ── 3. Thanh dưới: Nút quay về danh sách ──
    bar_w = min(w - 40, 620)
    bar_rect = rl.Rectangle(w // 2 - bar_w // 2, h - 50, bar_w, 38)
    rl.draw_rectangle_rounded(bar_rect, 0.40, 8, rl.Color(12, 24, 36, 225))
    rl.draw_rectangle_rounded_lines(bar_rect, 0.40, 8, rl.Color(65, 90, 110, 160))

    btn_back_list = rl.Rectangle(w // 2 - bar_w // 2 + 10, h - 46, 225, 30)
    h_bl, c_bl = check_button(btn_back_list)
    draw_styled_button(btn_back_list, "< DANH SÁCH CƠ CHẾ (ESC)", 13, h_bl)
    if c_bl:
        exit_tutorial_practice()
        ctx.current_state = STATE_TUTORIAL_STAGE2

    ctrl_hint = "[W/A/S/D]: Lăn khối  ·  [Space]: Đổi khối  ·  [Z]: Hoàn tác"
    ctl_w = measure_text_ui(ctrl_hint, 12)
    draw_text_ui(ctrl_hint, w // 2 + bar_w // 2 - ctl_w - 14, h - 39, 12, rl.Color(185, 210, 225, 220))

    # ── 4. Modal Thắng / Thua ──
    if game.status in ("WON", "LOST") and not ctx.roll_animating:
        mw, mh = 540, 215
        mrect = rl.Rectangle(w // 2 - mw // 2, h // 2 - mh // 2, mw, mh)
        rl.draw_rectangle_rounded(mrect, 0.14, 8, rl.Color(10, 22, 32, 252))

        if game.status == "WON":
            if idx not in ctx.completed_tutorials:
                ctx.completed_tutorials.add(idx)
                pos, _ = get_block_target_transform()
                if pos:
                    spawn_impact_sparks(pos.x, pos.z, count=28, is_gold=True)

            rl.draw_rectangle_rounded_lines(mrect, 0.14, 8, rl.Color(65, 245, 160, 255))
            glow_r = rl.Rectangle(w // 2 - mw // 2 - 4, h // 2 - mh // 2 - 4, mw + 8, mh + 8)
            rl.draw_rectangle_rounded(glow_r, 0.14, 8, rl.Color(65, 245, 160, 25))

            t1 = "HOÀN THÀNH CƠ CHẾ!"
            t2 = f"Bạn đã nắm vững: {card['name']} trong {game.moves} bước!"
            col1 = rl.Color(65, 245, 160, 255)

            bw_btn = 152
            b1 = rl.Rectangle(w // 2 - 245, h // 2 + 40, bw_btn, 42)
            b2 = rl.Rectangle(w // 2 - 76, h // 2 + 40, bw_btn, 42)
            b3 = rl.Rectangle(w // 2 + 93, h // 2 + 40, bw_btn, 42)

            h1, c1 = check_button(b1)
            h2, c2 = check_button(b2)
            h3, c3 = check_button(b3)

            if h1: notify_hover("tut_won_b1")
            elif h2: notify_hover("tut_won_b2")
            elif h3: notify_hover("tut_won_b3")

            draw_styled_button(b1, "CHƠI LẠI BÀI NÀY", 12, h1, accent_col=rl.Color(255, 215, 80, 255))
            next_label = "BÀI TIẾP THEO >" if idx < 5 else "VỀ DANH SÁCH"
            draw_styled_button(b2, next_label, 13, h2, accent_col=rl.Color(65, 245, 160, 255))
            draw_styled_button(b3, "VỀ DANH SÁCH", 13, h3)

            if c1:
                game.reset()
                play_sfx("reset")
                ctx.reset_camera()
                ctx.roll_animating = False
                ctx.buffered_move = None
            elif c2:
                play_sfx("ui_select")
                if idx < 5:
                    enter_tutorial_practice(idx + 1)
                else:
                    exit_tutorial_practice()
                    ctx.current_state = STATE_TUTORIAL_STAGE2
                return
            elif c3:
                play_sfx("ui_back")
                exit_tutorial_practice()
                ctx.current_state = STATE_TUTORIAL_STAGE2
                return

        else:  # LOST
            rl.draw_rectangle_rounded_lines(mrect, 0.14, 8, rl.Color(255, 80, 85, 255))
            glow_r = rl.Rectangle(w // 2 - mw // 2 - 4, h // 2 - mh // 2 - 4, mw + 8, mh + 8)
            rl.draw_rectangle_rounded(glow_r, 0.14, 8, rl.Color(255, 80, 85, 25))

            if game.lost_reason == "FRAGILE_BREAK":
                t1 = "SÀN CAM ĐÃ BỊ VỠ!"
                t2 = "Sàn cam đã bị vỡ vì khối đứng thẳng!"
            elif game.lost_reason == "BRIDGE_CLOSED":
                t1 = "CẦU ĐÃ ĐÓNG!"
                t2 = "Cầu nối bị đóng ngay dưới chân khối!"
            else:
                t1 = "RƠI XUỐNG VỰC!"
                t2 = "Khối đã rơi khỏi sàn xuống vực thẳm!"
            col1 = rl.Color(255, 80, 85, 255)

            bw_btn = 155
            b1 = rl.Rectangle(w // 2 - 165, h // 2 + 40, bw_btn, 42)
            b2 = rl.Rectangle(w // 2 + 10, h // 2 + 40, bw_btn, 42)

            h1, c1 = check_button(b1)
            h2, c2 = check_button(b2)

            if h1: notify_hover("tut_lost_b1")
            elif h2: notify_hover("tut_lost_b2")

            draw_styled_button(b1, "HOÀN TÁC (Z)", 14, h1, accent_col=rl.Color(0, 240, 245, 255))
            draw_styled_button(b2, "THỬ LẠI (R)", 14, h2, accent_col=rl.Color(255, 215, 80, 255))

            if c1:
                if game.undo():
                    play_sfx("undo")
                    ctx.roll_animating = False
                    ctx.buffered_move = None
            elif c2:
                game.reset()
                play_sfx("reset")
                ctx.reset_camera()
                ctx.roll_animating = False
                ctx.buffered_move = None

        w1 = measure_text_ui(t1, 28, is_bold=True)
        w2 = measure_text_ui(t2, 15)
        draw_text_ui(t1, w // 2 - w1 // 2, h // 2 - 58, 28, col1, is_bold=True, shadow=True, glow=True)
        draw_text_ui(t2, w // 2 - w2 // 2, h // 2 - 18, 15, rl.Color(225, 240, 250, 255))
