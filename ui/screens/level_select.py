# ui/screens/level_select.py
"""
Bloxorz 3D - Giao diện Màn hình Chọn màn chơi
Hiển thị danh sách 12 màn chơi dưới dạng thẻ bài Glassmorphic cao cấp.
"""

import pyray as rl
from levels import LEVELS
from config import LEVEL_NAMES_VI, STATE_MENU
from app_state import ctx
from ui.font_manager import draw_text_ui, measure_text_ui
from ui.widgets import check_button, draw_styled_button
from audio_manager import play_sfx, notify_hover


def draw_level_select_screen(w, h):
    """Màn hình lưới 12 màn chơi trực quan với thẻ bài Glassmorphic cao cấp"""
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
        is_cur = (i == ctx.game.level_index)
        hover, clicked = check_button(crec)
        if hover:
            notify_hover(f"lvl_card_{i}")

        if clicked:
            play_sfx("ui_select")
            ctx.load_and_play_level(i)
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
        name_sz = 14
        while measure_text_ui(lvl_name_text, name_sz, is_bold=True) > (card_w - 28) and name_sz > 11:
            name_sz -= 1
        draw_text_ui(lvl_name_text, cx + 16, cy + 38, name_sz, rl.Color(225, 240, 250, 255), is_bold=True)

        status_tag = "ĐANG CHƠI" if is_cur else "VÀO CHƠI"
        tag_col = rl.Color(65, 245, 160, 255) if is_cur else rl.Color(150, 185, 205, 200)
        draw_text_ui(status_tag, cx + 16, cy + 64, 12, tag_col)

    # Nút quay lại Menu
    btn_back_rec = rl.Rectangle(w // 2 - 130, h - 68, 260, 44)
    h_back, c_back = check_button(btn_back_rec)
    if h_back:
        notify_hover("lvl_btn_back")
    draw_styled_button(btn_back_rec, "< QUAY LẠI MENU", 17, h_back)
    if c_back:
        play_sfx("ui_back")
        ctx.current_state = STATE_MENU
