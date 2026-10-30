# ui/screens/menu_screen.py
"""
Bloxorz 3D - Giao diện Màn hình Menu chính (DELUXE SPLIT-LAYOUT EDITION)
Bố cục chia đôi: Trái = Thương hiệu & Nút điều hướng | Phải = Khối 3D xoay trưng bày & Bộ chọn 4 Skin 3D.
Hỗ trợ điều hướng song song Bàn phím (↑/↓/W/S + Enter/Space + Phím B đổi Skin + F11 Toàn màn hình) & Chuột.
"""

import sys
import math
try:
    import pyray as rl
except ImportError:
    from raylib import pyray as rl

from config import (
    STATE_PLAYING, STATE_LEVEL_SELECT, STATE_TUTORIAL_STAGE1,
    BLOCK_COLOR, BLOCK_WIRE, LEVEL_NAMES_VI,
    BLOCK_SKINS, get_skin_accent_color
)
from app_state import ctx
from ui.font_manager import draw_text_ui, measure_text_ui
from ui.widgets import draw_styled_button, check_button
from audio_manager import play_sfx, toggle_bgm, is_bgm_enabled, notify_hover

# ── Biến trạng thái điều hướng Menu ──
menu_selected_idx = 0          # Nút đang được chọn (0..3)
_last_input_was_keyboard = False  # Theo dõi nguồn input cuối cùng


def _check_button_menu(rec, btn_index):
    """
    Kiểm tra hover/click chuột cho nút menu, kết hợp cơ chế chống xung đột
    với bàn phím. Chỉ cập nhật menu_selected_idx khi chuột THỰC SỰ di chuyển.
    """
    global menu_selected_idx, _last_input_was_keyboard
    mp = rl.get_mouse_position()
    hover = rl.check_collision_point_rec(mp, rec)

    # Chỉ cập nhật chỉ mục khi chuột CÓ di chuyển (tránh kẹt khi chuột đứng yên)
    if hover:
        mouse_delta = rl.get_mouse_delta()
        if abs(mouse_delta.x) > 0.1 or abs(mouse_delta.y) > 0.1:
            menu_selected_idx = btn_index
            _last_input_was_keyboard = False
        notify_hover(f"menu_item_{btn_index}")

    clicked = hover and rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT)
    if clicked:
        menu_selected_idx = btn_index
        _last_input_was_keyboard = False

    return clicked


def _handle_keyboard_navigation():
    """Xử lý phím ↑/↓/W/S để di chuyển vệt chọn, Enter/Space để kích hoạt."""
    global menu_selected_idx, _last_input_was_keyboard

    navigated = False
    if rl.is_key_pressed(rl.KEY_UP) or rl.is_key_pressed(rl.KEY_W):
        menu_selected_idx = (menu_selected_idx - 1) % 4
        _last_input_was_keyboard = True
        navigated = True
    elif rl.is_key_pressed(rl.KEY_DOWN) or rl.is_key_pressed(rl.KEY_S):
        menu_selected_idx = (menu_selected_idx + 1) % 4
        _last_input_was_keyboard = True
        navigated = True

    confirmed = (
        rl.is_key_pressed(rl.KEY_ENTER)
        or rl.is_key_pressed(rl.KEY_KP_ENTER)
        or rl.is_key_pressed(rl.KEY_SPACE)
    )
    if navigated:
        play_sfx("ui_nav")
    return navigated, confirmed


def _activate_menu_action(idx):
    """Kích hoạt hành động tương ứng với nút menu tại chỉ mục idx."""
    play_sfx("ui_select")
    if idx == 0:
        ctx.current_state = STATE_PLAYING
    elif idx == 1:
        ctx.current_state = STATE_LEVEL_SELECT
    elif idx == 2:
        ctx.current_state = STATE_TUTORIAL_STAGE1
    elif idx == 3:
        rl.close_window()
        sys.exit(0)


def draw_menu_3d_showcase(dt):
    """
    Vẽ khối Bloxorz 3D trưng bày xoay lơ lửng trên bệ năng lượng Sci-Fi.
    Được gọi bên trong rl.begin_mode_3d(camera) khi ở STATE_MENU.
    """
    from ui.effects import draw_starfield
    from ui.render3d import draw_deluxe_block

    # Vẫn giữ bầu trời sao vũ trụ
    draw_starfield()

    t = ctx.spin_timer

    # ── Khối 3D Trưng bày (Rotating Hero Block) ──
    bob_y = math.sin(t * 2.0) * 0.22   # Bay lơ lửng Zero-G
    block_y = 0.0 + bob_y

    rl.rl_push_matrix()
    rl.rl_translatef(0.0, block_y, 0.0)
    # Xoay mượt quanh trục Y
    rl.rl_rotatef(t * 38.0, 0.0, 1.0, 0.0)
    # Nghiêng nhẹ theo X/Z để thấy nhiều góc nhìn
    tilt_x = math.sin(t * 1.2) * 18.0
    tilt_z = math.cos(t * 0.9) * 12.0
    rl.rl_rotatef(tilt_x, 1.0, 0.0, 0.0)
    rl.rl_rotatef(tilt_z, 0.0, 0.0, 1.0)

    # Khối cỡ lớn ấn tượng, tỷ lệ 1x2x1 với cấu trúc 3D của Skin đang chọn
    draw_deluxe_block(
        rl.Vector3(0.0, 0.0, 0.0),
        rl.Vector3(1.5, 3.0, 1.5),
        BLOCK_COLOR, BLOCK_WIRE, is_golden=True
    )
    rl.rl_pop_matrix()

    # ── Bệ đỡ Năng lượng Sci-Fi (Hologram Pedestal) ──
    pedestal_y = -2.2

    # Vòng tròn năng lượng đồng tâm xoay ngược chiều nhau (đồng điệu màu Skin)
    for ring_i in range(3):
        ring_radius = 1.2 + ring_i * 0.6
        ring_alpha = int(180 - ring_i * 50)
        ring_speed = (35.0 + ring_i * 15.0) * (1.0 if ring_i % 2 == 0 else -1.0)
        ring_bob = pedestal_y + math.sin(t * 1.5 + ring_i * 0.7) * 0.06

        rl.rl_push_matrix()
        rl.rl_translatef(0.0, ring_bob, 0.0)
        rl.rl_rotatef(t * ring_speed, 0.0, 1.0, 0.0)
        ring_pos = rl.Vector3(0.0, 0.0, 0.0)
        if ring_i % 2 == 0:
            ring_col = get_skin_accent_color(ctx.current_skin_idx, t, alpha=ring_alpha)
        else:
            ring_col = rl.Color(0, 240, 245, ring_alpha)
        rl.draw_cylinder_wires(ring_pos, ring_radius, ring_radius, 0.04, 24, ring_col)
        rl.rl_pop_matrix()

    # Cột sáng lượng tử mờ bên dưới
    beam_pos = rl.Vector3(0.0, pedestal_y - 0.8, 0.0)
    beam_accent = get_skin_accent_color(ctx.current_skin_idx, t, alpha=35)
    beam_wire = get_skin_accent_color(ctx.current_skin_idx, t, alpha=95)
    rl.draw_cube(beam_pos, 0.18, 1.6, 0.18, beam_accent)
    rl.draw_cube_wires(beam_pos, 0.20, 1.6, 0.20, beam_wire)

    # Cụm 3x3 ô gạch đá phiến bệ đỡ nổi
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            tile_x = dr * 1.1
            tile_z = dc * 1.1
            tile_y = pedestal_y - 0.1 + math.sin(t * 1.8 + dr * 1.3 + dc * 0.9) * 0.05
            tile_pos = rl.Vector3(tile_x, tile_y, tile_z)
            if dr == 0 and dc == 0:
                # Ô trung tâm phát sáng (ô đích)
                glow_a = int(185 + 70 * math.sin(t * 5.0))
                rl.draw_cube(tile_pos, 0.92, 0.12, 0.92, rl.Color(2, 5, 8, 255))
                rl.draw_cube_wires(tile_pos, 0.92, 0.12, 0.92, get_skin_accent_color(ctx.current_skin_idx, t, alpha=glow_a))
            else:
                top_col = rl.Color(76, 100, 116, 200) if (dr + dc) % 2 == 0 else rl.Color(58, 78, 92, 200)
                rl.draw_cube(tile_pos, 0.88, 0.10, 0.88, top_col)
                rl.draw_cube_wires(tile_pos, 0.88, 0.10, 0.88, rl.Color(28, 42, 52, 150))

    # Hạt vệ tinh năng lượng nhỏ xoay quanh khối
    for sat_i in range(5):
        sat_angle = t * (60.0 + sat_i * 18.0) + sat_i * 72.0
        sat_rad = math.radians(sat_angle)
        sat_dist = 2.2 + math.sin(t * 2.5 + sat_i) * 0.3
        sat_y_pos = bob_y + math.sin(t * 3.0 + sat_i * 1.5) * 0.6
        sat_x = math.cos(sat_rad) * sat_dist
        sat_z = math.sin(sat_rad) * sat_dist
        sat_sparkle = 0.5 + 0.5 * math.sin(t * 4.0 + sat_i * 2.0)
        sat_alpha = int(140 + 115 * sat_sparkle)
        if sat_i % 2 == 0:
            sat_col = get_skin_accent_color(ctx.current_skin_idx, t + sat_i * 0.5, alpha=sat_alpha)
        else:
            sat_col = rl.Color(0, 245, 255, sat_alpha)
        rl.draw_cube(rl.Vector3(sat_x, sat_y_pos, sat_z), 0.1, 0.1, 0.1, sat_col)


def draw_menu_screen(w, h):
    """Màn hình Menu chính Deluxe Split-Layout với điều hướng Bàn phím + Chuột & Bộ chọn 4 Skin 3D."""
    global menu_selected_idx

    # ── Xử lý điều hướng bàn phím ──
    _navigated, _confirmed = _handle_keyboard_navigation()

    # ══════════════════════════════════════════════════════════════════
    # A. NỬA BÊN TRÁI — Thương hiệu & Các nút điều hướng (≈50% chiều rộng)
    # ══════════════════════════════════════════════════════════════════

    # Gradient nền tối sang trọng cho nửa bên trái, trong suốt dần sang phải
    panel_w = int(w * 0.58)
    rl.draw_rectangle_gradient_h(
        0, 0, panel_w, h,
        rl.Color(5, 10, 18, 240),
        rl.Color(5, 10, 18, 0)
    )

    # ── [NÚT BẬT/TẮT NHẠC NỀN TRÊN MENU] ──
    btn_sound_menu = rl.Rectangle(w - 175, 24, 145, 38)
    h_snd_m, c_snd_m = check_button(btn_sound_menu)
    if h_snd_m:
        notify_hover("menu_btn_sound")
    music_on = is_bgm_enabled()
    snd_lbl = "NHẠC: BẬT (M)" if music_on else "NHẠC: TẮT (M)"
    snd_col = rl.Color(0, 240, 245, 255) if music_on else rl.Color(255, 80, 85, 255)
    draw_styled_button(btn_sound_menu, snd_lbl, 13, h_snd_m, active=music_on, accent_col=snd_col)
    if c_snd_m:
        toggle_bgm()
        play_sfx("ui_select")

    left_margin = 75

    # ── Badge nhỏ phía trên tiêu đề ──
    badge_text = "DELUXE 3D PUZZLE EDITION"
    badge_y = 80
    badge_w = measure_text_ui(badge_text, 12, is_bold=True)
    badge_rec = rl.Rectangle(left_margin - 6, badge_y - 4, badge_w + 12, 20)
    rl.draw_rectangle_rounded(badge_rec, 0.45, 6, rl.Color(0, 200, 210, 25))
    rl.draw_rectangle_rounded_lines(badge_rec, 0.45, 6, rl.Color(0, 240, 245, 100))
    draw_text_ui(badge_text, left_margin, badge_y, 12, rl.Color(0, 240, 245, 220), is_bold=True)

    # ── Tiêu đề lớn ──
    title_text = "BLOXORZ 3D"
    title_y = 115
    draw_text_ui(
        title_text, left_margin, title_y, 62,
        rl.Color(255, 215, 80, 255),
        is_bold=True, shadow=True,
        shadow_color=rl.Color(0, 0, 0, 220),
        glow=True,
        glow_color=rl.Color(255, 195, 50, 50)
    )

    # ── Dòng mô tả phụ ──
    subtitle_text = "Lăn khối - Giải mã không gian - Đấu trí cùng AI."
    subtitle_y = title_y + 72
    draw_text_ui(subtitle_text, left_margin, subtitle_y, 16, rl.Color(180, 200, 215, 200))

    # ══════════════════════════════════════════════════════════════════
    # CỤM 4 NÚT MENU với hiệu ứng chọn nổi bật
    # ══════════════════════════════════════════════════════════════════
    btn_w, btn_h = 370, 54
    btn_x = left_margin
    start_y = subtitle_y + 52
    gap = 70

    play_label = "TIẾP TỤC CHƠI" if ctx.game.moves > 0 else "BẮT ĐẦU CHƠI"
    btn_labels = [
        play_label,
        "CHỌN MÀN CHƠI (1 - 12)",
        "HƯỚNG DẪN LUẬT CHƠI",
        "THOÁT TRÒ CHƠI"
    ]
    btn_accents = [
        rl.Color(65, 245, 160, 255),   # Xanh ngọc lục bảo
        rl.Color(0, 240, 245, 255),    # Cyan
        rl.Color(255, 195, 80, 255),   # Vàng cam
        rl.Color(255, 80, 85, 255),    # Đỏ hồng
    ]
    btn_font_sizes = [19, 18, 18, 18]

    for i in range(4):
        is_selected = (i == menu_selected_idx)

        # Dịch nhẹ nút sang phải khi được chọn (phản hồi thị giác)
        offset_x = 8 if is_selected else 0

        btn_rec = rl.Rectangle(btn_x + offset_x, start_y + gap * i, btn_w, btn_h)

        # Kiểm tra click chuột (có cơ chế chống xung đột)
        clicked = _check_button_menu(btn_rec, i)

        # Vẽ thanh chỉ thị phát sáng bên trái khi đang được chọn
        if is_selected:
            accent = btn_accents[i]
            ar = getattr(accent, 'r', 0)
            ag = getattr(accent, 'g', 240)
            ab = getattr(accent, 'b', 245)

            indicator_x = btn_x - 8 + offset_x
            indicator_y = int(btn_rec.y + 8)
            indicator_h = int(btn_h - 16)

            # Thanh neon dọc phát sáng
            glow_pulse = 0.7 + 0.3 * math.sin(ctx.spin_timer * 5.0)
            glow_alpha = int(200 * glow_pulse)
            rl.draw_rectangle(indicator_x, indicator_y, 3, indicator_h, rl.Color(ar, ag, ab, glow_alpha))
            # Hào quang mờ xung quanh thanh
            rl.draw_rectangle(indicator_x - 3, indicator_y - 2, 9, indicator_h + 4, rl.Color(ar, ag, ab, int(40 * glow_pulse)))

        # Vẽ nút với trạng thái hover nếu đang được chọn
        draw_styled_button(
            btn_rec, btn_labels[i], btn_font_sizes[i],
            is_hover=is_selected,
            accent_col=btn_accents[i]
        )

        # Kích hoạt hành động khi click chuột
        if clicked:
            _activate_menu_action(i)

    # Kích hoạt hành động khi nhấn Enter/Space
    if _confirmed:
        _activate_menu_action(menu_selected_idx)

    # ══════════════════════════════════════════════════════════════════
    # THANH CHỈ DẪN ĐIỀU KHIỂN Ở GÓC DƯỚI BÊN TRÁI
    # ══════════════════════════════════════════════════════════════════
    hint = "[↑/↓] hoặc [W/S]: Di chuyển  ·  [Enter]: Chọn  ·  [B]: Đổi Skin  ·  [F11]: Toàn màn hình  ·  [M]: Nhạc"
    w_hint = measure_text_ui(hint, 12)
    hint_x = left_margin - 6
    hint_y = h - 55
    hint_pill = rl.Rectangle(hint_x - 8, hint_y - 5, w_hint + 16, 24)
    rl.draw_rectangle_rounded(hint_pill, 0.45, 8, rl.Color(10, 22, 32, 200))
    rl.draw_rectangle_rounded_lines(hint_pill, 0.45, 8, rl.Color(0, 200, 210, 60))
    draw_text_ui(hint, hint_x, hint_y, 12, rl.Color(150, 185, 200, 200))

    # ══════════════════════════════════════════════════════════════════
    # B. NỬA BÊN PHẢI — Thanh Chọn Skin 3D & Nhãn Trạng Thái
    # ══════════════════════════════════════════════════════════════════
    right_center_x = int(w * 0.74)

    # ── Thanh chọn Skin 3D tương tác: [<] [ SKIN: <Tên Skin> (B) ] [>] ──
    cur_skin = ctx.get_current_skin()
    skin_accent = get_skin_accent_color(ctx.current_skin_idx, ctx.spin_timer)
    skin_y = h - 148
    main_skin_w = 310
    arrow_w = 38
    skin_h = 40
    total_skin_w = arrow_w * 2 + main_skin_w + 16
    skin_start_x = right_center_x - total_skin_w // 2

    btn_prev_skin = rl.Rectangle(skin_start_x, skin_y, arrow_w, skin_h)
    btn_main_skin = rl.Rectangle(skin_start_x + arrow_w + 8, skin_y, main_skin_w, skin_h)
    btn_next_skin = rl.Rectangle(skin_start_x + arrow_w + 8 + main_skin_w + 8, skin_y, arrow_w, skin_h)

    h_ps, c_ps = check_button(btn_prev_skin)
    h_ms, c_ms = check_button(btn_main_skin)
    h_ns, c_ns = check_button(btn_next_skin)

    if h_ps:
        notify_hover("menu_skin_prev")
    elif h_ms:
        notify_hover("menu_skin_main")
    elif h_ns:
        notify_hover("menu_skin_next")

    skin_label = f"SKIN ({ctx.current_skin_idx + 1}/{len(BLOCK_SKINS)}): {cur_skin['name']} (B)"
    draw_styled_button(btn_prev_skin, "<", 16, h_ps, accent_col=skin_accent)
    draw_styled_button(btn_main_skin, skin_label, 13, h_ms, active=True, accent_col=skin_accent)
    draw_styled_button(btn_next_skin, ">", 16, h_ns, accent_col=skin_accent)

    if c_ps:
        ctx.cycle_skin(-1)
        play_sfx("ui_select")
    elif c_ms or c_ns:
        ctx.cycle_skin(1)
        play_sfx("ui_select")

    # Dòng trạng thái nhỏ tinh tế phía dưới thanh chọn Skin
    level_idx = ctx.game.level_index
    level_name = LEVEL_NAMES_VI[level_idx] if level_idx < len(LEVEL_NAMES_VI) else f"Màn {level_idx + 1}"
    status_text = f"ĐANG CHỜ LỆNH  ·  MÀN HIỆN TẠI: MÀN {level_idx + 1:02d}"
    w_status = measure_text_ui(status_text, 12)
    status_x = right_center_x - w_status // 2
    status_y = h - 90

    # Badge bo góc cho nhãn trạng thái
    status_pill = rl.Rectangle(status_x - 10, status_y - 4, w_status + 20, 22)
    rl.draw_rectangle_rounded(status_pill, 0.45, 6, rl.Color(5, 12, 20, 160))
    rl.draw_rectangle_rounded_lines(status_pill, 0.45, 6, rl.Color(0, 200, 210, 35))
    draw_text_ui(status_text, status_x, status_y, 12, rl.Color(0, 220, 230, 140))

    # Tên màn chơi dưới dòng trạng thái
    name_text = f"— {level_name} —"
    w_name = measure_text_ui(name_text, 13)
    name_x = right_center_x - w_name // 2
    draw_text_ui(name_text, name_x, status_y + 24, 13, rl.Color(255, 215, 80, 120))
