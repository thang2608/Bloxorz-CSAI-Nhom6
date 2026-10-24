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
    # MÀN 2: Sàn dễ vỡ (Fragile Tiles - Màu cam)
    # ─────────────────────────────────────────────
    {
        "id": 2,
        "name": "Màn 2: Sàn cam dễ vỡ",
        "description": "Khối chỉ được NẰM đè lên ô cam. Đứng thẳng lên ô cam sẽ làm sàn vỡ và rơi!",
        "board": [
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 3, 3, 1, 1],
            [0, 1, 1, 3, 3, 1, 1],
            [0, 0, 0, 0, 1, 1, 2],
            [0, 0, 0, 0, 1, 1, 1],
        ],
        "start": (0, 1),
        "switches": [],
        "bridges": {},
    },

    # ─────────────────────────────────────────────
    # MÀN 3: Cầu & Công tắc mềm (Soft Switch)
    # ─────────────────────────────────────────────
    {
        "id": 3,
        "name": "Màn 3: Cầu & Công tắc mềm",
        "description": "Chạm bất kỳ phần nào của khối lên công tắc tròn để bật cầu bắc qua vực.",
        "board": [
            [1, 1, 1, 1, 0, 0, 0, 1, 1, 1],
            [1, 1, 1, 1, 0, 0, 0, 1, 1, 1],
            [1, 1, 1, 1, 0, 0, 0, 1, 2, 1],
            [0, 1, 1, 0, 0, 0, 0, 1, 1, 1],
        ],
        "start": (0, 0),
        "switches": [
            {
                "id": "sw_soft_1",
                "type": "soft",
                "pos": [0, 3],
                "effects": [{"action": "toggle", "bridge_id": 0}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[1, 4], [1, 5], [1, 6]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 4: Công tắc nặng (Heavy Switch - Chữ X)
    # ─────────────────────────────────────────────
    {
        "id": 4,
        "name": "Màn 4: Công tắc nặng (Chữ X)",
        "description": "Công tắc X chỉ kích hoạt khi khối ĐỨNG THẲNG trên nó. Nằm đè lên sẽ không có tác dụng!",
        "board": [
            [1, 1, 1, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 0, 1, 0, 0, 1, 2],
        ],
        "start": (0, 0),
        "switches": [
            {
                "id": "sw_heavy_1",
                "type": "heavy",
                "pos": [1, 2],
                "effects": [{"action": "toggle", "bridge_id": 0}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[2, 4], [2, 5], [3, 4], [3, 5], [4, 4], [4, 5]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 5: Tách Khối & Hợp Nhất (Split Switch)
    # ─────────────────────────────────────────────
    {
        "id": 5,
        "name": "Màn 5: Phân thân () & Hợp nhất",
        "description": "Đứng thẳng lên () để tách thành 2 khối nhỏ. Dùng Space/Tab đổi khối điều khiển để mở cầu, rồi gộp lại!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9
            [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1],  # 0
            [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1],  # 1
            [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1],  # 2: cầu ở (2,4), (2,5), (2,6)
            [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1],  # 3
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1],  # 4: đích ở (4, 9)
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],  # 5
        ],
        "start": (3, 1),
        "switches": [
            {
                "id": "sw_split_1",
                "type": "split",
                "pos": [1, 1],
                "split_to": [[1, 2], [1, 8]],
                "effects": [],
            },
            {
                "id": "sw_soft_open",
                "type": "soft",
                "pos": [0, 8],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[2, 4], [2, 5], [2, 6]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 6: Cầu Kép Đảo Chiều (Dual Bridges)
    # ─────────────────────────────────────────────
    {
        "id": 6,
        "name": "Màn 6: Cầu Kép Đảo Chiều",
        "description": "Hai cây cầu phụ thuộc lẫn nhau: mở cầu này sẽ đóng cầu kia. Hãy tính toán lộ trình!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],  # 0
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],  # 1: cầu 0 ở (1,4)-(1,5), cầu 1 ở (1,10)-(1,11)
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 2, 1],  # 2: đích ở (2, 13)
            [0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],  # 3
        ],
        "start": (0, 0),
        "switches": [
            {
                "id": "sw_soft_A",
                "type": "soft",
                "pos": [0, 3],
                "effects": [
                    {"action": "open", "bridge_id": 0},
                    {"action": "close", "bridge_id": 1},
                ],
            },
            {
                "id": "sw_heavy_B",
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
                "tiles": [[1, 10], [1, 11]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 7: Thử Thách Bậc Thầy (Master Puzzle)
    # ─────────────────────────────────────────────
    {
        "id": 7,
        "name": "Màn 7: Thử Thách Bậc Thầy",
        "description": "Kết hợp Sàn cam dễ vỡ, Công tắc X nặng, Công tắc mềm và Cầu nối bí mật!",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10
            [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],  # 0: X ở (0, 3), công tắc mềm ở (0, 9)
            [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],  # 1: Cầu 0 ở (1, 5), (1, 6)
            [0, 1, 3, 3, 1, 0, 0, 1, 1, 1, 1],  # 2: Ô cam ở (2, 2), (2, 3)
            [0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],  # 3
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4: Cầu 1 ở (4, 8)
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5: Cầu 1 ở (5, 8)
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],  # 6
            [0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 0],  # 7: Đích ở (7, 8)
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],  # 8
        ],
        "start": (0, 1),
        "switches": [
            {
                "id": "sw_heavy_master",
                "type": "heavy",
                "pos": [0, 3],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
            {
                "id": "sw_soft_master",
                "type": "soft",
                "pos": [0, 9],
                "effects": [{"action": "open", "bridge_id": 1}],
            },
        ],
        "bridges": {
            0: {
                "tiles": [[1, 5], [1, 6]],
                "initially_open": False,
            },
            1: {
                "tiles": [[4, 8], [5, 8]],
                "initially_open": False,
            },
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 8: Đảo Nổi & Hai Nhịp Cầu
    # ─────────────────────────────────────────────
    {
        "id": 8,
        "name": "Màn 8: Đảo Nổi & Hai Nhịp Cầu",
        "description": "Đảo trung tâm là nơi xoay chuyển trục khối hộp để mở đường đến đích.",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12
            [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1],  # 0
            [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 2, 1],  # 1: Đích ở (1, 11)
            [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1],  # 2
            [0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1],  # 3
        ],
        "start": (0, 0),
        "switches": [
            {
                "id": "sw_8_1",
                "type": "soft",
                "pos": [0, 1],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
            {
                "id": "sw_8_2",
                "type": "heavy",
                "pos": [3, 6],
                "effects": [{"action": "open", "bridge_id": 1}],
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
        },
    },

    # ─────────────────────────────────────────────
    # MÀN 9: Phân Thân Cách Trở
    # ─────────────────────────────────────────────
    {
        "id": 9,
        "name": "Màn 9: Phân Thân Cách Trở",
        "description": "Hai khối nhỏ ở hai bờ vực thẳm phải hỗ trợ nhau mở cầu rồi hội ngộ.",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9 10 11
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],  # 0
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],  # 1
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],  # 2
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1],  # 3: Đích ở (3, 10)
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],  # 4
        ],
        "start": (0, 1),
        "switches": [
            {
                "id": "sw_9_split",
                "type": "split",
                "pos": [2, 1],
                "split_to": [[0, 3], [0, 8]],
                "effects": [],
            },
            {
                "id": "sw_9_soft_left",
                "type": "soft",
                "pos": [2, 3],
                "effects": [{"action": "open", "bridge_id": 0}],
            },
            {
                "id": "sw_9_soft_right",
                "type": "soft",
                "pos": [2, 8],
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
    # MÀN 10: Ván Cờ Sàn Cam & Khóa Chữ X
    # ─────────────────────────────────────────────
    {
        "id": 10,
        "name": "Màn 10: Ván Cờ Sàn Cam & Khóa Chữ X",
        "description": "Tính toán số bước lăn chuẩn xác qua dải sàn cam để kích hoạt công tắc X mở lối về đích.",
        "board": [
            # 0  1  2  3  4  5  6  7  8  9
            [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],  # 0: X ở (0, 8)
            [1, 1, 1, 3, 3, 1, 3, 3, 1, 1],  # 1: ô (1, 5) là đệm 1
            [1, 1, 1, 3, 3, 1, 3, 3, 1, 1],  # 2: ô (2, 5) là đệm 1
            [0, 1, 1, 0, 0, 0, 0, 1, 1, 0],  # 3
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 4: Cầu ở (4, 1), (4, 2)
            [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],  # 5
            [0, 1, 2, 1, 0, 0, 0, 0, 0, 0],  # 6: Đích ở (6, 2)
            [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],  # 7
        ],
        "start": (0, 1),
        "switches": [
            {
                "id": "sw_10_heavy",
                "type": "heavy",
                "pos": [0, 8],
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
    # MÀN 11: Ba Cầu Liên Hoàn
    # ─────────────────────────────────────────────
    {
        "id": 11,
        "name": "Màn 11: Ba Cầu Liên Hoàn",
        "description": "Mở tuần tự ba nhịp cầu phụ thuộc lẫn nhau để vượt qua đại vực thẳm.",
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
    # MÀN 12: Đỉnh Cao Đại Bậc Thầy
    # ─────────────────────────────────────────────
    {
        "id": 12,
        "name": "Màn 12: Đỉnh Cao Đại Bậc Thầy",
        "description": "Thử thách tối thượng kết hợp mọi cơ chế: Phân thân, Sàn cam dễ vỡ, Công tắc X và Cầu nối bí mật!",
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
