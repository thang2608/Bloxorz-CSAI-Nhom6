# ui/render3d.py
"""
Bloxorz 3D - Bộ dựng hình không gian 3D (3D Renderer)
Vẽ bàn cờ đa tầng, ô đích, công tắc, bóng đổ tiếp xúc và khối hộp lật vật lý.
"""

import math
import pyray as rl
from config import (
    PEDESTAL_COLOR, TILE_TOP_A, TILE_TOP_B, WIRE_COLOR,
    FRAGILE_TOP, FRAGILE_BASE, BRIDGE_TOP, BRIDGE_BASE,
    GOAL_HOLE, GOAL_BEAM, GOAL_BEAM_WIRE,
    BLOCK_COLOR, BLOCK_WIRE,
    MINI_ACTIVE, MINI_ACTIVE_WIRE, MINI_IDLE, MINI_IDLE_WIRE
)
from app_state import ctx
from ui.animation import grid_to_world, get_block_target_transform
from ui.effects import draw_starfield, update_and_draw_particles


def draw_deluxe_block(pos, size, color, wire_color, is_golden=True):
    """Vẽ khối hộp kim loại vát cạnh sang trọng, hiển thị đường nối mờ tinh tế phân chia hai nửa 1x1x1"""
    # 1. Vẽ thân khối hộp chính và viền ngoài
    rl.draw_cube(pos, size.x, size.y, size.z, color)
    rl.draw_cube_wires(pos, size.x, size.y, size.z, wire_color)

    # Kiểm tra xem khối có phải là khối dài 2x1x1
    max_dim = max(size.x, size.y, size.z)
    min_dim = min(size.x, size.y, size.z)
    is_2x1 = (max_dim > min_dim * 1.4)

    if is_2x1:
        # Xác định trục dài của khối 2x1x1
        if size.y >= max_dim - 0.01:
            # Khối đứng dọc theo trục Y (đường nối nằm ngang trên mặt phẳng XZ)
            sub_sz = rl.Vector3(size.x, size.y * 0.5, size.z)
            p1 = rl.Vector3(pos.x, pos.y - size.y * 0.25, pos.z)
            p2 = rl.Vector3(pos.x, pos.y + size.y * 0.25, pos.z)
            # Vòng chỉ phân tách ở giữa (nhô nhẹ 0.006 ra ngoài mặt khối để không bị hiện tượng Z-fighting)
            ring_outer = rl.Vector3(size.x + 0.006, 0.008, size.z + 0.006)
            band_subtle = rl.Vector3(size.x + 0.004, 0.016, size.z + 0.004)
        elif size.x >= max_dim - 0.01:
            # Khối nằm ngang theo trục X (đường nối nằm trên mặt phẳng YZ)
            sub_sz = rl.Vector3(size.x * 0.5, size.y, size.z)
            p1 = rl.Vector3(pos.x - size.x * 0.25, pos.y, pos.z)
            p2 = rl.Vector3(pos.x + size.x * 0.25, pos.y, pos.z)
            ring_outer = rl.Vector3(0.008, size.y + 0.006, size.z + 0.006)
            band_subtle = rl.Vector3(0.016, size.y + 0.004, size.z + 0.004)
        else:
            # Khối nằm dọc theo trục Z (đường nối nằm trên mặt phẳng XY)
            sub_sz = rl.Vector3(size.x, size.y, size.z * 0.5)
            p1 = rl.Vector3(pos.x, pos.y, pos.z - size.z * 0.25)
            p2 = rl.Vector3(pos.x, pos.y, pos.z + size.z * 0.25)
            ring_outer = rl.Vector3(size.x + 0.006, size.y + 0.006, 0.008)
            band_subtle = rl.Vector3(size.x + 0.004, size.y + 0.004, 0.016)

        # 2. Khung tinh thể mờ bên trong lòng mỗi nửa 1x1x1
        rl.draw_cube_wires(p1, sub_sz.x * 0.88, sub_sz.y * 0.88, sub_sz.z * 0.88, rl.Color(255, 215, 120, 65))
        rl.draw_cube_wires(p2, sub_sz.x * 0.88, sub_sz.y * 0.88, sub_sz.z * 0.88, rl.Color(255, 215, 120, 65))

        # 3. Đường rãnh nối ở chính giữa: mờ nhẹ, liền mạch, tinh tế tông cam mật ong
        rl.draw_cube(pos, band_subtle.x, band_subtle.y, band_subtle.z, rl.Color(160, 85, 20, 60))
        rl.draw_cube_wires(pos, ring_outer.x, ring_outer.y, ring_outer.z, rl.Color(255, 220, 140, 110))
    else:
        # Khối phân thân 1x1x1 khi đã tách ra
        rl.draw_cube_wires(pos, size.x * 0.88, size.y * 0.88, size.z * 0.88, rl.Color(255, 230, 160, 150))


def draw_contact_shadow():
    """Vẽ bóng đổ mềm chân thực dưới đáy khối hộp trên mặt sàn"""
    game = ctx.game
    if game.is_split:
        for i, (mr, mc) in enumerate(game.mini_blocks):
            if ctx.roll_animating and ctx.roll_info.get("is_mini", False) and i == ctx.roll_info.get("mini_idx", -1):
                piv = ctx.roll_info.get("pivot")
                old_p = ctx.roll_info.get("old_pos")
                ax = ctx.roll_info.get("axis")
                if piv and old_p and ax:
                    rad = math.radians(ctx.roll_angle)
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
    if ctx.roll_animating:
        rad = math.radians(ctx.roll_angle)
        piv = ctx.roll_info.get("pivot")
        old_p = ctx.roll_info.get("old_pos")
        ax = ctx.roll_info.get("axis")
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

        s_old = ctx.roll_info.get("old_size", rl.Vector3(1, 1, 1))
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


def draw_3d_scene(dt):
    """Vẽ toàn bộ bàn cờ đa tầng, công tắc, lỗ đích và khối hộp"""
    game = ctx.game

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
                glow_alpha = int(185 + 70 * math.sin(ctx.spin_timer * 5.0))
                rl.draw_cube_wires(grid_to_world(r, c, y=-0.01), 0.88, 0.02, 0.88, rl.Color(0, 245, 255, glow_alpha))
                rl.draw_cube_wires(grid_to_world(r, c, y=-0.03), 0.74, 0.02, 0.74, rl.Color(0, 210, 255, glow_alpha // 2))

                # Cột sáng năng lượng lượng tử xoay tròn
                beam_pos = grid_to_world(r, c, y=2.2)
                rl.draw_cube(beam_pos, 0.28, 4.4, 0.28, GOAL_BEAM)
                rl.draw_cube_wires(beam_pos, 0.30, 4.4, 0.30, GOAL_BEAM_WIRE)

                # 3 Vòng hào quang năng lượng bay lượn từ lỗ đích lên bầu trời
                for ring_i in range(3):
                    ring_phase = (ctx.spin_timer * 1.5 + ring_i * 1.33) % 4.0
                    ring_y = ring_phase
                    ring_alpha = int(220 * (1.0 - ring_y / 4.0))
                    ring_scale = 0.36 + 0.08 * math.sin(ctx.spin_timer * 4.0 + ring_i)
                    ring_pos = grid_to_world(r, c, y=ring_y)
                    rl.draw_cylinder_wires(ring_pos, ring_scale, ring_scale, 0.03, 16, rl.Color(0, 245, 255, ring_alpha))

            # Ô cam dễ vỡ (Magma Fissure Plate)
            elif t == 3:
                y_drop = 0.0
                if game.status == "LOST" and game.broken_tile == [r, c]:
                    y_drop = ctx.roll_y_offset if ctx.roll_animating else -20.0

                magma_pulse = 0.65 + 0.35 * math.sin(ctx.spin_timer * 4.5 + (r * 1.7 + c * 2.3))
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
            pulse_s = 0.75 + 0.25 * math.sin(ctx.spin_timer * 4.0)
            rl.draw_cylinder(spos_base, 0.38, 0.38, 0.03, 16, rl.Color(38, 52, 60, 255))
            rl.draw_cylinder(spos_top, 0.28, 0.28, 0.09, 16, rl.Color(46, int(210 + 35 * pulse_s), 125, 255))
            rl.draw_cylinder_wires(spos_top, 0.28, 0.28, 0.09, 16, rl.Color(180, 255, 210, 255))
            rl.draw_cylinder_wires(spos_base, 0.44 * pulse_s, 0.44 * pulse_s, 0.01, 16, rl.Color(50, 240, 140, int(115 * pulse_s)))

        elif stype == "heavy":
            # Công tắc nặng chữ X (Đế vuông + Chữ X hồng ngọc Ruby sang trọng)
            pulse_h = 0.75 + 0.25 * math.sin(ctx.spin_timer * 5.0)
            rl.draw_cube(spos_base, 0.76, 0.03, 0.76, rl.Color(38, 52, 60, 255))
            ruby_col = rl.Color(255, int(50 + 20 * pulse_h), int(70 + 20 * pulse_h), 255)
            rl.draw_cube(spos_top, 0.68, 0.09, 0.20, ruby_col)
            rl.draw_cube(spos_top, 0.20, 0.09, 0.68, ruby_col)
            rl.draw_cube_wires(spos_top, 0.68, 0.09, 0.20, rl.Color(255, 180, 190, 255))
            rl.draw_cube_wires(spos_top, 0.20, 0.09, 0.68, rl.Color(255, 180, 190, 255))

        elif stype == "split":
            # Công tắc phân thân (Vòng tròn ngọc lam lượng tử)
            pulse_sp = 0.75 + 0.25 * math.sin(ctx.spin_timer * 6.0)
            rl.draw_cylinder(spos_base, 0.38, 0.38, 0.03, 16, rl.Color(28, 46, 56, 255))
            rl.draw_cylinder(spos_top, 0.27, 0.27, 0.07, 16, rl.Color(0, int(220 + 35 * pulse_sp), 245, 255))
            rl.draw_cylinder_wires(spos_top, 0.27, 0.27, 0.07, 16, rl.Color(190, 255, 255, 255))
            rl.draw_cylinder_wires(spos_base, 0.44 * pulse_sp, 0.44 * pulse_sp, 0.01, 16, rl.Color(0, 240, 255, int(120 * pulse_sp)))

    # ── 4. Bóng đổ tiếp xúc mềm chân thực (Dynamic Contact Shadow) ──
    draw_contact_shadow()

    # ── 5. Dựng khối hộp Bloxorz Deluxe (Khối cam hổ phách & Khối phân thân) ──
    if not game.is_split:
        if ctx.roll_animating and not ctx.roll_info.get("is_mini", False):
            draw_rolling_block(
                ctx.roll_info["pivot"],
                ctx.roll_info["axis"],
                ctx.roll_angle,
                ctx.roll_info["old_pos"],
                ctx.roll_info["old_size"],
                BLOCK_COLOR,
                BLOCK_WIRE,
                ctx.roll_y_offset,
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

            if ctx.roll_animating and ctx.roll_info.get("is_mini", False) and i == ctx.roll_info.get("mini_idx", -1):
                draw_rolling_block(
                    ctx.roll_info["pivot"],
                    ctx.roll_info["axis"],
                    ctx.roll_angle,
                    ctx.roll_info["old_pos"],
                    ctx.roll_info["old_size"],
                    col,
                    wire_col,
                    ctx.roll_y_offset,
                    is_golden=False
                )
            else:
                if not (game.status == "LOST" and is_active):
                    mpos = grid_to_world(mr, mc, y=0.46)
                    draw_deluxe_block(mpos, rl.Vector3(0.92, 0.92, 0.92), col, wire_col, is_golden=False)

            # Vòng hào quang xoay lơ lửng trên khối đang chọn
            if is_active and not (game.status == "LOST"):
                halo_y = 1.25 + math.sin(ctx.spin_timer * 4.0) * 0.06
                halo_pos = grid_to_world(mr, mc, y=halo_y)
                rl.draw_cylinder_wires(halo_pos, 0.32, 0.32, 0.04, 16, rl.Color(255, 235, 90, 255))
                rl.draw_cylinder_wires(halo_pos, 0.40, 0.40, 0.02, 16, rl.Color(255, 210, 50, 150))

    # ── 6. Hiệu ứng hạt va đập & tia lửa phát sáng trong không gian 3D ──
    update_and_draw_particles(dt)
