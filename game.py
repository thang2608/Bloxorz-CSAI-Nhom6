# game.py — Logic cốt lõi của game Bloxorz
import copy
from levels import LEVELS

class Block:
    def __init__(self, r1, c1, r2=None, c2=None):
        if r2 is None or c2 is None:
            r2, c2 = r1, c1
        if (r1, c1) <= (r2, c2):
            self.state = ((r1, c1), (r2, c2))
        else:
            self.state = ((r2, c2), (r1, c1))

    # --- 1. Nhận diện tư thế khối ---
    def is_standing(self):
        (r1, c1), (r2, c2) = self.state
        return r1 == r2 and c1 == c2

    def is_horizontal(self):
        (r1, c1), (r2, c2) = self.state
        return r1 == r2 and c1 != c2

    def is_vertical(self):
        (r1, c1), (r2, c2) = self.state
        return r1 != r2 and c1 == c2

    # --- 2. Lăn theo 4 hướng ---
    def left(self):
        (r1, c1), (r2, c2) = self.state
        if self.is_standing():
            return Block(r1, c1 - 2, r1, c1 - 1)
        elif self.is_horizontal():
            return Block(r1, c1 - 1)
        else:
            return Block(r1, c1 - 1, r2, c2 - 1)

    def right(self):
        (r1, c1), (r2, c2) = self.state
        if self.is_standing():
            return Block(r1, c1 + 1, r1, c1 + 2)
        elif self.is_horizontal():
            return Block(r1, c2 + 1)
        else:
            return Block(r1, c1 + 1, r2, c2 + 1)

    def up(self):
        (r1, c1), (r2, c2) = self.state
        if self.is_standing():
            return Block(r1 - 2, c1, r1 - 1, c1)
        elif self.is_horizontal():
            return Block(r1 - 1, c1, r2 - 1, c2)
        else:
            return Block(r1 - 1, c1)

    def down(self):
        (r1, c1), (r2, c2) = self.state
        if self.is_standing():
            return Block(r1 + 1, c1, r1 + 2, c1)
        elif self.is_horizontal():
            return Block(r1 + 1, c1, r2 + 1, c2)
        else:
            return Block(r2 + 1, c1)

    def __eq__(self, other):
        return isinstance(other, Block) and self.state == other.state

    def __hash__(self):
        return hash(self.state)


class BloxorzGame:
    def __init__(self, level_index=0):
        self.load_level(level_index)

    def load_level(self, level_input):
        if isinstance(level_input, dict):
            level_data = level_input
            self.level_index = level_data.get("id", 1) - 1
        else:
            if not (0 <= level_input < len(LEVELS)):
                level_input = 0
            self.level_index = level_input
            level_data = LEVELS[self.level_index]

        self.current_level_data = level_data
        self.level_id = level_data.get("id", self.level_index + 1)
        self.level_name = level_data.get("name", f"Màn {self.level_index + 1}")
        self.level_description = level_data.get("description", "")
        self.board = [row[:] for row in level_data["board"]]
        self.rows = len(self.board)
        self.cols = len(self.board[0])
        self.start_pos = level_data["start"]

        # Bridges: id -> {"tiles": [[r, c], ...], "is_open": bool, "initially_open": bool}
        self.bridges = {}
        for bid, binfo in level_data.get("bridges", {}).items():
            self.bridges[int(bid)] = {
                "tiles": [list(t) for t in binfo["tiles"]],
                "initially_open": binfo.get("initially_open", False),
                "is_open": binfo.get("initially_open", False),
            }

        self.switches = copy.deepcopy(level_data.get("switches", []))

        # Block & Split mode
        start_split = level_data.get("start_split")
        if start_split and len(start_split) == 2:
            # Bài thực hành Hợp nhất: bắt đầu sẵn 2 khối nhỏ 1×1×1 tách rời
            self.block = Block(start_split[0][0], start_split[0][1])
            self.is_split = True
            self.mini_blocks = [list(start_split[0]), list(start_split[1])]
            self.active_block = 0
        else:
            self.block = Block(self.start_pos[0], self.start_pos[1])
            self.is_split = False
            self.mini_blocks = []      # [[r0, c0], [r1, c1]] khi split
            self.active_block = 0      # 0 hoặc 1

        self.moves = 0
        self.status = "PLAYING"    # "PLAYING", "WON", "LOST"
        self.lost_reason = None    # "FALL", "FRAGILE_BREAK", "BRIDGE_CLOSED"
        self.broken_tile = None    # [r, c] khi ô cam bị vỡ
        self.last_event = None     # "SPLIT", "MERGE", "SWITCH_TRIGGER", "UNDO", None
        self.history = []          # Stack lưu lịch sử để hỗ trợ Undo (Hoàn tác)

    def _save_snapshot(self):
        """Lưu lại bản sao trạng thái trước khi di chuyển để hỗ trợ Undo"""
        snapshot = {
            "block": copy.deepcopy(self.block),
            "is_split": self.is_split,
            "mini_blocks": copy.deepcopy(self.mini_blocks),
            "active_block": self.active_block,
            "bridges": copy.deepcopy(self.bridges),
            "moves": self.moves,
            "status": self.status,
            "lost_reason": self.lost_reason,
            "broken_tile": copy.deepcopy(self.broken_tile),
            "last_event": self.last_event,
        }
        self.history.append(snapshot)

    def can_undo(self):
        """Kiểm tra có thể hoàn tác bước đi trước đó không"""
        return len(self.history) > 0

    def undo(self):
        """Hoàn tác bước đi trước đó"""
        if not self.history:
            return False
        snapshot = self.history.pop()
        self.block = snapshot["block"]
        self.is_split = snapshot["is_split"]
        self.mini_blocks = snapshot["mini_blocks"]
        self.active_block = snapshot["active_block"]
        self.bridges = snapshot["bridges"]
        self.moves = snapshot["moves"]
        self.status = snapshot["status"]
        self.lost_reason = snapshot["lost_reason"]
        self.broken_tile = snapshot["broken_tile"]
        self.last_event = "UNDO"
        return True

    def get_bridge_at(self, r, c):
        for bid, binfo in self.bridges.items():
            if [r, c] in binfo["tiles"]:
                return bid, binfo
        return None, None

    def is_walkable(self, r, c):
        """Kiểm tra ô (r, c) có thể đứng lên được không"""
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return False
        # Nếu ô thuộc về cầu, phụ thuộc vào trạng thái mở của cầu đó
        bid, binfo = self.get_bridge_at(r, c)
        if binfo is not None:
            return binfo["is_open"]
        # Ngược lại, kiểm tra không phải vực thẳm (0)
        return self.board[r][c] != 0

    def is_fragile(self, r, c):
        """Kiểm tra ô có phải là ô sàn dễ vỡ màu cam (3) hay không"""
        return 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == 3

    def is_legal(self, block):
        """Kiểm tra khối 1x1x2 có nằm hoàn toàn trên sàn đi được không"""
        (r1, c1), (r2, c2) = block.state
        return self.is_walkable(r1, c1) and self.is_walkable(r2, c2)

    def is_goal(self, block):
        """Kiểm tra khối đã đứng thẳng vào ô đích màu xanh neon (2) chưa"""
        (r1, c1), _ = block.state
        return block.is_standing() and self.board[r1][c1] == 2

    def apply_switch(self, switch):
        """Thực hiện hiệu ứng mở/đóng/toggle cầu từ công tắc"""
        for effect in switch.get("effects", []):
            action = effect.get("action")
            bid = int(effect.get("bridge_id"))
            if bid in self.bridges:
                if action == "toggle":
                    self.bridges[bid]["is_open"] = not self.bridges[bid]["is_open"]
                elif action == "open":
                    self.bridges[bid]["is_open"] = True
                elif action == "close":
                    self.bridges[bid]["is_open"] = False
        self.last_event = "SWITCH_TRIGGER"

    def check_switches_for_block(self, block):
        """Kiểm tra va chạm công tắc khi đang là khối 1x1x2 nguyên bản"""
        (r1, c1), (r2, c2) = block.state
        tiles = [[r1, c1], [r2, c2]]
        standing = block.is_standing()

        for switch in self.switches:
            sr, sc = switch["pos"]
            stype = switch["type"]

            # 1. Công tắc mềm: kích hoạt khi bất kỳ phần nào của khối đè lên
            if stype == "soft":
                if [sr, sc] in tiles:
                    self.apply_switch(switch)

            # 2. Công tắc nặng (X): CHỈ kích hoạt khi khối đứng thẳng
            elif stype == "heavy":
                if standing and [r1, c1] == [sr, sc]:
                    self.apply_switch(switch)

            # 3. Công tắc tách khối (): CHỈ kích hoạt khi khối đứng thẳng
            elif stype == "split":
                if standing and [r1, c1] == [sr, sc]:
                    split_to = switch.get("split_to")
                    if split_to and len(split_to) == 2:
                        self.is_split = True
                        self.mini_blocks = [list(split_to[0]), list(split_to[1])]
                        self.active_block = 0
                        self.last_event = "SPLIT"
                        return "SPLIT"
        return None

    def check_switches_for_mini(self, r, c):
        """Khối nhỏ 1x1x1 chỉ có thể kích hoạt công tắc mềm"""
        for switch in self.switches:
            sr, sc = switch["pos"]
            stype = switch["type"]
            if stype == "soft":
                if [sr, sc] == [r, c]:
                    self.apply_switch(switch)

    def move(self, direction):
        if self.status != "PLAYING":
            return self.status

        dir_upper = direction.upper()
        self.last_event = None

        # Chuyển đổi khối đang điều khiển (khi đang ở chế độ tách khối)
        if dir_upper == "SWITCH":
            if self.is_split:
                self._save_snapshot()
                self.active_block = 1 - self.active_block
            return self.status

        # ── TRƯỜNG HỢP 1: KHỐI LIỀN 1x1x2 ───────────────────
        if not self.is_split:
            actions = {
                "LEFT": self.block.left,
                "RIGHT": self.block.right,
                "UP": self.block.up,
                "DOWN": self.block.down
            }
            action_fn = actions.get(dir_upper)
            if not action_fn:
                return self.status

            self._save_snapshot()
            next_block = action_fn()
            self.moves += 1

            # 1. Kiểm tra lọt ra ngoài vực / cầu đóng
            if not self.is_legal(next_block):
                self.block = next_block
                self.status = "LOST"
                self.lost_reason = "FALL"
                return self.status

            # 2. Kiểm tra ô sàn cam dễ vỡ (Fragile)
            # Nếu đứng thẳng lên ô cam -> ô sẽ vỡ và rơi!
            # Nếu nằm ngang / dọc -> trọng lượng trải đều, an toàn!
            if next_block.is_standing():
                (r1, c1), _ = next_block.state
                if self.is_fragile(r1, c1):
                    self.block = next_block
                    self.status = "LOST"
                    self.lost_reason = "FRAGILE_BREAK"
                    self.broken_tile = [r1, c1]
                    return self.status

            # 3. Kiểm tra rơi vào lỗ đích (Thắng)
            self.block = next_block
            if self.is_goal(self.block):
                self.status = "WON"
                return self.status

            # 4. Kiểm tra kích hoạt công tắc
            self.check_switches_for_block(self.block)

            # 5. Kiểm tra nếu công tắc vừa bật làm sập cầu ngay dưới chân khối -> rơi!
            if not self.is_legal(self.block):
                self.status = "LOST"
                self.lost_reason = "BRIDGE_CLOSED"
                return self.status

            return self.status

        # ── TRƯỜNG HỢP 2: ĐANG TÁCH THÀNH 2 KHỐI 1x1x1 ────────
        else:
            cur_r, cur_c = self.mini_blocks[self.active_block]
            dr, dc = 0, 0
            if dir_upper == "UP": dr = -1
            elif dir_upper == "DOWN": dr = 1
            elif dir_upper == "LEFT": dc = -1
            elif dir_upper == "RIGHT": dc = 1
            else:
                return self.status

            self._save_snapshot()
            nr, nc = cur_r + dr, cur_c + dc
            self.mini_blocks[self.active_block] = [nr, nc]
            self.moves += 1

            # 1. Khối nhỏ rơi ra vực / cầu đóng (lưu ý: ô đích 2 vẫn là sàn đi được với khối nhỏ, không bị rớt)
            if not self.is_walkable(nr, nc):
                self.status = "LOST"
                self.lost_reason = "FALL"
                return self.status

            # 3. Kiểm tra GỘP KHỐI (khi 2 khối nhỏ nằm cạnh nhau theo hàng hoặc cột)
            other_idx = 1 - self.active_block
            or_, oc = self.mini_blocks[other_idx]
            if abs(nr - or_) + abs(nc - oc) == 1:
                # Gộp lại thành khối 1x1x2 ban đầu!
                self.is_split = False
                self.block = Block(nr, nc, or_, oc)
                self.mini_blocks = []
                self.last_event = "MERGE"

                # Khối sau khi gộp luôn ở tư thế nằm (ngang hoặc dọc), kiểm tra hợp lệ
                if not self.is_legal(self.block):
                    self.status = "LOST"
                    self.lost_reason = "FALL"
                    return self.status

                # Kích hoạt công tắc cho khối vừa gộp
                self.check_switches_for_block(self.block)
                if not self.is_legal(self.block):
                    self.status = "LOST"
                    self.lost_reason = "BRIDGE_CLOSED"
                    return self.status

                return self.status

            # 4. Kích hoạt công tắc mềm cho khối nhỏ
            self.check_switches_for_mini(nr, nc)

            # 5. Nếu công tắc vừa bật làm sập cầu dưới chân khối nhỏ này HOẶC khối còn lại -> thua
            if not self.is_walkable(nr, nc) or not self.is_walkable(or_, oc):
                self.status = "LOST"
                self.lost_reason = "BRIDGE_CLOSED"
                return self.status

            return self.status

    def reset(self):
        self.load_level(self.current_level_data)

    def next_level(self):
        next_idx = (self.level_index + 1) % len(LEVELS)
        self.load_level(next_idx)

    def get_possible_actions(self):
        """Trả về danh sách các action hợp lệ có thể bấm ở trạng thái hiện tại"""
        if self.status != "PLAYING":
            return []
        actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        if self.is_split:
            actions.append("SWITCH")
        return actions

    def to_dict(self):
        """Đóng gói toàn bộ thông tin bàn cờ, khối, cầu, công tắc sang JSON cho Frontend / UI"""
        block_info = None
        if not self.is_split:
            (r1, c1), (r2, c2) = self.block.state
            block_info = {
                "tiles": [[r1, c1], [r2, c2]],
                "is_standing": self.block.is_standing(),
                "is_horizontal": self.block.is_horizontal(),
                "is_vertical": self.block.is_vertical(),
            }

        # Bridges formatting
        bridges_dict = {}
        for bid, binfo in self.bridges.items():
            bridges_dict[bid] = {
                "tiles": binfo["tiles"],
                "is_open": binfo["is_open"],
                "initially_open": binfo["initially_open"]
            }

        return {
            "level_index": self.level_index,
            "level_id": self.level_id,
            "level_name": self.level_name,
            "level_description": self.level_description,
            "total_levels": len(LEVELS),
            "board": self.board,
            "rows": self.rows,
            "cols": self.cols,
            "bridges": bridges_dict,
            "switches": self.switches,
            "is_split": self.is_split,
            "active_block": self.active_block,
            "mini_blocks": self.mini_blocks,
            "block": block_info,
            "status": self.status,
            "lost_reason": self.lost_reason,
            "broken_tile": self.broken_tile,
            "last_event": self.last_event,
            "moves": self.moves,
            "can_undo": self.can_undo(),
            "history_length": len(self.history),
        }
