# ai_controller.py
"""
Bloxorz 3D - Bộ điều khiển thuật toán AI (AI Controller)
Kết nối trò chơi với các bộ giải thông minh (A*, BFS, DFS, IDS, UCS).
"""

import pyray as rl
from solvers import AVAILABLE_SOLVERS
from app_state import ctx
from audio_manager import play_sfx


def trigger_ai_solve(algo_name=None):
    """Tìm đường bằng thuật toán (nếu có truyền tên) và tự động nạp danh sách nước đi"""
    ctx.show_solvers_dropdown = False  # Đóng menu dropdown sau khi chọn

    if ctx.game.status != "PLAYING":
        return

    # Nếu AI đang chạy tự động mà bấm vào nút chính thì dừng lại
    if ctx.ai_move_queue and algo_name is None:
        ctx.ai_move_queue.clear()
        return

    # Nếu người chơi click chọn một thuật toán cụ thể từ dropdown menu
    if algo_name is not None and algo_name in ctx.solver_names:
        ctx.current_solver_idx = ctx.solver_names.index(algo_name)

    chosen_algo = ctx.solver_names[ctx.current_solver_idx]
    solver_fn = AVAILABLE_SOLVERS[chosen_algo]

    print(f"\n[*] Đang tìm đường bằng thuật toán: {chosen_algo}...")
    result = solver_fn(ctx.game)
    if result and result.get("moves"):
        ctx.ai_move_queue = list(result["moves"])
        ctx.ai_stats = result
        print(f"[{chosen_algo}] Đã tìm thấy {len(ctx.ai_move_queue)} bước! (Duyệt {result.get('nodes_expanded', 0)} trạng thái)")
        ctx.show_toast(f"AI ({chosen_algo}): Tìm thấy {len(ctx.ai_move_queue)} bước!", 2.2, rl.Color(65, 245, 160, 255))
    else:
        print(f"[{chosen_algo}] Không tìm thấy đường đi tới đích!")
        play_sfx("ui_back")
        ctx.show_toast(f"AI ({chosen_algo}): Không tìm thấy đường giải từ vị trí này!", 3.0, rl.Color(255, 95, 95, 255))


def cycle_solver():
    """Chuyển đổi tuần tự qua lại giữa các thuật toán có sẵn (A* -> BFS -> DFS -> ...)"""
    ctx.ai_move_queue.clear()  # Dừng AI hiện tại nếu đang chạy
    ctx.current_solver_idx = (ctx.current_solver_idx + 1) % len(ctx.solver_names)
    algo_name = ctx.solver_names[ctx.current_solver_idx]
    print(f"[*] Đã chuyển sang thuật toán: {algo_name}")
    ctx.show_toast(f"Thuật toán AI: {algo_name} (Tab)", 1.5, rl.Color(0, 240, 245, 255))
