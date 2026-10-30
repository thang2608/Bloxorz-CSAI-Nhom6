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
        "description": "Bật công tắc tròn và khóa X nặng để đảo chiều các nhịp cầu, rồi bước lên công tắc tách khối. Hai khối nhỏ 1x1x1 đi được trên sàn cam, hãy đổi qua lại giữa chúng và gộp lại ở đích!",
        # Lời giải ngắn nhất (61 thao tác, X = đổi khối đang điều khiển):
        # DLURDDRRDRRRULLDLDRURDLUULLLDDRRRDRRRRRRRRRRUXDDRDRRRRRRRRRRD
        # Tách khối ở thao tác thứ 28, gộp lại ở (3,14) ngay trước khi vào đích.
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14
            [1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],  # Row 0: Start ở (0, 1)
            [1, 3, 1, 1, 0, 0, 0, 1, 3, 3, 1, 0, 0, 0, 0],  # Row 1: cam (1,1) = chỗ mini A xuất hiện; (1,3) = chỗ mini B xuất hiện
            [1, 3, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 0],  # Row 2: công tắc tách khối ở (2, 2)
            [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 3, 1, 0, 0, 3],  # Row 3
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1],  # Row 4
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 2],  # Row 5: Đích ở (5, 14)
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 6
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],  # Row 7
        ],
        "start": (0, 1),
        "switches": [
            {
                "id": "sw_quantum_1",
                "type": "soft",
                "pos": [2, 6],  # Công tắc mềm giữa đường
                "effects": [
                    {"action": "open", "bridge_id": 0},
                    {"action": "close", "bridge_id": 1},
                ],
            },
            {
                "id": "sw_quantum_heavy",
                "type": "heavy",
                "pos": [4, 7],  # Công tắc X nặng đòi hỏi đứng thẳng
                "effects": [
                    {"action": "open", "bridge_id": 1},
                    {"action": "open", "bridge_id": 2},
                ],
            },
            {
                "id": "sw_quantum_split",
                "type": "split",
                "pos": [2, 2],  # Đứng thẳng lên đây để tách thành 2 khối nhỏ
                "split_to": [[1, 1], [1, 3]],
                "effects": [],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[3, 0], [3, 1], [3, 2], [3, 3]],
                "initially_open": False,
            },
            1: {
                "tiles": [[3, 5], [3, 6], [3, 7]],
                "initially_open": True,
            },
            2: {
                "tiles": [[4, 8], [4, 9], [4, 10], [4, 11], [4, 12]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 6: Phân Thân () & Cầu Kép Viễn Xứ
    # ─────────────────────────────────────────────
    {
        "id": 6,
        "description": "Thử thách đỉnh cao 35 bước: Vượt đầm lầy cam, xoay quanh lỗ rỗng bấm khóa X nặng, mở cầu kép đảo chiều để về đích!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],  # 0: Khóa X nặng ở (0, 11)
            [1, 1, 1, 1, 3, 3, 3, 3, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1],  # 1: Start (1, 1), Cầu 1 (1, 12..13)
            [1, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 1, 0, 0, 1, 2, 1, 1],  # 2: Sàn cam (cols 4..7), Đích ở (2, 15)
            [0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],  # 3: Lỗ rỗng giữa đảo 2 (1, 9..10)
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4: Cầu 0 nối xuống đảo dưới (4, 11)
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5: Cầu 0 (5, 11)
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # 6: Công tắc tròn mở cầu đích ở (6, 8)
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # 7: Đảo đáy 2x6
        ],
        "start": (1, 1),
        "switches": [
            {
                "id": "sw_heavy_x",
                "type": "heavy",
                "pos": [0, 11],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
            {
                "id": "sw_soft_round",
                "type": "soft",
                "pos": [6, 8],
                "effects": [{"action": "open", "bridge_id": 1}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[4, 11], [5, 11]],
                "initially_open": False,
            },
            1: {
                "tiles": [[1, 12], [1, 13]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 7: Cầu Kép Đảo Chiều (Dual Alternating Bridges)
    # ─────────────────────────────────────────────
    {
        "id": 7,
        "description": "Bật công tắc để mở cầu, đứng thẳng lên công tắc X để mở cầu tiếp theo. Cẩn thận các ô cam dễ vỡ!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0],  # 0
            [1, 1, 3, 1, 0, 0, 1, 3, 1, 1, 0, 0, 0, 0, 0],  # 1: Start (1,1) | Cầu 0 (1,4..5)
            [1, 1, 1, 1, 0, 0, 1, 3, 1, 3, 0, 0, 0, 0, 0],  # 2: Switch (2,2) | X (2,8)
            [0, 0, 0, 0, 0, 0, 1, 3, 1, 1, 0, 0, 0, 0, 0],  # 3: Cầu 1 (4..5, 7) đi xuống từ (3,7)
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4: Cầu 1 (4,7)
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5: Cầu 1 (5,7)
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],  # 6
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 3, 1],  # 7: Switch (7,6) | Cầu 2 (7,10..11)
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 2, 1],  # 8: ĐÍCH (8,13)
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],  # 9
        ],
        "start": (1, 1),
        "switches": [
            {
                "id": "sw_14_a",
                "type": "soft",
                "pos": [2, 2],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
            {
                "id": "sw_14_b",
                "type": "heavy",
                "pos": [2, 8],
                "effects": [{"action": "open", "bridge_id": 1}],
            },
            {
                "id": "sw_14_c",
                "type": "soft",
                "pos": [7, 6],
                "effects": [{"action": "open", "bridge_id": 2}],
            },
        ],
        "bridges": {
            0: {"tiles": [[1, 4], [1, 5]], "initially_open": False},
            1: {"tiles": [[4, 7], [5, 7]], "initially_open": False},
            2: {"tiles": [[7, 10], [7, 11]], "initially_open": False},
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 8: Mê Cung Sàn Cam & Khóa Chữ X Liên Hoàn
    # ─────────────────────────────────────────────
    {
        "id": 8,
        "description": "Cả bản đồ rải đầy sàn cam dễ vỡ. Chỉ được đứng thẳng trên ô xám thường, hãy tìm nhịp lăn chính xác để tới lỗ đích!",
        "board": [
            [0, 1, 1, 1, 3, 1, 3, 1, 3, 1, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
            [3, 1, 1, 0, 1, 3, 2, 1, 0, 3, 1, 1, 1],
            [3, 1, 0, 3, 1, 0, 3, 1, 1, 1, 0, 3, 1],
            [3, 1, 1, 1, 3, 1, 1, 0, 3, 1, 1, 1, 3],
            [1, 1, 1, 0, 1, 3, 3, 3, 0, 1, 3, 0, 0],
            [0, 1, 1, 1, 3, 0, 1, 1, 3, 1, 1, 1, 0],
        ],
        "start": (6, 2),
        "switches": [
        ],
        "bridges": {
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 9: Quần Đảo Nổi & Ba Nhịp Cầu
    # ─────────────────────────────────────────────
    {
        "id": 9,
        "description": "Hai công tắc tròn ở hai đầu bản đồ, mỗi cái mở một nhịp cầu. Phải đi vòng, bật đúng thứ tự rồi quay lại băng qua cầu.",
        "board": [
            [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1],
            [1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0],
            [1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1],
            [0, 0, 2, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0],
        ],
        "start": (4, 8),
        "switches": [
            {"id": "sw_14_s0", "type": "soft", "pos": [5, 4], "effects": [{"action": "open", "bridge_id": 0}]},
            {"id": "sw_14_s1", "type": "soft", "pos": [1, 1], "effects": [{"action": "open", "bridge_id": 1}]},
        ],
        "bridges": {
            0: {"tiles": [[0, 4], [0, 5], [0, 6]], "initially_open": False},
            1: {"tiles": [[4, 3], [4, 4], [4, 5]], "initially_open": False},
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 10: Phân Thân Băng Qua Sàn Cam (Mini Block Fragile Run)
    # ─────────────────────────────────────────────
    {
        "id": 10,
        "description": "Công tắc tròn mở cầu thứ nhất, khóa X nặng (phải đứng thẳng) mở cầu thứ hai, giữa đường là sàn cam dễ vỡ.",
        "board": [
            [1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 3, 1, 0],
            [1, 0, 1, 3, 1, 0, 1, 1, 0, 0, 1, 1, 1],
            [1, 3, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 3, 0, 3, 0, 0, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 0, 2, 0, 1, 1, 1, 0],
            [1, 3, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0],
            [1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        ],
        "start": (3, 10),
        "switches": [
            {"id": "sw_15_s0", "type": "soft", "pos": [4, 9], "effects": [{"action": "open", "bridge_id": 0}]},
            {"id": "sw_15_s1", "type": "heavy", "pos": [7, 1], "effects": [{"action": "open", "bridge_id": 1}]},
        ],
        "bridges": {
            0: {"tiles": [[2, 12], [3, 12], [4, 12]], "initially_open": False},
            1: {"tiles": [[3, 8], [3, 9]], "initially_open": False},
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 11: Ba Cầu Liên Hoàn Đảo Chiều (Triple Interlocking Bridges)
    # ─────────────────────────────────────────────
    {
        "id": 11,
        "description": "Ba nhịp cầu, công tắc tròn vừa mở vừa đóng cầu khác, khóa X nặng và sàn cam. Sai một nhịp là phải làm lại!",
        "board": [
            [3, 1, 1, 1, 1, 3, 0, 1, 3, 1, 1, 1, 1, 1],
            [1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0],
            [0, 0, 0, 2, 0, 1, 0, 1, 0, 3, 1, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1],
            [1, 3, 1, 3, 3, 1, 0, 1, 1, 1, 0, 1, 0, 1],
            [3, 1, 3, 0, 1, 1, 1, 1, 0, 0, 1, 1, 3, 1],
            [0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 3, 1, 0, 0],
            [0, 3, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 3],
        ],
        "start": (7, 11),
        "switches": [
            {"id": "sw_16_s0", "type": "soft", "pos": [5, 13], "effects": [{"action": "open", "bridge_id": 0}, {"action": "close", "bridge_id": 1}]},
            {"id": "sw_16_s1", "type": "heavy", "pos": [6, 1], "effects": [{"action": "open", "bridge_id": 2}]},
            {"id": "sw_16_s2", "type": "soft", "pos": [0, 2], "effects": [{"action": "open", "bridge_id": 1}]},
        ],
        "bridges": {
            0: {"tiles": [[1, 9], [1, 10]], "initially_open": False},
            1: {"tiles": [[2, 11], [2, 12], [2, 13]], "initially_open": True},
            2: {"tiles": [[1, 5], [1, 6], [1, 7]], "initially_open": False},
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 12: Đỉnh Cao Đại Bậc Thầy (The Grandmaster Climax)
    # ─────────────────────────────────────────────
    {
        "id": 12,
                "description": "5 nhịp cầu đóng/mở đảo chiều, công tắc X nặng và sàn cam dễ vỡ. Mỗi nước đi đều có thể là nước đi cuối cùng!",
                "board": [
                    # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
                    [1, 1, 1, 1, 0, 0, 0, 0, 1, 3, 1, 1, 3, 1, 0, 0],  # 0
                    [1, 1, 1, 3, 3, 0, 0, 1, 3, 1, 1, 1, 1, 1, 0, 0],  # 1: Start (1,1) | Switch (1,2) | Cầu 0 (1,5..6) | X (1,9)
                    [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0],  # 2: Cầu 1 (2,11)
                    [0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],  # 3: Cầu 1 (3,11)
                    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],  # 4
                    [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 3, 1, 1, 1, 0],  # 5: Switch (5,12)
                    [0, 0, 1, 1, 3, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0],  # 6: Cầu 2 (6,12)
                    [0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0],  # 7: Cầu 2 (7,12)
                    [0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 3, 0, 1, 1, 0],  # 8: X (8,8) | Cầu 3 (8,5..6)
                    [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 3, 1, 1],  # 9: Cầu 4 (9,2)
                    [2, 1, 0, 1, 1, 3, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],  # 10: ĐÍCH (10,0) | Switch (10,3) | Cầu 4 (10,2)
                    [0, 0, 0, 1, 1, 3, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],  # 11
                ],
                "start": (1, 1),
                "switches": [
                    {
                        "id": "sw_13_a",
                        "type": "soft",
                        "pos": [1, 2],
                        "effects": [{"action": "open", "bridge_id": 0}],
                    },
                    {
                        "id": "sw_13_b",
                        "type": "heavy",
                        "pos": [1, 9],
                        "effects": [
                            {"action": "open", "bridge_id": 1},
                            {"action": "close", "bridge_id": 0},
                        ],
                    },
                    {
                        "id": "sw_13_c",
                        "type": "soft",
                        "pos": [5, 12],
                        "effects": [
                            {"action": "open", "bridge_id": 2},
                            {"action": "close", "bridge_id": 1},
                        ],
                    },
                    {
                        "id": "sw_13_d",
                        "type": "heavy",
                        "pos": [8, 8],
                        "effects": [
                            {"action": "open", "bridge_id": 0},
                            {"action": "open", "bridge_id": 3},
                        ],
                    },
                    {
                        "id": "sw_13_e",
                        "type": "soft",
                        "pos": [10, 3],
                        "effects": [
                            {"action": "close", "bridge_id": 2},
                            {"action": "open", "bridge_id": 4},
                        ],
                    },
                ],
                "bridges": {
                    0: {"tiles": [[1, 5], [1, 6]], "initially_open": False},
                    1: {"tiles": [[2, 11], [3, 11]], "initially_open": False},
                    2: {"tiles": [[6, 12], [7, 12]], "initially_open": False},
                    3: {"tiles": [[8, 5], [8, 6]], "initially_open": False},
                    4: {"tiles": [[9, 2], [10, 2]], "initially_open": False},
                },
    },
]
