# solvers/__init__.py — Nơi tập hợp và đăng ký các thuật toán
from .astar import solve_astar_from_game
# Sau này có BFS, DFS thì import thêm ở đây:
# from .bfs import solve_bfs_from_game
# from .dfs import solve_dfs_from_game
from .bfs import solve_bfs
from .dfs import solve_dfs, solve_ids
# Danh bạ các thuật toán (Tên hiển thị và Hàm giải)
AVAILABLE_SOLVERS = {
    "A*": solve_astar_from_game,
    "BFS": solve_bfs,
    "DFS": solve_dfs,
    "IDS": solve_ids,
}
 
 
def solve_game(game, algo_name: str = "A*") -> dict | None:
    """Hàm trung tâm để gọi thuật toán bất kỳ theo tên."""
    solver_fn = AVAILABLE_SOLVERS.get(algo_name)
    if solver_fn is None:
        return None
    return solver_fn(game)