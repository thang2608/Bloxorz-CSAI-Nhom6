import copy
import heapq
import time
import tracemalloc
from game import BloxorzGame


def encode_state(game):
    """Chuyển trạng thái hiện tại của game thành tuple bất biến để làm key trong dict."""
    if game.is_split:
        blk_pos = None
        minis = tuple(tuple(p) for p in game.mini_blocks)
        active = game.active_block
    else:
        blk_pos = game.block.state
        minis = ()
        active = 0

    # Phải sort bridges theo id để đảm bảo cùng 1 trạng thái cầu luôn ra cùng 1 tuple
    bridges = tuple((b_id, data["is_open"]) for b_id, data in sorted(game.bridges.items()))

    return (blk_pos, game.is_split, minis, active, bridges)


def solve_ucs(level_index=0):
    tracemalloc.start()
    t0 = time.perf_counter()

    init_game = BloxorzGame(level_index)
    init_key = encode_state(init_game)

    # Hàng đợi ưu tiên lưu: (cost, tie_breaker, state_key)
    tie_breaker = 0
    pq = [(0, tie_breaker, init_key)]

    state_map = {init_key: init_game}
    min_cost = {init_key: 0}
    trace = {init_key: (None, None)}  # Lưu (state_cha, action_đã_đi) để truy vết

    expanded = 0
    goal_key = None

    while pq:
        cost, _, curr_key = heapq.heappop(pq)

        # Nếu đường đi này đắt hơn đường đã biết tới curr_key thì bỏ qua (lazy deletion)
        if cost > min_cost.get(curr_key, float("inf")):
            continue

        curr_game = state_map[curr_key]

        if curr_game.status == "WON":
            goal_key = curr_key
            break

        if curr_game.status != "PLAYING":
            continue

        expanded += 1

        for move_dir in curr_game.get_possible_actions():
            nxt_game = copy.deepcopy(curr_game)
            nxt_game.move(move_dir)
            nxt_game.history = []  # Xóa lịch sử undo cho nhẹ RAM khi chạy tìm kiếm

            if nxt_game.status == "LOST":
                continue

            nxt_key = encode_state(nxt_game)
            nxt_cost = cost + 1

            if nxt_cost < min_cost.get(nxt_key, float("inf")):
                min_cost[nxt_key] = nxt_cost
                state_map[nxt_key] = nxt_game
                trace[nxt_key] = (curr_key, move_dir)

                tie_breaker += 1
                heapq.heappush(pq, (nxt_cost, tie_breaker, nxt_key))

    elapsed = time.perf_counter() - t0
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Truy vết ngược từ đích về trạng thái đầu
    path = []
    if goal_key is not None:
        curr = goal_key
        while trace[curr][0] is not None:
            prev_key, act = trace[curr]
            path.append(act)
            curr = prev_key
        path.reverse()

    found = goal_key is not None
    return {
        "found": found,
        "path": path,
        "solution_length": len(path) if found else None,
        "total_cost": min_cost[goal_key] if found else None,
        "expanded_nodes": expanded,
        "search_time_seconds": elapsed,
        "peak_memory_mb": peak_mem / (1024 * 1024)
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Chạy thuật toán UCS giải game Bloxorz")
    parser.add_argument("--level", type=int, default=0, help="Màn chơi (bắt đầu từ 0)")
    args = parser.parse_args()

    res = solve_ucs(args.level)

    print(f"\n--- KẾT QUẢ UCS (Level {args.level}) ---")
    if res["found"]:
        print("Đường đi:", " -> ".join(res["path"]))
        print("Số bước:", res["solution_length"])
        print("Tổng chi phí:", res["total_cost"])
    else:
        print("Không tìm thấy lời giải!")

    print(f"Số node đã mở rộng: {res['expanded_nodes']}")
    print(f"Thời gian chạy: {res['search_time_seconds']:.6f} s")
    print(f"Bộ nhớ đỉnh: {res['peak_memory_mb']:.4f} MB")