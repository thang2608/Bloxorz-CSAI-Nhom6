# solvers/base.py — Nền tảng mô phỏng trạng thái dùng chung cho mọi thuật toán AI
from game import BloxorzGame


def extract_state(game: BloxorzGame) -> tuple:
    """
    Chuyển trạng thái hiện tại của BloxorzGame thành tuple bất biến (hashable).
    Cấu trúc: (is_split, block_or_minis, active_block, bridges_open_tuple)
    """
    bridges_state = tuple(
        (bid, binfo["is_open"]) for bid, binfo in sorted(game.bridges.items())
    )
    if not game.is_split:
        return (False, game.block.state, 0, bridges_state)
    else:
        m0 = tuple(game.mini_blocks[0])
        m1 = tuple(game.mini_blocks[1])
        return (True, (m0, m1), game.active_block, bridges_state)


def find_goal_pos(board: list[list[int]]) -> tuple[int, int]:
    """Tìm tọa độ ô đích (giá trị 2) trên bàn cờ."""
    for r, row in enumerate(board):
        for c, val in enumerate(row):
            if val == 2:
                return (r, c)
    return (0, 0)


def get_valid_actions(state: tuple) -> list[str]:
    """Trả về danh sách các hành động có thể thử từ trạng thái hiện tại."""
    is_split = state[0]
    actions = ["UP", "DOWN", "LEFT", "RIGHT"]
    if is_split:
        actions.append("SWITCH")
    return actions


def reconstruct_moves(parents: dict[tuple, tuple[tuple, str]], target_state: tuple) -> list[str]:
    """Truy vết lại danh sách các bước di chuyển từ trạng thái đích."""
    moves = []
    cur = target_state
    while cur in parents:
        cur, act = parents[cur]
        moves.append(act)
    moves.reverse()
    return moves


def _is_walkable(game: BloxorzGame, r: int, c: int, bridges_dict: dict[int, bool]) -> bool:
    if not (0 <= r < game.rows and 0 <= c < game.cols):
        return False
    for bid, binfo in game.bridges.items():
        if [r, c] in binfo["tiles"]:
            return bridges_dict[bid]
    return game.board[r][c] != 0


def _apply_switch_effects(switch: dict, bridges_dict: dict[int, bool]):
    for effect in switch.get("effects", []):
        action = effect.get("action")
        bid = int(effect.get("bridge_id"))
        if bid in bridges_dict:
            if action == "toggle":
                bridges_dict[bid] = not bridges_dict[bid]
            elif action == "open":
                bridges_dict[bid] = True
            elif action == "close":
                bridges_dict[bid] = False


def get_next_state(game: BloxorzGame, state: tuple, action: str) -> tuple[tuple | None, bool]:
    """
    Mô phỏng bước đi trên state tuple mà không làm thay đổi game gốc.
    Trả về: (next_state_hoặc_None_nếu_thua, is_won)
    """
    is_split, pos_data, active_block, bridges_tuple = state
    bridges_dict = dict(bridges_tuple)

    # 1. Đổi khối điều khiển khi đang phân thân
    if action == "SWITCH":
        if not is_split:
            return None, False
        return (True, pos_data, 1 - active_block, bridges_tuple), False

    # 2. Di chuyển khi đang là khối liền 1x1x2
    if not is_split:
        (r1, c1), (r2, c2) = pos_data
        standing = (r1 == r2 and c1 == c2)
        horizontal = (r1 == r2 and c1 != c2)

        if action == "LEFT":
            if standing: nr1, nc1, nr2, nc2 = r1, c1 - 2, r1, c1 - 1
            elif horizontal: nr1, nc1, nr2, nc2 = r1, c1 - 1, r1, c1 - 1
            else: nr1, nc1, nr2, nc2 = r1, c1 - 1, r2, c2 - 1
        elif action == "RIGHT":
            if standing: nr1, nc1, nr2, nc2 = r1, c1 + 1, r1, c1 + 2
            elif horizontal: nr1, nc1, nr2, nc2 = r1, c2 + 1, r1, c2 + 1
            else: nr1, nc1, nr2, nc2 = r1, c1 + 1, r2, c2 + 1
        elif action == "UP":
            if standing: nr1, nc1, nr2, nc2 = r1 - 2, c1, r1 - 1, c1
            elif horizontal: nr1, nc1, nr2, nc2 = r1 - 1, c1, r2 - 1, c2
            else: nr1, nc1, nr2, nc2 = r1 - 1, c1, r1 - 1, c1
        elif action == "DOWN":
            if standing: nr1, nc1, nr2, nc2 = r1 + 1, c1, r1 + 2, c1
            elif horizontal: nr1, nc1, nr2, nc2 = r1 + 1, c1, r2 + 1, c2
            else: nr1, nc1, nr2, nc2 = r2 + 1, c1, r2 + 1, c1
        else:
            return None, False

        if (nr1, nc1) > (nr2, nc2):
            nr1, nc1, nr2, nc2 = nr2, nc2, nr1, nc1

        if not (_is_walkable(game, nr1, nc1, bridges_dict) and _is_walkable(game, nr2, nc2, bridges_dict)):
            return None, False

        next_standing = (nr1 == nr2 and nc1 == nc2)

        if next_standing and game.board[nr1][nc1] == 3:
            return None, False

        if next_standing and game.board[nr1][nc1] == 2:
            new_bridges = tuple(sorted(bridges_dict.items()))
            return (False, ((nr1, nc1), (nr2, nc2)), 0, new_bridges), True

        tiles = [[nr1, nc1], [nr2, nc2]]
        now_split = False
        mini_pos = None

        for sw in game.switches:
            sr, sc = sw["pos"]
            stype = sw["type"]
            if stype == "soft" and [sr, sc] in tiles:
                _apply_switch_effects(sw, bridges_dict)
            elif stype == "heavy" and next_standing and [nr1, nc1] == [sr, sc]:
                _apply_switch_effects(sw, bridges_dict)
            elif stype == "split" and next_standing and [nr1, nc1] == [sr, sc]:
                split_to = sw.get("split_to")
                if split_to and len(split_to) == 2:
                    now_split = True
                    mini_pos = (tuple(split_to[0]), tuple(split_to[1]))
                    break

        new_bridges = tuple(sorted(bridges_dict.items()))
        if now_split:
            return (True, mini_pos, 0, new_bridges), False

        if not (_is_walkable(game, nr1, nc1, bridges_dict) and _is_walkable(game, nr2, nc2, bridges_dict)):
            return None, False

        return (False, ((nr1, nc1), (nr2, nc2)), 0, new_bridges), False

    # 3. Di chuyển khi đang ở chế độ tách 2 khối nhỏ 1x1x1
    else:
        m0, m1 = list(pos_data[0]), list(pos_data[1])
        cur = m0 if active_block == 0 else m1
        other = m1 if active_block == 0 else m0

        dr, dc = 0, 0
        if action == "UP": dr = -1
        elif action == "DOWN": dr = 1
        elif action == "LEFT": dc = -1
        elif action == "RIGHT": dc = 1
        else: return None, False

        nr, nc = cur[0] + dr, cur[1] + dc
        if not _is_walkable(game, nr, nc, bridges_dict):
            return None, False

        or_, oc = other[0], other[1]
        if abs(nr - or_) + abs(nc - oc) == 1:
            p1, p2 = (nr, nc), (or_, oc)
            if p1 > p2:
                p1, p2 = p2, p1

            if not (_is_walkable(game, p1[0], p1[1], bridges_dict) and _is_walkable(game, p2[0], p2[1], bridges_dict)):
                return None, False

            tiles = [[p1[0], p1[1]], [p2[0], p2[1]]]
            for sw in game.switches:
                if sw["type"] == "soft" and sw["pos"] in tiles:
                    _apply_switch_effects(sw, bridges_dict)

            if not (_is_walkable(game, p1[0], p1[1], bridges_dict) and _is_walkable(game, p2[0], p2[1], bridges_dict)):
                return None, False

            new_bridges = tuple(sorted(bridges_dict.items()))
            return (False, (p1, p2), 0, new_bridges), False

        for sw in game.switches:
            if sw["type"] == "soft" and sw["pos"] == [nr, nc]:
                _apply_switch_effects(sw, bridges_dict)

        if not (_is_walkable(game, nr, nc, bridges_dict) and _is_walkable(game, or_, oc, bridges_dict)):
            return None, False

        new_bridges = tuple(sorted(bridges_dict.items()))
        new_minis = ((nr, nc), (or_, oc)) if active_block == 0 else ((or_, oc), (nr, nc))
        return (True, new_minis, active_block, new_bridges), False