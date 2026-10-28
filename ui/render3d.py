# ui/render3d.py
"""
Bloxorz 3D - Bộ dựng hình không gian 3D (3D Renderer)
Vẽ bàn cờ đa tầng, ô đích, công tắc, bóng đổ tiếp xúc và Hệ thống 4 Skin Khối Đặc Đa Tầng.
"""

import math
import pyray as rl
from config import (
    PEDESTAL_COLOR, TILE_TOP_A, TILE_TOP_B, WIRE_COLOR,
    FRAGILE_TOP, FRAGILE_BASE, BRIDGE_TOP, BRIDGE_BASE,
    GOAL_HOLE, GOAL_BEAM, GOAL_BEAM_WIRE,
    BLOCK_COLOR, BLOCK_WIRE,
    MINI_ACTIVE, MINI_ACTIVE_WIRE, MINI_IDLE, MINI_IDLE_WIRE,
    BLOCK_SKINS, get_skin_accent_color
)
from app_state import ctx
from ui.animation import grid_to_world, get_block_target_transform
from ui.effects import draw_starfield, update_and_draw_particles


def _adj_col(col, is_split_mode=False, is_active=True):
    """Điều chỉnh độ sáng cho khối phân thân: rực rỡ khi đang chọn, dịu hơn khi nghỉ (giữ nguyên alpha=255)"""
    if not is_split_mode:
        return col
    if is_active:
        return rl.Color(
            min(255, col.r + 18),
            min(255, col.g + 18),
            min(255, col.b + 18),
            col.a
        )
    return rl.Color(
        int(col.r * 0.65),
        int(col.g * 0.65),
        int(col.b * 0.65),
        col.a
    )


def _draw_6face_plates(sub_pos, sub_sz, plate_ratio, protrude, plate_col, wire_col=None):
    """
    Vẽ 6 tấm ốp nổi trên 6 mặt (+X, -X, +Y, -Y, +Z, -Z) của nửa khối `sub_pos`
    bằng kỹ thuật giao 3 khối hộp chữ nhật đặc đi qua tâm `sub_pos`.
    Để lộ toàn bộ 12 cạnh vát + 8 góc của khối lõi bên dưới và tuyệt đối không bị Z-fighting.
    """
    sx, sy, sz = sub_sz.x, sub_sz.y, sub_sz.z

    # Khối trục X (+X / -X)
    wx, wy, wz = sx * protrude, sy * plate_ratio, sz * plate_ratio
    rl.draw_cube(sub_pos, wx, wy, wz, plate_col)
    if wire_col is not None:
        rl.draw_cube_wires(sub_pos, wx, wy, wz, wire_col)

    # Khối trục Y (+Y / -Y) - chênh nhẹ 0.002 ở plate_ratio để tránh trùng mặt bên với trục X/Z
    r_y = plate_ratio - 0.002
    wx, wy, wz = sx * r_y, sy * protrude, sz * r_y
    rl.draw_cube(sub_pos, wx, wy, wz, plate_col)
    if wire_col is not None:
        rl.draw_cube_wires(sub_pos, wx, wy, wz, wire_col)

    # Khối trục Z (+Z / -Z) - chênh nhẹ 0.004 ở plate_ratio
    r_z = plate_ratio - 0.004
    wx, wy, wz = sx * r_z, sy * r_z, sz * protrude
    rl.draw_cube(sub_pos, wx, wy, wz, plate_col)
    if wire_col is not None:
        rl.draw_cube_wires(sub_pos, wx, wy, wz, wire_col)


def draw_armored_half_cube(sub_pos, sub_sz, skin_idx, half_idx=0, is_split_mode=False, is_active=True):
    """
    Hàm vẽ chi tiết cấu trúc Khối Đặc Đa Tầng (Solid Core + Surface Armor Plates / Cracks)
    trên từng nửa khối 1x1x1 tại `sub_pos` với kích thước `sub_sz`.
    """
    t = ctx.spin_timer
    sx, sy, sz = sub_sz.x, sub_sz.y, sub_sz.z

    if skin_idx == 1:
        # ══════════════════════════════════════════════════════════════════
        # SKIN 1 — "NHAM THẠCH HỎA LONG" (Molten Magma)
        # Lõi dung nham đặc sôi sục + Vỏ đá núi lửa Obsidian đen nứt vỡ + Mạch chữ thập rực cháy
        # ══════════════════════════════════════════════════════════════════
        pulse = 0.5 + 0.5 * math.sin(t * 5.5 + half_idx * 0.9)
        lava_core = _adj_col(
            rl.Color(255, int(115 + 110 * pulse), int(15 + 45 * pulse), 255),
            is_split_mode, is_active
        )
        lava_wire = _adj_col(rl.Color(255, 240, 150, 255), is_split_mode, is_active)
        obsidian_col = _adj_col(rl.Color(26, 20, 22, 255), is_split_mode, is_active)
        crust_wire = _adj_col(rl.Color(120, 45, 20, 255), is_split_mode, is_active)
        lava_vein = _adj_col(
            rl.Color(255, int(165 + 80 * pulse), 30, 255),
            is_split_mode, is_active
        )

        # 1. Khối Lõi Dung Nham Đặc (alpha = 255) ở tỷ lệ 0.95
        rl.draw_cube(sub_pos, sx * 0.95, sy * 0.95, sz * 0.95, lava_core)
        rl.draw_cube_wires(sub_pos, sx * 0.95, sy * 0.95, sz * 0.95, lava_wire)

        # 2. Lớp Vỏ Đá Núi Lửa Obsidian Đặc (plate_ratio = 0.78, nhô 1.005)
        _draw_6face_plates(sub_pos, sub_sz, 0.78, 1.005, obsidian_col, crust_wire)

        # 3. Các mạch nứt dung nham chữ thập cắt ngang tâm 6 mặt (chia mỗi mặt thành 4 mảng đá)
        vein_w = 0.14
        vein_len = 0.80
        # Mạch chữ thập trên mặt +X / -X (nhô 1.015)
        rl.draw_cube(sub_pos, sx * 1.015, sy * vein_len, sz * vein_w, lava_vein)
        rl.draw_cube(sub_pos, sx * 1.014, sy * vein_w, sz * vein_len, lava_vein)
        # Mạch chữ thập trên mặt +Y / -Y
        rl.draw_cube(sub_pos, sx * vein_len, sy * 1.015, sz * vein_w, lava_vein)
        rl.draw_cube(sub_pos, sx * vein_w, sy * 1.014, sz * vein_len, lava_vein)
        # Mạch chữ thập trên mặt +Z / -Z
        rl.draw_cube(sub_pos, sx * vein_len, sy * vein_w, sz * 1.015, lava_vein)
        rl.draw_cube(sub_pos, sx * vein_w, sy * vein_len, sz * 1.014, lava_vein)

        # Tâm điểm nóng trắng vàng ở chính giữa mỗi mặt
        hot_center = _adj_col(rl.Color(255, int(215 + 40 * pulse), 110, 255), is_split_mode, is_active)
        _draw_6face_plates(sub_pos, sub_sz, 0.22, 1.018, hot_center, None)

    elif skin_idx == 2:
        # ══════════════════════════════════════════════════════════════════
        # SKIN 2 — "CỰC QUANG ĐA SẮC" (Prismatic Aurora)
        # Cyber-Neon Hologram đa tầng trên nền tối đặc sâu thẳm, 2 nửa khối lệch pha sóng ánh sáng
        # ══════════════════════════════════════════════════════════════════
        phase = t * 3.0 + half_idx * 1.8
        r = max(0, min(255, int(130 + 125 * math.sin(phase))))
        g = max(0, min(255, int(140 + 115 * math.sin(phase + 2.094))))
        b = max(0, min(255, int(185 + 70 * math.sin(phase + 4.188))))

        phase_sub = phase + 1.4
        r2 = max(0, min(255, int(130 + 125 * math.sin(phase_sub))))
        g2 = max(0, min(255, int(140 + 115 * math.sin(phase_sub + 2.094))))
        b2 = max(0, min(255, int(185 + 70 * math.sin(phase_sub + 4.188))))

        c_main = _adj_col(rl.Color(r, g, b, 255), is_split_mode, is_active)
        c_sub = _adj_col(rl.Color(r2, g2, b2, 255), is_split_mode, is_active)
        dark_base = _adj_col(rl.Color(12, 14, 30, 255), is_split_mode, is_active)
        tier1_col = _adj_col(rl.Color(r // 3, g // 3, b // 3, 255), is_split_mode, is_active)
        ice_white = _adj_col(rl.Color(235, 250, 255, 255), is_split_mode, is_active)

        # 1. Thân Khối Nền Đen Tím Vũ Trụ Đặc (0.92)
        rl.draw_cube(sub_pos, sx * 0.92, sy * 0.92, sz * 0.92, dark_base)

        # 2. Tầng 1: Ốp 6 mặt tại plate_ratio = 0.80, nhô 0.95 với màu tối ánh cực quang & viền c_main
        _draw_6face_plates(sub_pos, sub_sz, 0.80, 0.95, tier1_col, c_main)

        # 3. Tầng 2: Ốp 6 mặt tại plate_ratio = 0.52, nhô 0.98 với màu c_sub rực rỡ & viền trắng băng
        _draw_6face_plates(sub_pos, sub_sz, 0.52, 0.98, c_sub, ice_white)

        # 4. Khung viền lồng ngoài: 2 lớp draw_cube_wires ở 1.0 (c_main) và 0.96 (c_sub)
        rl.draw_cube_wires(sub_pos, sx * 1.0, sy * 1.0, sz * 1.0, c_main)
        rl.draw_cube_wires(sub_pos, sx * 0.96, sy * 0.96, sz * 0.96, c_sub)

    elif skin_idx == 3:
        # ══════════════════════════════════════════════════════════════════
        # SKIN 3 — "HẮC TINH HỐ ĐEN" (Void Singularity)
        # Lõi Năng Lượng Tím Tử Quang Đặc + Giáp Hắc Ám Vũ Trụ + Tâm Hố Đen phát xung
        # ══════════════════════════════════════════════════════════════════
        pulse = 0.5 + 0.5 * math.sin(t * 5.0 + half_idx * 1.2)
        void_core_col = _adj_col(rl.Color(175, 55, 255, 255), is_split_mode, is_active)
        core_wire_col = _adj_col(rl.Color(235, 175, 255, 255), is_split_mode, is_active)
        dark_armor_col = _adj_col(rl.Color(10, 6, 18, 255), is_split_mode, is_active)
        neon_purple_wire = _adj_col(rl.Color(210, 110, 255, 255), is_split_mode, is_active)
        singularity_col = _adj_col(
            rl.Color(int(205 + 50 * pulse), int(145 + 100 * pulse), 255, 255),
            is_split_mode, is_active
        )
        silver_wire = _adj_col(rl.Color(245, 248, 255, 255), is_split_mode, is_active)

        # 1. Lõi Năng Lượng Tím Tử Quang Đặc ở tỷ lệ 0.93
        rl.draw_cube(sub_pos, sx * 0.93, sy * 0.93, sz * 0.93, void_core_col)
        rl.draw_cube_wires(sub_pos, sx * 0.93, sy * 0.93, sz * 0.93, core_wire_col)

        # 2. Giáp Hắc Ám Vũ Trụ: Ốp 6 mặt với plate_ratio = 0.78, nhô 0.97
        _draw_6face_plates(sub_pos, sub_sz, 0.78, 0.97, dark_armor_col, neon_purple_wire)

        # 3. Tâm Hố Đen trên mỗi mặt: plate_ratio = 0.34, nhô 0.995 màu trắng tím phát xung
        _draw_6face_plates(sub_pos, sub_sz, 0.34, 0.995, singularity_col, silver_wire)
        rl.draw_cube_wires(sub_pos, sx * 1.0, sy * 1.0, sz * 1.0, neon_purple_wire)


def draw_deluxe_block(pos, size, color=None, wire_color=None, is_golden=True, is_active=None):
    """
    Vẽ khối 3D theo Hệ thống 4 Skin Khối Đặc Đa Tầng (BLOCK_SKINS[ctx.current_skin_idx]).
    Không dùng vỏ trong suốt hay tấm phẳng cắt ngang ruột khối.
    """
    skin_idx = ctx.current_skin_idx % len(BLOCK_SKINS)
    t = ctx.spin_timer

    max_dim = max(size.x, size.y, size.z)
    min_dim = min(size.x, size.y, size.z)
    is_2x1 = (max_dim > min_dim * 1.4)
    is_split_mode = not is_2x1

    if is_active is None:
        if is_split_mode:
            is_active = bool(is_golden) or (color == MINI_ACTIVE)
        else:
            is_active = True

    # ── SKIN 0: HOÀNG KIM NGUYÊN BẢN (Imperial Gold) ──
    if skin_idx == 0:
        base_col = _adj_col(rl.Color(240, 140, 30, 255), is_split_mode, is_active)
        outer_wire = _adj_col(rl.Color(255, 205, 110, 240), is_split_mode, is_active)

        rl.draw_cube(pos, size.x, size.y, size.z, base_col)
        rl.draw_cube_wires(pos, size.x, size.y, size.z, outer_wire)

        if is_2x1:
            if size.y >= max_dim - 0.01:
                ring_outer = rl.Vector3(size.x + 0.006, 0.008, size.z + 0.006)
            elif size.x >= max_dim - 0.01:
                ring_outer = rl.Vector3(0.008, size.y + 0.006, size.z + 0.006)
            else:
                ring_outer = rl.Vector3(size.x + 0.006, size.y + 0.006, 0.008)
            # Chỉ vẽ viền rãnh ở mép ngoài bằng draw_cube_wires, không vẽ tấm phẳng cắt ngang ruột khối
            rl.draw_cube_wires(pos, ring_outer.x, ring_outer.y, ring_outer.z, rl.Color(255, 220, 140, 165))
        return

    # ── CÁC SKIN 1, 2, 3: CẤU TRÚC KHỐI ĐẶC ĐA TẦNG (Solid Core + 6-Face Armor Plates) ──
    if is_2x1:
        if size.y >= max_dim - 0.01:
            sub_sz = rl.Vector3(size.x, size.y * 0.5, size.z)
            p1 = rl.Vector3(pos.x, pos.y - size.y * 0.25, pos.z)
            p2 = rl.Vector3(pos.x, pos.y + size.y * 0.25, pos.z)
            ring_outer = rl.Vector3(size.x * 0.96, 0.04, size.z * 0.96)
        elif size.x >= max_dim - 0.01:
            sub_sz = rl.Vector3(size.x * 0.5, size.y, size.z)
            p1 = rl.Vector3(pos.x - size.x * 0.25, pos.y, pos.z)
            p2 = rl.Vector3(pos.x + size.x * 0.25, pos.y, pos.z)
            ring_outer = rl.Vector3(0.04, size.y * 0.96, size.z * 0.96)
        else:
            sub_sz = rl.Vector3(size.x, size.y, size.z * 0.5)
            p1 = rl.Vector3(pos.x, pos.y, pos.z - size.z * 0.25)
            p2 = rl.Vector3(pos.x, pos.y, pos.z + size.z * 0.25)
            ring_outer = rl.Vector3(size.x * 0.96, size.y * 0.96, 0.04)

        draw_armored_half_cube(p1, sub_sz, skin_idx, half_idx=0, is_split_mode=False, is_active=True)
        draw_armored_half_cube(p2, sub_sz, skin_idx, half_idx=1, is_split_mode=False, is_active=True)

        # Rãnh giữa 2 nửa khối
        if skin_idx == 1:
            # Mạch dung nham rực sáng màu Vàng Cam ở giữa 2 nửa khối
            pulse = 0.5 + 0.5 * math.sin(t * 5.5)
            rl.draw_cube(pos, ring_outer.x, ring_outer.y, ring_outer.z, rl.Color(255, 190, 40, 255))
            rl.draw_cube_wires(pos, ring_outer.x + 0.01, ring_outer.y + 0.005, ring_outer.z + 0.01, rl.Color(255, int(210 + 45 * pulse), 120, 255))
        elif skin_idx == 2:
            # Viền năng lượng Cực Quang nối giữa 2 nửa
            seam_col = get_skin_accent_color(2, t + 0.9, alpha=255)
            rl.draw_cube_wires(pos, ring_outer.x + 0.02, ring_outer.y, ring_outer.z + 0.02, seam_col)
        elif skin_idx == 3:
            # Đai Hố Đen Tím Tử Quang ở rãnh giữa
            rl.draw_cube(pos, ring_outer.x, ring_outer.y, ring_outer.z, rl.Color(195, 75, 255, 255))
            rl.draw_cube_wires(pos, ring_outer.x + 0.01, ring_outer.y + 0.005, ring_outer.z + 0.01, rl.Color(240, 210, 255, 255))
    else:
        # Khối nhỏ 1x1x1 khi ở chế độ phân thân (is_split == True)
        draw_armored_half_cube(pos, size, skin_idx, half_idx=0, is_split_mode=True, is_active=is_active)


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


def draw_rolling_block(pivot, axis, angle_deg, pos, size, color, wire_color, y_offset=0.0, is_golden=True, is_active=None):
    """Vẽ khối hộp đang xoay lật quanh cạnh sàn bằng biến đổi ma trận rlgl"""
    rl.rl_push_matrix()
    rl.rl_translatef(pivot.x, pivot.y + y_offset, pivot.z)
    rl.rl_rotatef(angle_deg, axis.x, axis.y, axis.z)
    rl.rl_translatef(-pivot.x, -pivot.y, -pivot.z)

    draw_deluxe_block(pos, size, color, wire_color, is_golden=is_golden, is_active=is_active)

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

    # ── 5. Dựng khối hộp Bloxorz 3D (Áp dụng Hệ thống 4 Skin Khối Đặc Đa Tầng) ──
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
                is_golden=True,
                is_active=True
            )
        else:
            if not (game.status == "LOST" and game.lost_reason in ("FALL", "FRAGILE_BREAK", "BRIDGE_CLOSED")):
                pos, scale = get_block_target_transform()
                if pos:
                    draw_deluxe_block(pos, scale, BLOCK_COLOR, BLOCK_WIRE, is_golden=True, is_active=True)
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
                    is_golden=is_active,
                    is_active=is_active
                )
            else:
                if not (game.status == "LOST" and is_active):
                    mpos = grid_to_world(mr, mc, y=0.46)
                    draw_deluxe_block(
                        mpos,
                        rl.Vector3(0.92, 0.92, 0.92),
                        col,
                        wire_col,
                        is_golden=is_active,
                        is_active=is_active
                    )

            # Vòng hào quang xoay lơ lửng trên đầu khối đang được chọn (mang màu chủ đạo của Skin hiện tại)
            if is_active and not (game.status == "LOST"):
                halo_y = 1.25 + math.sin(ctx.spin_timer * 4.0) * 0.06
                halo_pos = grid_to_world(mr, mc, y=halo_y)
                halo_primary = get_skin_accent_color(ctx.current_skin_idx, ctx.spin_timer, alpha=255)
                halo_secondary = get_skin_accent_color(ctx.current_skin_idx, ctx.spin_timer + 1.0, alpha=160)
                rl.draw_cylinder_wires(halo_pos, 0.32, 0.32, 0.04, 16, halo_primary)
                rl.draw_cylinder_wires(halo_pos, 0.40, 0.40, 0.02, 16, halo_secondary)

    # ── 6. Hiệu ứng hạt va đập & tia lửa phát sáng trong không gian 3D ──
    update_and_draw_particles(dt)
