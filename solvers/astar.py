# solvers/astar.py — Thuật toán tìm kiếm A* (A-Star)
from heapq import heappop, heappush
from itertools import count
from game import BloxorzGame
from .base import (
    extract_state,
    find_goal_pos,
    get_next_state,
    get_valid_actions,
    reconstruct_moves,
)


def _heuristic(state: tuple, goal_pos: tuple[int, int]) -> float:
    """Ước lượng khoảng cách từ trạng thái hiện tại đến ô đích."""
    is_split, pos_data, _, _ = state
    gr, gc = goal_pos

    if not is_split:
        (r1, c1), (r2, c2) = pos_data
        dist = (abs(r1 - gr) + abs(c1 - gc) + abs(r2 - gr) + abs(c2 - gc)) / 2.0
        standing_penalty = 0.0 if (r1 == r2 and c1 == c2) else 0.5
        return (dist / 2.0) + standing_penalty
    else:
        (r1, c1), (r2, c2) = pos_data
        d1 = abs(r1 - gr) + abs(c1 - gc)
        d2 = abs(r2 - gr) + abs(c2 - gc)
        return (d1 + d2) / 3.0


def solve_astar_from_game(game: BloxorzGame) -> dict | None:
    """Chạy thuật toán A* từ trạng thái hiện tại của BloxorzGame."""
    if game.status != "PLAYING":
        return None

    initial_state = extract_state(game)
    goal_pos = find_goal_pos(game.board)

    sequence = count()
    frontier = [
        (
            _heuristic(initial_state, goal_pos),
            0,
            next(sequence),
            initial_state,
        )
    ]
    best_cost = {initial_state: 0}
    parents = {}
    nodes_expanded = 0
    nodes_generated = 1

    while frontier:
        _, cost, _, state = heappop(frontier)

        if cost != best_cost.get(state):
            continue

        nodes_expanded += 1

        for action in get_valid_actions(state):
            next_state, is_won = get_next_state(game, state, action)
            if next_state is None:
                continue

            step_cost = 0.1 if action == "SWITCH" else 1
            next_cost = cost + step_cost

            if next_cost >= best_cost.get(next_state, float("inf")):
                continue

            best_cost[next_state] = next_cost
            parents[next_state] = (state, action)
            nodes_generated += 1

            if is_won:
                moves = reconstruct_moves(parents, next_state)
                return {
                    "algorithm": "A*",
                    "moves": moves,
                    "total_cost": len([m for m in moves if m != "SWITCH"]),
                    "nodes_expanded": nodes_expanded,
                    "nodes_generated": nodes_generated,
                }

            priority = next_cost + _heuristic(next_state, goal_pos)
            heappush(frontier, (priority, next_cost, next(sequence), next_state))

    return None