# ui/screens/hud.py
"""
Bloxorz 3D - Bảng điều khiển 2D HUD (Heads-Up Display)
Hiển thị thông tin màn chơi, số bước, Skin hiện tại, dropdown chọn thuật toán AI, phím tắt và Modal Thắng/Thua.
"""

import pyray as rl
from config import (
    LEVEL_NAMES_VI, STATE_MENU, STATE_LEVEL_SELECT,
    BLOCK_SKINS, get_skin_accent_color
)
from app_state import ctx
from ui.font_manager import draw_text_ui, measure_text_ui
from ui.widgets import check_button, draw_styled_button
from ai_controller import trigger_ai_solve
from audio_manager import play_sfx, toggle_bgm, is_bgm_enabled, notify_hover


def draw_2d_hud():
    """Bảng thông tin khi đang chơi, nút Skin, nút Menu, Dropdown Solvers, Nút Nhạc và Modal Thắng/Thua"""
    game = ctx.game
    w = rl.get_screen_width()
    h = rl.get_screen_height()

    clean_name = LEVEL_NAMES_VI[game.level_index] if game.level_index < len(LEVEL_NAMES_VI) else f"Màn {game.level_index + 1}"
    cur_skin = ctx.get_current_skin()
    skin_accent = get_skin_accent_color(ctx.current_skin_idx, ctx.spin_timer)

    # Card thông tin góc trái (hiển thị cả tên màn, bước đi và tên Skin hiện tại)
    card_w = min(320, max(280, w - 620))
    card_rect = rl.Rectangle(20, 18, card_w, 114)
    rl.draw_rectangle_rounded(card_rect, 0.16, 8, rl.Color(14, 28, 38, 225))
    rl.draw_rectangle_rounded_lines(card_rect, 0.16, 8, rl.Color(0, 240, 245, 140))

    # Vệt phản chiếu ánh sáng thủy tinh (Glass highlight)
    c_hl = rl.Rectangle(22, 20, card_w - 4, 36)
    rl.draw_rectangle_rounded(c_hl, 0.16, 8, rl.Color(255, 255, 255, 10))

    draw_text_ui("BLOXORZ 3D", 34, 26, 21, rl.Color(255, 215, 80, 255), is_bold=True, shadow=True, glow=True, glow_color=rl.Color(255, 195, 50, 40))
    lvl_info = f"MÀN {game.level_index + 1:02d}  ·  {clean_name}"
    lvl_sz = 14
    while measure_text_ui(lvl_info, lvl_sz, is_bold=True) > (card_w - 36) and lvl_sz > 10:
        lvl_sz -= 1
    draw_text_ui(lvl_info, 34, 53, lvl_sz, rl.Color(220, 240, 250, 255), is_bold=True)
    draw_text_ui(f"BƯỚC ĐI: {game.moves}", 34, 75, 16, rl.Color(0, 240, 245, 255), is_bold=True, glow=True)

    # Nhãn Skin hiện tại ngay trong thẻ thông tin góc trái
    skin_info_txt = f"SKIN: {cur_skin['name']} (B)"
    skin_sz = 12
    while measure_text_ui(skin_info_txt, skin_sz, is_bold=True) > (card_w - 36) and skin_sz > 10:
        skin_sz -= 1
    draw_text_ui(skin_info_txt, 34, 100, skin_sz, skin_accent, is_bold=True)

    # ── [NÚT ĐỔI SKIN NHANH (B)] ─────────────────────────────────
    btn_skin = rl.Rectangle(w - 585, 24, 135, 40)
    h_skin, c_skin = check_button(btn_skin)
    if h_skin:
        notify_hover("hud_btn_skin")
    skin_btn_lbl = f"SKIN {ctx.current_skin_idx + 1}/{len(BLOCK_SKINS)} (B)"
    draw_styled_button(btn_skin, skin_btn_lbl, 13, h_skin, active=False, accent_col=skin_accent)
    if c_skin:
        ctx.cycle_skin(1)
        play_sfx("ui_select")

    # ── [NÚT BẬT/TẮT NHẠC NỀN] ─────────────────────────────────
    btn_sound = rl.Rectangle(w - 440, 24, 135, 40)
    h_sound, c_sound = check_button(btn_sound)
    if h_sound:
        notify_hover("hud_btn_sound")

    music_on = is_bgm_enabled()
    snd_label = "NHẠC: BẬT (M)" if music_on else "NHẠC: TẮT (M)"
    snd_col = rl.Color(0, 240, 245, 255) if music_on else rl.Color(255, 80, 85, 255)
    draw_styled_button(btn_sound, snd_label, 13, h_sound, active=music_on, accent_col=snd_col)
    if c_sound:
        toggle_bgm()
        play_sfx("ui_select")

    # ── [NÚT SOLVERS DROPDOWN] ─────────────────────────────────
    btn_solvers = rl.Rectangle(w - 295, 24, 135, 40)
    h_solvers, c_solvers = check_button(btn_solvers)
    if h_solvers:
        notify_hover("hud_btn_solvers")

    cur_algo = ctx.solver_names[ctx.current_solver_idx]

    # Nếu AI đang tự chạy thì hiện nút "DỪNG AI (H)", ngược lại hiện "AI: Tên ▼"
    if ctx.ai_move_queue:
        solvers_label = "DỪNG AI (H)"
        draw_styled_button(btn_solvers, solvers_label, 14, h_solvers, active=True, accent_col=rl.Color(255, 80, 85, 255))
        if c_solvers:
            play_sfx("ui_back")
            ctx.ai_move_queue.clear()
    else:
        arrow = "▲" if ctx.show_solvers_dropdown else "▼"
        solvers_label = f"AI: {cur_algo} {arrow}"
        draw_styled_button(btn_solvers, solvers_label, 14, h_solvers, active=ctx.show_solvers_dropdown, accent_col=rl.Color(65, 245, 160, 255))
        if c_solvers:
            play_sfx("ui_select")
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
            if h_item:
                notify_hover(f"hud_solver_{idx}")

            # Highlight làm sáng thuật toán đang được chọn (active)
            is_active = (idx == ctx.current_solver_idx)
            item_label = f"● {name}" if is_active else name
            item_accent = rl.Color(255, 215, 80, 255) if is_active else rl.Color(0, 240, 245, 255)

            draw_styled_button(
                item_rect,
                item_label,
                14,
                h_item,
                active=is_active,
                accent_col=item_accent
            )
            # Click vào thuật toán nào -> chọn và chạy ngay thuật toán đó!
            if c_item:
                play_sfx("ui_select")
                trigger_ai_solve(name)

        # Tự động đóng menu nếu người chơi click chuột ra ngoài vùng menu
        if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT) and not h_solvers:
            mouse_pos = rl.get_mouse_position()
            if not rl.check_collision_point_rec(mouse_pos, drop_rect):
                ctx.show_solvers_dropdown = False

    # Nút [MENU (ESC)] ở góc trên bên phải
    btn_menu_top = rl.Rectangle(w - 150, 24, 126, 40)
    h_mtop, c_mtop = check_button(btn_menu_top)
    if h_mtop:
        notify_hover("hud_btn_menu_top")
    draw_styled_button(btn_menu_top, "MENU (ESC)", 15, h_mtop, accent_col=rl.Color(255, 215, 80, 255))
    if c_mtop:
        play_sfx("ui_back")
        ctx.ai_move_queue.clear()
        ctx.current_state = STATE_MENU

    # Thanh điều khiển đáy màn hình (có bổ sung [B]: Đổi Skin & [F11]: Toàn màn hình)
    bar_w = min(w - 30, 1040)
    bar_rect = rl.Rectangle(w // 2 - bar_w // 2, h - 46, bar_w, 34)
    rl.draw_rectangle_rounded(bar_rect, 0.45, 8, rl.Color(14, 28, 38, 215))
    rl.draw_rectangle_rounded_lines(bar_rect, 0.45, 8, rl.Color(65, 90, 110, 160))

    ctrl_text = f"[W/A/S/D]: Lăn khối  ·  [B]: Đổi Skin  ·  [F11]: Toàn màn hình  ·  [H]: AI ({cur_algo})  ·  [Tab]: Đổi AI  ·  [Z]: Hoàn tác  ·  [Space]: Đổi khối  ·  [R]: Chơi lại"
    ctrl_sz = 13
    text_w = measure_text_ui(ctrl_text, ctrl_sz, is_bold=False)
    while text_w > bar_w - 20 and ctrl_sz > 10:
        ctrl_sz -= 1
        text_w = measure_text_ui(ctrl_text, ctrl_sz, is_bold=False)
    draw_text_ui(ctrl_text, w // 2 - text_w // 2, h - 38, ctrl_sz, rl.Color(195, 225, 235, 255), is_bold=False)

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

            if h1: notify_hover("modal_won_b1")
            elif h2: notify_hover("modal_won_b2")
            elif h3: notify_hover("modal_won_b3")

            draw_styled_button(b1, "MÀN TIẾP (Space)", 13, h1, accent_col=rl.Color(65, 245, 160, 255))
            draw_styled_button(b2, "CHỌN MÀN", 14, h2)
            draw_styled_button(b3, "MENU CHÍNH", 14, h3)

            if c1:
                play_sfx("ui_select")
                game.next_level()
                ctx.reset_camera()
                ctx.roll_animating = False
                ctx.buffered_move = None
            elif c2:
                play_sfx("ui_select")
                ctx.current_state = STATE_LEVEL_SELECT
                ctx.roll_animating = False
                ctx.buffered_move = None
            elif c3:
                play_sfx("ui_back")
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

            if h1: notify_hover("modal_lost_b1")
            elif h2: notify_hover("modal_lost_b2")
            elif h3: notify_hover("modal_lost_b3")

            draw_styled_button(b1, "HOÀN TÁC (Z)", 14, h1, accent_col=rl.Color(0, 240, 245, 255))
            draw_styled_button(b2, "CHƠI LẠI (R)", 14, h2, accent_col=rl.Color(255, 215, 80, 255))
            draw_styled_button(b3, "MENU CHÍNH", 14, h3)

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
            elif c3:
                play_sfx("ui_back")
                ctx.current_state = STATE_MENU
                ctx.roll_animating = False
                ctx.buffered_move = None

        w1 = measure_text_ui(t1, 32, is_bold=True)
        w2 = measure_text_ui(t2, 16, is_bold=False)
        draw_text_ui(t1, w // 2 - w1 // 2, h // 2 - 64, 32, col1, is_bold=True, shadow=True, glow=True)
        draw_text_ui(t2, w // 2 - w2 // 2, h // 2 - 18, 16, rl.Color(225, 240, 250, 255), is_bold=False)

    # ── [THÔNG BÁO NỔI TOAST (AI / THÔNG ĐIỆP HỆ THỐNG)] ───────
    if ctx.toast_timer > 0:
        ctx.toast_timer -= rl.get_frame_time()
        t_sz = 14
        tw = measure_text_ui(ctx.toast_message, t_sz, is_bold=True)
        toast_w = max(260, tw + 44)
        toast_h = 36
        toast_x = w // 2 - toast_w // 2
        toast_y = 76
        t_rect = rl.Rectangle(toast_x, toast_y, toast_w, toast_h)
        col_accent = ctx.toast_color if ctx.toast_color is not None else rl.Color(0, 240, 245, 255)
        rl.draw_rectangle_rounded(t_rect, 0.40, 8, rl.Color(12, 22, 32, 240))
        rl.draw_rectangle_rounded_lines(t_rect, 0.40, 8, col_accent)
        draw_text_ui(ctx.toast_message, toast_x + (toast_w - tw) // 2, toast_y + 9, t_sz, col_accent, is_bold=True)
