# ui/screens/menu_screen.py
"""
Bloxorz 3D - Giao diện Màn hình Menu chính
Hiển thị logo trò chơi và các tùy chọn: Bắt đầu chơi, Chọn màn, Hướng dẫn, Thoát.
"""

import sys
import pyray as rl
from config import STATE_PLAYING, STATE_LEVEL_SELECT, STATE_TUTORIAL_STAGE1
from app_state import ctx
from ui.font_manager import draw_text_ui, measure_text_ui
from ui.widgets import check_button, draw_styled_button


def draw_menu_screen(w, h):
    """Màn hình Menu chính khởi đầu game"""
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

    play_label = "TIẾP TỤC CHƠI" if ctx.game.moves > 0 else "BẮT ĐẦU CHƠI"
    btn_play_rec = rl.Rectangle(w // 2 - btn_w // 2, start_y, btn_w, btn_h)
    btn_lvl_rec = rl.Rectangle(w // 2 - btn_w // 2, start_y + gap, btn_w, btn_h)
    btn_help_rec = rl.Rectangle(w // 2 - btn_w // 2, start_y + gap * 2, btn_w, btn_h)
    btn_exit_rec = rl.Rectangle(w // 2 - btn_w // 2, start_y + gap * 3, btn_w, btn_h)

    # 1. Nút Vào chơi
    h_play, c_play = check_button(btn_play_rec)
    draw_styled_button(btn_play_rec, play_label, 19, h_play, accent_col=rl.Color(65, 245, 160, 255))
    if c_play:
        ctx.current_state = STATE_PLAYING

    # 2. Nút Chọn màn (1 - 12)
    h_lvl, c_lvl = check_button(btn_lvl_rec)
    draw_styled_button(btn_lvl_rec, "CHỌN MÀN CHƠI (1 - 12)", 18, h_lvl, accent_col=rl.Color(0, 240, 245, 255))
    if c_lvl:
        ctx.current_state = STATE_LEVEL_SELECT

    # 3. Nút Hướng dẫn
    h_help, c_help = check_button(btn_help_rec)
    draw_styled_button(btn_help_rec, "HƯỚNG DẪN LUẬT CHƠI", 18, h_help, accent_col=rl.Color(255, 195, 80, 255))
    if c_help:
        ctx.current_state = STATE_TUTORIAL_STAGE1

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
