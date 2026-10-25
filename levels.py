# levels.py — Định nghĩa các màn chơi Bloxorz
#
# Tile types:
#   0 = VOID    (vực thẳm)
#   1 = NORMAL  (sàn thường)
#   2 = GOAL    (lỗ đích — màu xanh neon)
#   3 = FRAGILE (sàn dễ vỡ — màu cam; vỡ khi khối đứng thẳng lên)
#
# Switches:
#   "soft"  — kích hoạt khi bất kỳ phần nào của khối chạm vào
#   "heavy" — kích hoạt CHỈ khi khối đứng thẳng lên
#   "split" — kích hoạt CHỈ khi khối đứng thẳng → tách thành 2 mini block (1x1x1)
#
# Bridges:
#   Được định nghĩa qua danh sách tọa độ tiles, có trạng thái đóng (vực thẳm) hoặc mở (sàn đi được)

LEVELS = [
    # ─────────────────────────────────────────────
    # MÀN 1: Khởi đầu — Bản đồ kinh điển Bloxorz
    # ─────────────────────────────────────────────
    {
        "id": 1,
        "name": "Màn 1: Khởi đầu kinh điển",
        "description": "Lăn khối về lỗ đích màu xanh neon. Dùng W/A/S/D hoặc phím mũi tên.",
        "board": [
            [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 1, 1, 2, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
        ],
        "start": (1, 1),
        "switches": [],
        "bridges": {},
    },

    # ─────────────────────────────────────────────
    # MÀN 2: Lối đi chữ S hiểm trở (Narrow S-Corridor)
    # ─────────────────────────────────────────────
    {
        "id": 2,
        "name": "Màn 2: Hành Lang Hiểm Trở",
        "description": "Lối đi hẹp 1-2 ô uốn lượn quanh vực thẳm. Phải căn chỉnh hướng lăn chính xác từng bước một!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # 0: start (0, 1)
            [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1],  # 1
            [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1],  # 2: cầu hẹp ngang
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1],  # 3: eo hẹp (3, 5..6)
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0],  # 4
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 0],  # 5: Đích ở (5, 9)
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],  # 6
        ],
        "start": (0, 1),
        "switches": [],
        "bridges": {},
    },

    # ─────────────────────────────────────────────
    # MÀN 3: Bẫy Sàn Cam Dễ Vỡ (Fragile Crossroad)
    # ─────────────────────────────────────────────
    {
        "id": 3,
        "name": "Màn 3: Bẫy Sàn Cam Chẵn Lẻ",
        "description": "Sàn cam dài ngăn cách 2 bờ vực. Tuyệt đối không được đứng thẳng trên ô cam!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10
            [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # 0: start (0, 1)
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],  # 1: đảo xoay phụ
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],  # 2
            [0, 0, 1, 1, 3, 3, 3, 3, 1, 1, 0],  # 3: dải sàn cam 4 ô (3, 4..7)
            [0, 0, 0, 0, 3, 3, 3, 3, 1, 1, 1],  # 4: dải sàn cam 4 ô (4, 4..7)
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1],  # 5: Đích (5, 9)
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],  # 6
        ],
        "start": (0, 1),
        "switches": [],
        "bridges": {},
    },

    # ─────────────────────────────────────────────
    # MÀN 4: Cầu Hẹp & Công Tắc Tròn (Tight Switch & Turnaround)
    # ─────────────────────────────────────────────
    {
        "id": 4,
        "name": "Màn 4: Cầu Hẹp Vực Thẳm",
        "description": "Bật công tắc tròn ở góc khuất mở cầu, sau đó xoay sở trên đảo hẹp để thẳng hàng bước qua cầu.",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1],  # 0: switch ở (0, 0)
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1],  # 1
            [0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 2, 1],  # 2: Cầu nối (2, 5..8), Đích (2, 10)
            [0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1],  # 3: start ở (3, 2)
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0],  # 4
        ],
        "start": (3, 2),
        "switches": [
            {
                "id": "sw_soft_4",
                "type": "soft",
                "pos": [0, 0],
                "effects": [{"action": "toggle", "bridge_id": 0}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[2, 5], [2, 6], [2, 7], [2, 8]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 5: Khóa Chữ X Nặng & Vòng Xoay Đổi Thế
    # ─────────────────────────────────────────────
    {
        "id": 5,
        "name": "Màn 5: Khóa Chữ X Nặng",
        "description": "Công tắc X chỉ nhận khi ĐỨNG THẲNG. Phải tìm vòng xoay quanh hố sâu để đổi đúng thế đứng!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1],  # 0: start (0, 0), X ở (0, 4)
            [1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1],  # 1: lỗ rỗng (1, 2..3) tạo vòng xoay
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 2, 1],  # 2: Cầu nối (2, 5..8), Đích (2, 10)
            [0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1],  # 3
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],  # 4
        ],
        "start": (0, 0),
        "switches": [
            {
                "id": "sw_heavy_5",
                "type": "heavy",
                "pos": [0, 4],
                "effects": [{"action": "toggle", "bridge_id": 0}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[2, 5], [2, 6], [2, 7], [2, 8]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 6: Phân Thân () & Cầu Kép Viễn Xứ
    # ─────────────────────────────────────────────
    {
        "id": 6,
        "name": "Màn 6: Phân Thân & Cầu Kép",
        "description": "Đứng lên () tách thành 2 khối nhỏ. Phối hợp bật cả 2 nhịp cầu rồi hội ngộ hợp nhất!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],  # 0: switch L ở (0, 8), switch R ở (0, 12)
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],  # 1: Cầu 0 (1, 4..5), Cầu 1 (1, 6..7)
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],  # 2: split ở (2, 1)
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1],  # 3: Đích ở (3, 11)
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],  # 4
        ],
        "start": (0, 1),
        "switches": [
            {
                "id": "sw_split_6",
                "type": "split",
                "pos": [2, 1],
                "split_to": [[0, 2], [4, 11]],
                "effects": [],
            },
            {
                "id": "sw_soft_6_left",
                "type": "soft",
                "pos": [0, 8],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
            {
                "id": "sw_soft_6_right",
                "type": "soft",
                "pos": [0, 12],
                "effects": [{"action": "open", "bridge_id": 1}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[1, 4], [1, 5]],
                "initially_open": False,
            },
            1: {
                "tiles": [[1, 6], [1, 7]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 7: Cầu Kép Đảo Chiều (Dual Alternating Bridges)
    # ─────────────────────────────────────────────
    {
        "id": 7,
        "name": "Màn 7: Cầu Kép Đảo Chiều",
        "description": "Hai nhịp cầu nghịch đảo nhau: Mở cầu này sẽ đóng cầu kia! Phải tính toán kỹ đường đi và về.",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1],  # 0: switch A ở (0, 3), heavy B ở (0, 8)
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1],  # 1: Cầu 0 (1, 4..5), Cầu 1 (1, 10..12)
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 2, 1],  # 2: Đích ở (2, 14)
            [0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1],  # 3
        ],
        "start": (0, 0),
        "switches": [
            {
                "id": "sw_soft_7_A",
                "type": "soft",
                "pos": [0, 3],
                "effects": [
                    {"action": "open", "bridge_id": 0},
                    {"action": "close", "bridge_id": 1},
                ],
            },
            {
                "id": "sw_heavy_7_B",
                "type": "heavy",
                "pos": [0, 8],
                "effects": [
                    {"action": "close", "bridge_id": 0},
                    {"action": "open", "bridge_id": 1},
                ],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[1, 4], [1, 5]],
                "initially_open": False,
            },
            1: {
                "tiles": [[1, 10], [1, 11], [1, 12]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 8: Mê Cung Sàn Cam & Khóa Chữ X Liên Hoàn
    # ─────────────────────────────────────────────
    {
        "id": 8,
        "name": "Màn 8: Mê Cung Sàn Cam & Khóa X",
        "description": "Sàn cam dễ vỡ giăng đầy quanh công tắc X nặng. Phải tính toán từng bước lăn để đứng lên X an toàn!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10
            [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1],  # 0: X ở (0, 9)
            [1, 1, 1, 3, 3, 1, 3, 3, 1, 1, 1],  # 1: ô đệm (1, 5)
            [1, 1, 1, 3, 3, 1, 3, 3, 1, 1, 1],  # 2: ô đệm (2, 5)
            [0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0],  # 3
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4: Cầu ở (4, 1..2)
            [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],  # 5
            [0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0],  # 6: Đích ở (6, 2)
            [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],  # 7
        ],
        "start": (0, 1),
        "switches": [
            {
                "id": "sw_8_heavy",
                "type": "heavy",
                "pos": [0, 9],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[4, 1], [4, 2]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 9: Quần Đảo Nổi & Ba Nhịp Cầu
    # ─────────────────────────────────────────────
    {
        "id": 9,
        "name": "Màn 9: Quần Đảo Nổi & Ba Nhịp Cầu",
        "description": "Các hòn đảo nhỏ tí hon giữa đại dương hư vô. Chỉ một sơ suất nhỏ là rơi xuống đáy vực!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14
            [1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1],  # 0: switch 1 ở (0, 1), heavy 2 ở (3, 7)
            [1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 2, 1],  # 1: Cầu 0 (1, 3..5), Cầu 1 (1, 9..11), Đích (1, 13)
            [1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1],  # 2
            [0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1],  # 3
        ],
        "start": (0, 0),
        "switches": [
            {
                "id": "sw_9_1",
                "type": "soft",
                "pos": [0, 1],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
            {
                "id": "sw_9_2",
                "type": "heavy",
                "pos": [3, 7],
                "effects": [{"action": "open", "bridge_id": 1}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[1, 3], [1, 4], [1, 5]],
                "initially_open": False,
            },
            1: {
                "tiles": [[1, 9], [1, 10], [1, 11]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 10: Phân Thân Băng Qua Sàn Cam (Mini Block Fragile Run)
    # ─────────────────────────────────────────────
    {
        "id": 10,
        "name": "Màn 10: Phân Thân & Đầm Lầy Cam",
        "description": "Khối nhỏ 1x1x1 có thể đi an toàn trên sàn cam! Hãy tận dụng để vượt bẫy mở cầu hội ngộ.",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],  # 0
            [1, 1, 1, 1, 0, 0, 0, 0, 3, 3, 3, 1, 1],  # 1: Cầu 0 (1, 4..5), Cầu 1 (1, 6..7), sàn cam (1, 8..10)
            [1, 1, 1, 1, 0, 0, 0, 0, 3, 3, 3, 1, 1],  # 2: split ở (2, 1), sàn cam (2, 8..10)
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],  # 3
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2],  # 4: Đích ở (4, 12)
        ],
        "start": (0, 1),
        "switches": [
            {
                "id": "sw_10_split",
                "type": "split",
                "pos": [2, 1],
                "split_to": [[0, 3], [0, 8]],
                "effects": [],
            },
            {
                "id": "sw_10_soft_left",
                "type": "soft",
                "pos": [2, 3],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
            {
                "id": "sw_10_soft_right",
                "type": "soft",
                "pos": [3, 11],
                "effects": [{"action": "open", "bridge_id": 1}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[1, 4], [1, 5]],
                "initially_open": False,
            },
            1: {
                "tiles": [[1, 6], [1, 7]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 11: Ba Cầu Liên Hoàn Đảo Chiều (Triple Interlocking Bridges)
    # ─────────────────────────────────────────────
    {
        "id": 11,
        "name": "Màn 11: Ba Cầu Liên Hoàn",
        "description": "Ba nhịp cầu phụ thuộc lẫn nhau bắc qua vực sâu vô tận. Thử thách giải đố logic đỉnh cao!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
            [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1],  # 0
            [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1],  # 1: Cầu 0 (1, 3-4), Cầu 1 (1, 8-9), Cầu 2 (1, 13-14)
            [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 2, 1],  # 2: Đích ở (2, 16)
            [0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1],  # 3
        ],
        "start": (0, 0),
        "switches": [
            {
                "id": "sw_11_1",
                "type": "soft",
                "pos": [0, 2],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
            {
                "id": "sw_11_2",
                "type": "heavy",
                "pos": [3, 6],
                "effects": [{"action": "open", "bridge_id": 1}],
            },
            {
                "id": "sw_11_3",
                "type": "heavy",
                "pos": [3, 11],
                "effects": [{"action": "open", "bridge_id": 2}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[1, 3], [1, 4]],
                "initially_open": False,
            },
            1: {
                "tiles": [[1, 8], [1, 9]],
                "initially_open": False,
            },
            2: {
                "tiles": [[1, 13], [1, 14]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 12: Đỉnh Cao Đại Bậc Thầy (The Grandmaster Climax)
    # ─────────────────────────────────────────────
    {
        "id": 12,
        "name": "Màn 12: Đỉnh Cao Đại Bậc Thầy",
        "description": "Thử thách tối thượng kết hợp mọi cơ chế: Phân thân, Sàn cam dễ vỡ, Công tắc X và Cầu bí mật!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12 13
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0],  # 0
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0],  # 1: Cầu 0 (1, 4-5), Cầu 1 (1, 6-7)
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 3, 3, 1, 0, 0],  # 2: Ô cam ở (2, 9), (2, 10)
            [0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0],  # 3: X ở (3, 8)
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4: Cầu 2 ở (4, 10), (5, 10)
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0],  # 6
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 0, 0],  # 7: Đích ở (7, 10)
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0],  # 8
        ],
        "start": (0, 0),
        "switches": [
            {
                "id": "sw_12_split",
                "type": "split",
                "pos": [2, 1],
                "split_to": [[0, 3], [0, 8]],
                "effects": [],
            },
            {
                "id": "sw_12_soft_1",
                "type": "soft",
                "pos": [0, 1],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
            {
                "id": "sw_12_soft_2",
                "type": "soft",
                "pos": [0, 11],
                "effects": [{"action": "open", "bridge_id": 1}],
            },
            {
                "id": "sw_12_heavy",
                "type": "heavy",
                "pos": [3, 8],
                "effects": [{"action": "open", "bridge_id": 2}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[1, 4], [1, 5]],
                "initially_open": False,
            },
            1: {
                "tiles": [[1, 6], [1, 7]],
                "initially_open": False,
            },
            2: {
                "tiles": [[4, 10], [5, 10]],
                "initially_open": False,
            },
        },
    },
]
