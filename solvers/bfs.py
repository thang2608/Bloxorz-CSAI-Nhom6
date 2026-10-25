import time
import tracemalloc
from collections import deque
from .base import extract_state, get_valid_actions, get_next_state, reconstruct_moves

def solve_bfs(initial_game):
    tracemalloc.start()
    start_time = time.time()
    
    # 1. Khởi tạo trạng thái ban đầu dưới dạng tuple
    start_state = extract_state(initial_game)
    frontier = deque([start_state])
    explored = {start_state}
    parents = {}  # Lưu vết (state -> (parent_state, action)) để gọi reconstruct_moves
    expanded_nodes = 0
    
    while frontier:
        current_state = frontier.popleft()
        expanded_nodes += 1
        
        # Lấy danh sách hành động hợp lệ từ trạng thái hiện tại
        for action in get_valid_actions(current_state):
            # Mô phỏng bước đi nhanh trên tuple, trả về trạng thái mới và cờ chiến thắng
            next_state, is_won = get_next_state(initial_game, current_state, action)
            
            # Bỏ qua nếu bước đi không hợp lệ (rớt vực, vỡ ô cam)
            if next_state is None:
                continue
                
            if next_state not in explored:
                explored.add(next_state)
                parents[next_state] = (current_state, action)
                
                if is_won:
                    search_time = time.time() - start_time
                    _, peak_memory = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    
                    # Truy vết lại danh sách đường đi từ đích ngược về điểm xuất phát
                    path = reconstruct_moves(parents, next_state)
                    
                    return {
                        "path": path,
                        "solution_length": len(path),
                        "search_time": search_time,
                        "memory_usage": peak_memory,
                        "expanded_nodes": expanded_nodes
                    }
                
                frontier.append(next_state)
                
    tracemalloc.stop()
    return None