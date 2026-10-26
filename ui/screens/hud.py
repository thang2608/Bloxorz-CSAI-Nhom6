# ui/screens/hud.py
"""
Bloxorz 3D - Bảng điều khiển 2D HUD (Heads-Up Display)
Hiển thị thông tin màn chơi, số bước, dropdown chọn thuật toán AI, phím tắt và Modal Thắng/Thua.
"""

import pyray as rl
from config import LEVEL_NAMES_VI, STATE_MENU, STATE_LEVEL_SELECT
from app_state import ctx
from ui.font_manager import draw_text_ui, measure_text_ui
from ui.widgets import check_button, draw_styled_button
from ai_controller import trigger_ai_solve


def draw_2d_hud():
    """Bảng thông tin khi đang chơi, nút Menu, Dropdown Solvers và Modal Thắng/Thua"""
    game = ctx.game
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
    btn_solvers = rl.Rectangle(w - 295, 24, 135, 40)
    h_solvers, c_solvers = check_button(btn_solvers)

    # Nếu AI đang tự chạy thì hiện nút "DỪNG THUẬT TOÁN", ngược lại hiện "SOLVERS ▼"
    if ctx.ai_move_queue:
        solvers_label = "DỪNG THUẬT TOÁN"
        draw_styled_button(btn_solvers, solvers_label, 14, h_solvers, active=True, accent_col=rl.Color(255, 80, 85, 255))
        if c_solvers:
            ctx.ai_move_queue.clear()
    else:
        arrow = "▲" if ctx.show_solvers_dropdown else "▼"
        solvers_label = f"SOLVERS {arrow}"
        draw_styled_button(btn_solvers, solvers_label, 14, h_solvers, active=ctx.show_solvers_dropdown, accent_col=rl.Color(65, 245, 160, 255))
        if c_solvers:
            ctx.show_solvers_dropdown = not ctx.show_solvers_dropdown

    # Vẽ danh sách menu xổ xuống khi show_solvers_dropdown = True
    if ctx.show_solvers_dropdown and not ctx.ai_move_queue:
        item_h = 36
        total_menu_h = len(ctx.solver_names) * (item_h + 4) + 6
        drop_rect = rl.Rectangle(w - 295, 68, 135, total_menu_h)

        # Khung nền đổ bóng cho menu dropdown
        rl.draw_rectangle_rounded(drop_rect, 0.16, 6, rl.Color(14, 24, 34, 250))
        rl.draw_rectangle_rounded_lines(drop_rect, 0.16, 6, rl.Color(0, 240, 245, 180))

        # Vẽ từng thuật toán có trong hệ thống (A*, BFS, DFS,...)
        for idx, name in enumerate(ctx.solver_names):
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
                ctx.show_solvers_dropdown = False

    # Nút [MENU (ESC)] ở góc trên bên phải
    btn_menu_top = rl.Rectangle(w - 150, 24, 126, 40)
    h_mtop, c_mtop = check_button(btn_menu_top)
    draw_styled_button(btn_menu_top, "MENU (ESC)", 15, h_mtop, accent_col=rl.Color(255, 215, 80, 255))
    if c_mtop:
        ctx.ai_move_queue.clear()
        ctx.current_state = STATE_MENU

    # Thanh điều khiển đáy màn hình
    bar_w = min(w - 40, 960)
    bar_rect = rl.Rectangle(w // 2 - bar_w // 2, h - 46, bar_w, 34)
    rl.draw_rectangle_rounded(bar_rect, 0.45, 8, rl.Color(14, 28, 38, 215))
    rl.draw_rectangle_rounded_lines(bar_rect, 0.45, 8, rl.Color(65, 90, 110, 160))

    ctrl_text = "[W/A/S/D]: Lăn khối  ·  [H]: AI Giải  ·  [Tab]: Đổi thuật toán  ·  [Z]: Hoàn tác  ·  [Space]: Đổi khối  ·  [R]: Chơi lại"
    text_w = measure_text_ui(ctrl_text, 13, is_bold=False)
    draw_text_ui(ctrl_text, w // 2 - text_w // 2, h - 38, 13, rl.Color(195, 225, 235, 255), is_bold=False)

    # Modal Thắng / Thua tương tác đầy đủ (chỉ hiện khi đã hoàn tất hoạt ảnh)
    if game.status in ("WON", "LOST") and not ctx.roll_animating:
        ctx.ai_move_queue.clear()
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
                ctx.reset_camera()
                ctx.roll_animating = False
                ctx.buffered_move = None
            elif c2:
                ctx.current_state = STATE_LEVEL_SELECT
                ctx.roll_animating = False
                ctx.buffered_move = None
            elif c3:
                ctx.current_state = STATE_MENU
                ctx.roll_animating = False
                ctx.buffered_move = None

        else:  # LOST
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
                    ctx.roll_animating = False
                    ctx.buffered_move = None
            elif c2:
                game.reset()
                ctx.reset_camera()
                ctx.roll_animating = False
                ctx.buffered_move = None
            elif c3:
                ctx.current_state = STATE_MENU
                ctx.roll_animating = False
                ctx.buffered_move = None

        w1 = measure_text_ui(t1, 32, is_bold=True)
        w2 = measure_text_ui(t2, 16, is_bold=False)
        draw_text_ui(t1, w // 2 - w1 // 2, h // 2 - 64, 32, col1, is_bold=True, shadow=True, glow=True)
        draw_text_ui(t2, w // 2 - w2 // 2, h // 2 - 18, 16, rl.Color(225, 240, 250, 255), is_bold=False)
