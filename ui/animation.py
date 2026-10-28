import math
try:
    import pyray as rl
except ImportError:
    from raylib import pyray as rl

from app_state import ctx
from ui.effects import spawn_impact_sparks
from audio_manager import play_sfx


def _play_move_sound(game):
    """Phát hiệu ứng âm thanh tương ứng với kết quả của bước lăn khối"""
    if game.status == "LOST":
        if game.lost_reason == "FRAGILE_BREAK":
            play_sfx("lose_break")
        else:
            play_sfx("lose_fall")
    elif game.status == "WON":
        play_sfx("level_win")
    elif game.status == "PLAYING":
        if game.last_event == "SPLIT":
            play_sfx("block_split")
        elif game.last_event == "MERGE":
            play_sfx("block_merge")
        elif game.last_event == "SWITCH_TRIGGER":
            if getattr(game, "last_switch_type", "soft") == "heavy":
                play_sfx("switch_heavy")
            else:
                play_sfx("switch_soft")
        else:
            if not game.is_split:
                (r1, c1), (r2, c2) = game.block.state
                tiles = [[r1, c1], [r2, c2]]
                on_fragile = game.is_fragile(r1, c1) or game.is_fragile(r2, c2)
                on_heavy_deny = (not game.block.is_standing()) and any(
                    s.get("type") == "heavy" and s.get("pos") in tiles for s in game.switches
                )
            else:
                mr, mc = game.mini_blocks[game.active_block]
                on_fragile = game.is_fragile(mr, mc)
                on_heavy_deny = False

            if on_fragile:
                play_sfx("fragile_warn")
            elif on_heavy_deny:
                play_sfx("switch_deny")
            else:
                play_sfx("block_roll")


def grid_to_world(r, c, y=0.0):
    """Hệ tọa độ chuẩn: X=c (ngang), Y=y (cao), Z=r (dọc)"""
    return rl.Vector3(float(c), float(y), float(r))


def get_block_target_transform():
    """Tính toán kích thước và vị trí của khối hộp ở trạng thái tĩnh"""
    if not ctx.game.is_split:
        (r1, c1), (r2, c2) = ctx.game.block.state
        if ctx.game.block.is_standing():
            scale = rl.Vector3(0.92, 1.92, 0.92)
            y_base = 0.35 if ctx.game.status == "WON" else 0.96
            pos = grid_to_world(r1, c1, y=y_base)
        elif ctx.game.block.is_horizontal():
            scale = rl.Vector3(1.92, 0.92, 0.92)
            pos = grid_to_world(r1, (c1 + c2) / 2.0, y=0.46)
        else: # is_vertical
            scale = rl.Vector3(0.92, 0.92, 1.92)
            pos = grid_to_world((r1 + r2) / 2.0, c1, y=0.46)
        return pos, scale
    return None, None


def compute_roll_params_block(state, is_standing, is_horizontal, is_vertical, move_dir):
    """Tính toán trục quay và cạnh lật trên mặt sàn cho khối 1x1x2"""
    (r1, c1), (r2, c2) = state
    if is_standing:
        r, c = r1, c1
        old_pos = grid_to_world(r, c, y=0.96)
        old_size = rl.Vector3(0.92, 1.92, 0.92)
        if move_dir == "RIGHT":
            pivot = rl.Vector3(float(c) + 0.5, 0.0, float(r))
            axis = rl.Vector3(0.0, 0.0, -1.0)
        elif move_dir == "LEFT":
            pivot = rl.Vector3(float(c) - 0.5, 0.0, float(r))
            axis = rl.Vector3(0.0, 0.0, 1.0)
        elif move_dir == "UP":
            pivot = rl.Vector3(float(c), 0.0, float(r) - 0.5)
            axis = rl.Vector3(-1.0, 0.0, 0.0)
        else: # DOWN
            pivot = rl.Vector3(float(c), 0.0, float(r) + 0.5)
            axis = rl.Vector3(1.0, 0.0, 0.0)
    elif is_horizontal:
        r = r1
        min_c = min(c1, c2)
        max_c = max(c1, c2)
        center_c = (min_c + max_c) / 2.0
        old_pos = grid_to_world(r, center_c, y=0.46)
        old_size = rl.Vector3(1.92, 0.92, 0.92)
        if move_dir == "RIGHT":
            pivot = rl.Vector3(float(max_c) + 0.5, 0.0, float(r))
            axis = rl.Vector3(0.0, 0.0, -1.0)
        elif move_dir == "LEFT":
            pivot = rl.Vector3(float(min_c) - 0.5, 0.0, float(r))
            axis = rl.Vector3(0.0, 0.0, 1.0)
        elif move_dir == "UP":
            pivot = rl.Vector3(float(center_c), 0.0, float(r) - 0.5)
            axis = rl.Vector3(-1.0, 0.0, 0.0)
        else: # DOWN
            pivot = rl.Vector3(float(center_c), 0.0, float(r) + 0.5)
            axis = rl.Vector3(1.0, 0.0, 0.0)
    else: # is_vertical
        c = c1
        min_r = min(r1, r2)
        max_r = max(r1, r2)
        center_r = (min_r + max_r) / 2.0
        old_pos = grid_to_world(center_r, c, y=0.46)
        old_size = rl.Vector3(0.92, 0.92, 1.92)
        if move_dir == "RIGHT":
            pivot = rl.Vector3(float(c) + 0.5, 0.0, float(center_r))
            axis = rl.Vector3(0.0, 0.0, -1.0)
        elif move_dir == "LEFT":
            pivot = rl.Vector3(float(c) - 0.5, 0.0, float(center_r))
            axis = rl.Vector3(0.0, 0.0, 1.0)
        elif move_dir == "UP":
            pivot = rl.Vector3(float(c), 0.0, float(min_r) - 0.5)
            axis = rl.Vector3(-1.0, 0.0, 0.0)
        else: # DOWN
            pivot = rl.Vector3(float(c), 0.0, float(max_r) + 0.5)
            axis = rl.Vector3(1.0, 0.0, 0.0)
    return old_pos, old_size, pivot, axis


def compute_roll_params_mini(r, c, move_dir):
    """Tính toán trục quay và cạnh lật trên mặt sàn cho khối nhỏ 1x1x1"""
    old_pos = grid_to_world(r, c, y=0.46)
    old_size = rl.Vector3(0.92, 0.92, 0.92)
    if move_dir == "RIGHT":
        pivot = rl.Vector3(float(c) + 0.5, 0.0, float(r))
        axis = rl.Vector3(0.0, 0.0, -1.0)
    elif move_dir == "LEFT":
        pivot = rl.Vector3(float(c) - 0.5, 0.0, float(r))
        axis = rl.Vector3(0.0, 0.0, 1.0)
    elif move_dir == "UP":
        pivot = rl.Vector3(float(c), 0.0, float(r) - 0.5)
        axis = rl.Vector3(-1.0, 0.0, 0.0)
    else: # DOWN
        pivot = rl.Vector3(float(c), 0.0, float(r) + 0.5)
        axis = rl.Vector3(1.0, 0.0, 0.0)
    return old_pos, old_size, pivot, axis


def perform_move(move_dir):
    """Thực hiện bước đi và kích hoạt hiệu ứng xoay lật 90 độ vật lý quanh mép sàn"""
    if ctx.game.status != "PLAYING":
        return

    old_is_split = ctx.game.is_split
    if not old_is_split:
        old_state = ctx.game.block.state
        old_standing = ctx.game.block.is_standing()
        old_horizontal = ctx.game.block.is_horizontal()
        old_vertical = ctx.game.block.is_vertical()
    else:
        old_mini_pos = list(ctx.game.mini_blocks[ctx.game.active_block])
        old_active_idx = ctx.game.active_block

    res = ctx.game.move(move_dir)
    _play_move_sound(ctx.game)

    if res == "SPLIT" or ctx.game.last_event == "MERGE":
        ctx.roll_animating = False
        ctx.roll_angle = 0.0
        ctx.roll_y_offset = 0.0
        return

    if not old_is_split:
        p_old, s_old, pivot, axis = compute_roll_params_block(
            old_state, old_standing, old_horizontal, old_vertical, move_dir
        )
        is_mini = False
        mini_idx = -1
    else:
        p_old, s_old, pivot, axis = compute_roll_params_mini(
            old_mini_pos[0], old_mini_pos[1], move_dir
        )
        is_mini = True
        mini_idx = old_active_idx

    ctx.anim_time = 0.0
    if ctx.game.status == "LOST":
        ctx.anim_duration = 0.48
    elif ctx.game.status == "WON":
        ctx.anim_duration = 0.38
        pos_win, _ = get_block_target_transform()
        if pos_win:
            spawn_impact_sparks(pos_win.x, pos_win.z, count=36, is_gold=False)
    else:
        ctx.anim_duration = 0.14

    ctx.roll_angle = 0.0
    ctx.roll_y_offset = 0.0
    ctx.roll_info = {
        "is_mini": is_mini,
        "mini_idx": mini_idx,
        "old_pos": p_old,
        "old_size": s_old,
        "pivot": pivot,
        "axis": axis,
        "status": ctx.game.status,
        "lost_reason": ctx.game.lost_reason,
    }
    ctx.roll_animating = True


def update_roll_animation(dt):
    """Cập nhật tiến trình xoay lật vật lý quanh cạnh đáy (Tumble Animation)"""
    if not ctx.roll_animating:
        return

    ctx.anim_time += dt
    p = min(1.0, ctx.anim_time / ctx.anim_duration)
    status = ctx.roll_info.get("status", "PLAYING")
    lost_reason = ctx.roll_info.get("lost_reason", None)

    if status == "LOST":
        if lost_reason == "FALL":
            if p <= 0.35:
                e = p / 0.35
                ctx.roll_angle = 90.0 * (e * e * (3.0 - 2.0 * e))
                ctx.roll_y_offset = 0.0
            else:
                p_fall = (p - 0.35) / 0.65
                ctx.roll_angle = 90.0 + 130.0 * p_fall
                ctx.roll_y_offset = -22.0 * (p_fall * p_fall)
        elif lost_reason == "FRAGILE_BREAK":
            ctx.roll_angle = 0.0
            ctx.roll_y_offset = -20.0 * (p * p)
        else:  # BRIDGE_CLOSED
            ctx.roll_angle = 0.0
            ctx.roll_y_offset = -20.0 * (p * p)
    elif status == "WON":
        if p <= 0.45:
            e = p / 0.45
            ctx.roll_angle = 90.0 * (e * e * (3.0 - 2.0 * e))
            ctx.roll_y_offset = 0.0
        else:
            ctx.roll_angle = 90.0
            p_win = (p - 0.45) / 0.55
            ctx.roll_y_offset = -0.65 * math.sin(p_win * math.pi / 2.0)
    else:  # PLAYING
        e = p * p * (3.0 - 2.0 * p)
        ctx.roll_angle = 90.0 * e
        ctx.roll_y_offset = 0.0

    if p >= 1.0:
        ctx.roll_animating = False
        ctx.roll_angle = 0.0
        ctx.roll_y_offset = 0.0

        # Kích hoạt tia lửa & bụi tiếp đất khi lăn thành công
        if ctx.game.status in ("PLAYING", "WON"):
            if not ctx.game.is_split:
                pos, _ = get_block_target_transform()
                if pos:
                    spawn_impact_sparks(pos.x, pos.z, count=16, is_gold=True)
            else:
                if 0 <= ctx.game.active_block < len(ctx.game.mini_blocks):
                    mr, mc = ctx.game.mini_blocks[ctx.game.active_block]
                    spawn_impact_sparks(float(mc), float(mr), count=12, is_gold=False)

        if ctx.game.status == "PLAYING" and ctx.buffered_move is not None:
            next_m = ctx.buffered_move
            ctx.buffered_move = None
            perform_move(next_m)

