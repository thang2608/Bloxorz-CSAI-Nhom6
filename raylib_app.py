# raylib_app.py
"""
BLOXORZ 3D - AI SOLVER EDITION
Điểm khởi chạy ứng dụng (Main Entry Point).
Kiến trúc mô-đun hóa cao cấp, tinh gọn, đảm bảo hiệu năng 60 FPS mượt mà.
"""

import math
try:
    import pyray as rl
except ImportError:
    from raylib import pyray as rl

from levels import LEVELS
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR,
    STATE_PLAYING, STATE_MENU, STATE_LEVEL_SELECT,
    STATE_TUTORIAL_STAGE1, STATE_TUTORIAL_STAGE2, STATE_TUTORIAL_PRACTICE
)
from app_state import ctx
from ui.font_manager import init_fonts
from ui.widgets import draw_cinematic_vignette
from ui.effects import draw_cosmic_space_backdrop
from ui.render3d import draw_3d_scene
from ui.animation import perform_move, update_roll_animation
from ai_controller import trigger_ai_solve, cycle_solver
from ui.screens.menu_screen import draw_menu_screen, draw_menu_3d_showcase
from ui.screens.level_select import draw_level_select_screen
from ui.screens.hud import draw_2d_hud
from ui.screens.tutorial import (
    draw_tutorial_stage1, draw_tutorial_stage2, draw_tutorial_practice_hud,
    enter_tutorial_practice, exit_tutorial_practice
)
from audio_manager import (
    init_audio, close_audio, update_music, play_sfx, toggle_bgm, toggle_sfx
)


def main():
    # ── 1. Khởi tạo Cửa sổ & Đồ họa Raylib ──
    rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Bloxorz 3D - AI Solver Edition")
    rl.set_target_fps(60)
    rl.set_exit_key(0)  # Ngăn phím ESC tự động đóng cửa sổ

    # Nạp font chữ tiếng Việt có dấu
    init_fonts()

    # Khởi tạo hệ thống âm thanh & BGM
    init_audio()

    # Khởi tạo góc nhìn Camera ban đầu
    ctx.reset_camera()

    # ── 2. Vòng lặp Trò chơi Chính (Main Game Loop) ──
    while not rl.window_should_close():
        dt = rl.get_frame_time()
        ctx.spin_timer += dt
        game = ctx.game

        # Cập nhật luồng nhạc nền liên tục
        update_music()

        # Phím tắt toàn cục: [M] Bật/tắt nhạc nền, [K] Bật/tắt SFX
        if rl.is_key_pressed(rl.KEY_M):
            toggle_bgm()
        if rl.is_key_pressed(rl.KEY_K):
            toggle_sfx()

        # ── Phím ESC: Điều hướng trạng thái thông minh ──
        if rl.is_key_pressed(rl.KEY_ESCAPE):
            play_sfx("ui_back")
            ctx.ai_move_queue.clear()
            if ctx.current_state == STATE_PLAYING:
                ctx.current_state = STATE_MENU
            elif ctx.current_state == STATE_TUTORIAL_PRACTICE:
                exit_tutorial_practice()
                ctx.current_state = STATE_TUTORIAL_STAGE2
            elif ctx.current_state == STATE_TUTORIAL_STAGE2:
                ctx.current_state = STATE_TUTORIAL_STAGE1
            elif ctx.current_state == STATE_TUTORIAL_STAGE1:
                ctx.current_state = STATE_MENU
            elif ctx.current_state == STATE_LEVEL_SELECT:
                ctx.current_state = STATE_MENU
            elif ctx.current_state == STATE_MENU:
                if ctx.main_game_snapshot is None and game.status == "PLAYING":
                    ctx.current_state = STATE_PLAYING

        # ── A. Xử lý Input khi ĐANG CHƠI hoặc THỰC HÀNH TUTORIAL ──
        if ctx.current_state in (STATE_PLAYING, STATE_TUTORIAL_PRACTICE):
            is_tut = (ctx.current_state == STATE_TUTORIAL_PRACTICE)

            # 1. Trạng thái ĐÃ CHIẾN THẮNG
            if game.status == "WON" and not ctx.roll_animating:
                ctx.ai_move_queue.clear()
                if not is_tut:
                    if (rl.is_key_pressed(rl.KEY_SPACE) or rl.is_key_pressed(rl.KEY_ENTER) or
                            rl.is_key_pressed(rl.KEY_N)):
                        play_sfx("ui_select")
                        game.next_level()
                        ctx.reset_camera()
                        ctx.roll_animating = False
                        ctx.buffered_move = None
                else:
                    if rl.is_key_pressed(rl.KEY_SPACE) or rl.is_key_pressed(rl.KEY_ENTER):
                        play_sfx("ui_select")
                        if ctx.current_tutorial_idx < 5:
                            enter_tutorial_practice(ctx.current_tutorial_idx + 1)
                        else:
                            exit_tutorial_practice()
                            ctx.current_state = STATE_TUTORIAL_STAGE2

            # 2. Trạng thái THẤT BẠI
            elif game.status == "LOST" and not ctx.roll_animating:
                ctx.ai_move_queue.clear()
                if (rl.is_key_pressed(rl.KEY_SPACE) or rl.is_key_pressed(rl.KEY_ENTER) or
                        rl.is_key_pressed(rl.KEY_R)):
                    play_sfx("reset")
                    game.reset()
                    ctx.reset_camera()
                    ctx.roll_animating = False
                    ctx.buffered_move = None
                elif rl.is_key_pressed(rl.KEY_Z) or rl.is_key_pressed(rl.KEY_BACKSPACE):
                    if game.undo():
                        play_sfx("undo")
                        ctx.roll_animating = False
                        ctx.buffered_move = None

            # 3. Trạng thái ĐANG CHƠI
            else:
                target_move = None
                if rl.is_key_pressed(rl.KEY_W) or rl.is_key_pressed(rl.KEY_UP):
                    ctx.ai_move_queue.clear()
                    target_move = "UP"
                elif rl.is_key_pressed(rl.KEY_S) or rl.is_key_pressed(rl.KEY_DOWN):
                    ctx.ai_move_queue.clear()
                    target_move = "DOWN"
                elif rl.is_key_pressed(rl.KEY_A) or rl.is_key_pressed(rl.KEY_LEFT):
                    ctx.ai_move_queue.clear()
                    target_move = "LEFT"
                elif rl.is_key_pressed(rl.KEY_D) or rl.is_key_pressed(rl.KEY_RIGHT):
                    ctx.ai_move_queue.clear()
                    target_move = "RIGHT"
                elif rl.is_key_pressed(rl.KEY_H):
                    if is_tut:
                        ctx.show_tutorial_hint = not ctx.show_tutorial_hint
                    else:
                        trigger_ai_solve()
                elif rl.is_key_pressed(rl.KEY_TAB) and not is_tut:
                    cycle_solver()
                    play_sfx("ui_nav")
                elif rl.is_key_pressed(rl.KEY_SPACE):
                    if game.is_split and not ctx.roll_animating:
                        game.move("SWITCH")
                        play_sfx("block_swap")
                elif rl.is_key_pressed(rl.KEY_Z) or rl.is_key_pressed(rl.KEY_BACKSPACE):
                    ctx.ai_move_queue.clear()
                    if game.undo():
                        play_sfx("undo")
                        ctx.roll_animating = False
                        ctx.buffered_move = None
                elif rl.is_key_pressed(rl.KEY_R):
                    ctx.ai_move_queue.clear()
                    game.reset()
                    play_sfx("reset")
                    ctx.reset_camera()
                    ctx.roll_animating = False
                    ctx.buffered_move = None
                elif not is_tut and rl.is_key_pressed(rl.KEY_N):
                    ctx.ai_move_queue.clear()
                    game.next_level()
                    play_sfx("ui_select")
                    ctx.reset_camera()
                    ctx.roll_animating = False
                    ctx.buffered_move = None
                elif not is_tut and rl.is_key_pressed(rl.KEY_P):
                    ctx.ai_move_queue.clear()
                    prev_i = (game.level_index - 1) % len(LEVELS)
                    game.load_level(prev_i)
                    play_sfx("ui_select")
                    ctx.reset_camera()
                    ctx.roll_animating = False
                    ctx.buffered_move = None
                elif rl.is_key_pressed(rl.KEY_C):
                    ctx.reset_camera()

                if target_move:
                    if not ctx.roll_animating:
                        perform_move(target_move)
                    elif game.status == "PLAYING":
                        ctx.buffered_move = target_move

                # Tự động lấy bước đi từ hàng đợi AI khi khối đã hoàn tất bước lăn
                if not is_tut and not ctx.roll_animating and ctx.ai_move_queue and game.status == "PLAYING":
                    next_ai_action = ctx.ai_move_queue.pop(0)
                    if next_ai_action == "SWITCH":
                        game.move("SWITCH")
                        play_sfx("block_swap")
                    else:
                        perform_move(next_ai_action)

            # Xoay Camera 360° bằng chuột khi giữ chuột
            if rl.is_mouse_button_down(rl.MOUSE_BUTTON_LEFT) or rl.is_mouse_button_down(rl.MOUSE_BUTTON_RIGHT):
                delta = rl.get_mouse_delta()
                ctx.target_yaw += delta.x * 0.35
                ctx.target_pitch = max(15.0, min(80.0, ctx.target_pitch - delta.y * 0.35))

            # Phím Q / E xoay góc nhìn mượt mà
            if rl.is_key_down(rl.KEY_Q):
                ctx.target_yaw -= 85.0 * dt
            if rl.is_key_down(rl.KEY_E):
                ctx.target_yaw += 85.0 * dt

            # Cuộn chuột để Zoom
            wheel = rl.get_mouse_wheel_move()
            if wheel != 0:
                ctx.target_dist = max(7.0, min(48.0, ctx.target_dist - wheel * 1.6))

            # Giảm chấn mượt mà (Smooth Damping Interpolation) khi đang trong gameplay
            damping = min(1.0, dt * 14.0)
            ctx.cam_yaw += (ctx.target_yaw - ctx.cam_yaw) * damping
            ctx.cam_pitch += (ctx.target_pitch - ctx.cam_pitch) * damping
            ctx.cam_dist += (ctx.target_dist - ctx.cam_dist) * damping

        else:
            if ctx.current_state == STATE_MENU:
                # Camera đặc biệt cho Menu: Nhìn vào gốc tọa độ, dịch sang phải
                # để khối 3D trưng bày nằm ở nửa bên phải màn hình
                ctx.target_yaw = -25.0
                ctx.target_pitch = 32.0
                ctx.target_dist = 12.0
                ctx.cam_yaw = -25.0
                ctx.cam_pitch = 32.0
                ctx.cam_dist = 12.0
            else:
                # Khi ở Bảng chọn màn / Hướng dẫn: Khóa Camera tĩnh tuyệt đối
                default_dist = max(game.rows, game.cols) * 1.48 + 4.0
                ctx.target_yaw = -25.0
                ctx.target_pitch = 48.0
                ctx.target_dist = default_dist
                ctx.cam_yaw = -25.0
                ctx.cam_pitch = 48.0
                ctx.cam_dist = default_dist

        # ── B. Cập nhật Tọa độ Camera Orbital ──
        if ctx.current_state == STATE_MENU:
            # Camera cho menu: target dịch sang trái để khối 3D ở nửa phải màn hình
            import math as _math
            _rad_yaw = _math.radians(ctx.cam_yaw)
            _rad_pitch = _math.radians(ctx.cam_pitch)
            # Dịch camera target sang trái theo hướng nhìn để vật thể tại (0,0,0) hiện ở nửa phải
            ctx.camera.target = rl.Vector3(-3.5, -0.5, 0.0)
            _eye_x = -3.5 + ctx.cam_dist * _math.cos(_rad_pitch) * _math.sin(_rad_yaw)
            _eye_y = -0.5 + ctx.cam_dist * _math.sin(_rad_pitch)
            _eye_z = 0.0 + ctx.cam_dist * _math.cos(_rad_pitch) * _math.cos(_rad_yaw)
            ctx.camera.position = rl.Vector3(_eye_x, _eye_y, _eye_z)
        else:
            ctx.update_camera_coords()

        # ── C. Cập nhật Hoạt ảnh Lật Vật lý 3D ──
        update_roll_animation(dt)

        # ── D. Render Khung hình ──
        win_w = rl.get_screen_width()
        win_h = rl.get_screen_height()

        rl.begin_drawing()
        rl.clear_background(BG_COLOR)

        # Phông nền vũ trụ (Tinh vân phát quang, Sao 2D, Sao băng)
        draw_cosmic_space_backdrop(win_w, win_h, dt)

        # Không gian 3D
        rl.begin_mode_3d(ctx.camera)
        if ctx.current_state == STATE_MENU:
            # Chỉ vẽ khối trưng bày showcase, không vẽ bàn cờ game
            draw_menu_3d_showcase(dt)
        else:
            draw_3d_scene(dt)
        rl.end_mode_3d()

        # Giao diện tương ứng với State
        if ctx.current_state == STATE_PLAYING:
            draw_cinematic_vignette(win_w, win_h)
            draw_2d_hud()
        elif ctx.current_state == STATE_TUTORIAL_PRACTICE:
            draw_cinematic_vignette(win_w, win_h)
            draw_tutorial_practice_hud(win_w, win_h)
        elif ctx.current_state == STATE_MENU:
            draw_menu_screen(win_w, win_h)
        elif ctx.current_state == STATE_LEVEL_SELECT:
            draw_level_select_screen(win_w, win_h)
        elif ctx.current_state == STATE_TUTORIAL_STAGE1:
            draw_tutorial_stage1(win_w, win_h)
        elif ctx.current_state == STATE_TUTORIAL_STAGE2:
            draw_tutorial_stage2(win_w, win_h)

        rl.end_drawing()

    close_audio()
    rl.close_window()


if __name__ == "__main__":
    main()
