# solvers/dfs.py — Thuật toán tìm kiếm theo chiều sâu: DFS (stack + visited) và IDS
import time
import tracemalloc

from .base import extract_state, get_valid_actions, get_next_state, reconstruct_moves


def _build_result(name, path, start_time, peak_memory, expanded_nodes, generated_nodes):
    """Đóng gói kết quả theo cùng định dạng với bfs.py / astar.py."""
    return {
        "algorithm": name,
        "path": path,
        "moves": path,
        "solution_length": len(path),
        "total_cost": len([m for m in path if m != "SWITCH"]),
        "search_time": time.time() - start_time,
        "memory_usage": peak_memory,
        "expanded_nodes": expanded_nodes,
        "nodes_expanded": expanded_nodes,
        "nodes_generated": generated_nodes,
    }


def solve_dfs(initial_game):
    """
    DFS lặp (dùng stack tường minh, tránh tràn đệ quy) có tập visited để chống chu trình.
    Lưu ý: DFS không đảm bảo lời giải ngắn nhất.
    """
    if initial_game.status != "PLAYING":
        return None

    tracemalloc.start()
    start_time = time.time()

    start_state = extract_state(initial_game)
    # Mỗi phần tử stack: (state, parent_state, action). parent=None cho trạng thái đầu.
    stack = [(start_state, None, None)]
    visited = set()          # các trạng thái đã mở rộng
    parents = {}
    expanded_nodes = 0
    generated_nodes = 1

    while stack:
        state, parent, action = stack.pop()
        if state in visited:
            continue
        visited.add(state)
        if parent is not None:
            parents[state] = (parent, action)
        expanded_nodes += 1

        # Duyệt ngược để hành động đứng đầu danh sách (UP) được thử trước khi pop
        for act in reversed(get_valid_actions(state)):
            next_state, is_won = get_next_state(initial_game, state, act)
            if next_state is None:
                continue

            if is_won:
                parents[next_state] = (state, act)
                path = reconstruct_moves(parents, next_state)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                return _build_result("DFS", path, start_time, peak, expanded_nodes, generated_nodes + 1)

            if next_state not in visited:
                generated_nodes += 1
                stack.append((next_state, state, act))

    tracemalloc.stop()
    return None


def solve_ids(initial_game, max_depth: int = 200):
    """
    Iterative Deepening Search: lặp DFS giới hạn độ sâu 0,1,2,... cho đến khi gặp đích.
    Đầy đủ và tối ưu theo số bước (mọi bước chi phí như nhau).
    Để chống chu trình mà vẫn đúng, dùng best_depth[state]: chỉ mở rộng lại một trạng thái
    nếu tới được nó bằng đường nông hơn lần trước trong cùng vòng lặp.
    """
    if initial_game.status != "PLAYING":
        return None

    tracemalloc.start()
    start_time = time.time()

    start_state = extract_state(initial_game)
    expanded_nodes = 0
    generated_nodes = 1

    for limit in range(max_depth + 1):
        best_depth = {start_state: 0}
        parents = {}
        stack = [(start_state, 0)]
        cutoff = False

        while stack:
            state, depth = stack.pop()
            if best_depth.get(state, float("inf")) < depth:
                continue  # đã có đường nông hơn tới state này
            expanded_nodes += 1

            if depth >= limit:
                cutoff = True
                continue

            for act in reversed(get_valid_actions(state)):
                next_state, is_won = get_next_state(initial_game, state, act)
                if next_state is None:
                    continue

                if is_won:
                    parents[next_state] = (state, act)
                    path = reconstruct_moves(parents, next_state)
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    return _build_result("IDS", path, start_time, peak, expanded_nodes, generated_nodes + 1)

                nd = depth + 1
                if nd < best_depth.get(next_state, float("inf")):
                    best_depth[next_state] = nd
                    parents[next_state] = (state, act)
                    generated_nodes += 1
                    stack.append((next_state, nd))

        if not cutoff:
            break  # đã duyệt hết không gian trạng thái, không có lời giải

    tracemalloc.stop()
    return None
