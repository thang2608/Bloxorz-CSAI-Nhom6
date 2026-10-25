# solvers/ucs_solver.py — Thuật toán tìm kiếm Uniform Cost Search (UCS)
from heapq import heappop, heappush
from itertools import count
import time
import tracemalloc
from game import BloxorzGame
from .base import (
    extract_state,
    get_next_state,
    get_valid_actions,
    reconstruct_moves,
)


def solve_ucs(game_or_level=0) -> dict | None:
    """
    Chạy thuật toán Uniform Cost Search (UCS / Dijkstra).
    Hỗ trợ nhận vào đối tượng BloxorzGame (dùng cho UI)
    hoặc số nguyên level_index (dùng cho CLI test độc lập).
    """
    if isinstance(game_or_level, int):
        game = BloxorzGame(game_or_level)
    else:
        game = game_or_level

    if game.status != "PLAYING":
        return None

    tracemalloc.start()
    start_time = time.perf_counter()

    initial_state = extract_state(game)
    sequence = count()
    
    # Priority Queue lưu: (cost, tie_breaker, state)
    frontier = [(0, next(sequence), initial_state)]
    best_cost = {initial_state: 0}
    parents = {}
    nodes_expanded = 0

    goal_reached_state = None

    while frontier:
        cost, _, state = heappop(frontier)

        if cost > best_cost.get(state, float("inf")):
            continue

        nodes_expanded += 1

        for action in get_valid_actions(state):
            next_state, is_won = get_next_state(game, state, action)
            if next_state is None:
                continue

            step_cost = 0.1 if action == "SWITCH" else 1.0
            next_cost = cost + step_cost

            if next_cost >= best_cost.get(next_state, float("inf")):
                continue

            best_cost[next_state] = next_cost
            parents[next_state] = (state, action)

            if is_won:
                goal_reached_state = next_state
                break

            heappush(frontier, (next_cost, next(sequence), next_state))

        if goal_reached_state is not None:
            break

    elapsed = time.perf_counter() - start_time
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if goal_reached_state is not None:
        moves = reconstruct_moves(parents, goal_reached_state)
        total_cost = len([m for m in moves if m != "SWITCH"])
        return {
            "algorithm": "UCS",
            "found": True,
            "moves": moves,
            "path": moves,
            "solution_length": len(moves),
            "total_cost": total_cost,
            "search_time": elapsed,
            "search_time_seconds": elapsed,
            "memory_usage": peak_mem,
            "peak_memory_mb": peak_mem / (1024 * 1024),
            "nodes_expanded": nodes_expanded,
            "expanded_nodes": nodes_expanded,
        }

    return {
        "algorithm": "UCS",
        "found": False,
        "moves": [],
        "path": [],
        "solution_length": 0,
        "total_cost": 0,
        "search_time_seconds": elapsed,
        "peak_memory_mb": peak_mem / (1024 * 1024),
        "nodes_expanded": nodes_expanded,
        "expanded_nodes": nodes_expanded,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Chạy thuật toán UCS giải game Bloxorz")
    parser.add_argument("--level", type=int, default=0, help="Màn chơi (bắt đầu từ 0)")
    args = parser.parse_args()

    res = solve_ucs(args.level)

    print(f"\n--- KẾT QUẢ UCS (Level {args.level}) ---")
    if res and res.get("found"):
        print("Đường đi:", " -> ".join(res["path"]))
        print("Số bước:", res["solution_length"])
        print("Tổng chi phí:", res["total_cost"])
    else:
        print("Không tìm thấy lời giải!")

    if res:
        print(f"Số node đã mở rộng: {res['nodes_expanded']}")
        print(f"Thời gian chạy: {res['search_time_seconds']:.6f} s")
        print(f"Bộ nhớ đỉnh: {res['peak_memory_mb']:.4f} MB")