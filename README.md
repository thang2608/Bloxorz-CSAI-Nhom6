# Bloxorz 3D - AI Solver

Đồ án môn học: **Cơ sở Trí tuệ Nhân tạo (CSAI) - Nhóm 6**  
Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM

Chương trình mô phỏng trò chơi giải đố Bloxorz trên không gian 3D bằng Python và thư viện Raylib, tích hợp các thuật toán tìm kiếm không gian trạng thái để tìm đường đi tự động cho các màn chơi.

---

## 1. Giới thiệu & Tính năng

- **Đồ họa 3D (Raylib)**: Xây dựng bằng `raylib-py`, hỗ trợ camera xoay góc nhìn, hiệu ứng chuyển động lăn khối, âm thanh và hiệu ứng va chạm.
- **Mô phỏng 12 màn chơi với đầy đủ cơ chế của Bloxorz**:
  - Ô sàn cam (Fragile tile): Sẽ vỡ và làm rơi khối nếu đứng thẳng lên trên.
  - Công tắc mềm (hình tròn) và công tắc nặng (chữ X): Đóng/mở hoặc chuyển đổi trạng thái các cây cầu.
  - Công tắc phân thân (Split tile): Tách khối trụ $1 \times 1 \times 2$ thành 2 khối nhỏ $1 \times 1 \times 1$, hỗ trợ phím chuyển đổi điều khiển qua lại.
- **Các thuật toán AI tìm kiếm đường đi**:
  - **BFS (Breadth-First Search)**: Tìm nghiệm tối ưu về số bước di chuyển.
  - **DFS / IDS (Depth-First Search / Iterative Deepening)**: Tìm kiếm theo chiều sâu kèm tập lưu trạng thái đã duyệt (`visited`).
  - **UCS (Uniform Cost Search)**: Tìm kiếm đường đi tối ưu theo chi phí di chuyển.
  - **A\* Search**: Sử dụng hàm Heuristic ước lượng khoảng cách Manhattan kết hợp giữa vị trí khối và ô đích, hỗ trợ đánh giá cho cả trạng thái đơn lẫn trạng thái phân thân.
- **Trực quan hóa lời giải (Visualizer)**: Xem AI tự động thực hiện lần lượt các bước đi tìm được trực tiếp trên bàn cờ 3D.

---

## 2. Cấu trúc thư mục

```text
.
├── assets/                     # Tài nguyên âm thanh và font chữ
│   └── sounds/                 # Các file âm thanh WAV
├── solvers/                    # Mã nguồn các thuật toán tìm kiếm
│   ├── base.py                 # Hàm trích xuất trạng thái, kiểm tra hợp lệ, luật di chuyển
│   ├── astar.py                # Thuật toán A* và hàm Heuristic
│   ├── bfs.py                  # Thuật toán BFS
│   ├── dfs.py                  # Thuật toán DFS và IDS
│   └── ucs_solver.py           # Thuật toán UCS
├── ui/                         # Các module giao diện 3D và 2D HUD (Raylib)
│   ├── animation.py            # Hoạt ảnh lăn khối và nội suy chuyển động
│   ├── effects.py              # Hiệu ứng đồ họa phụ trợ
│   ├── font_manager.py         # Quản lý hiển thị font chữ tiếng Việt
│   ├── render3d.py             # Dựng hình bàn cờ, khối trụ và công tắc 3D
│   ├── widgets.py              # Xử lý nút bấm và giao diện HUD
│   └── screens/                # Giao diện menu, chọn màn, hướng dẫn
├── ai_controller.py            # Quản lý luồng gọi thuật toán và animation tự giải
├── app_state.py                # Quản lý trạng thái màn hình và cấu hình chạy
├── audio_manager.py            # Quản lý phát nhạc nền và hiệu ứng âm thanh
├── audio_synth.py              # Bộ sinh âm thanh procedural (WAV)
├── config.py                   # Cấu hình kích thước, màu sắc, tên màn chơi
├── game.py                     # Logic game Bloxorz
├── levels.py                   # Bản đồ và dữ liệu cấu hình 12 màn chơi
├── raylib_app.py               # Điểm khởi chạy ứng dụng 3D chính
├── requirements.txt            # Danh sách thư viện phụ thuộc
└── README.md                   # Hướng dẫn sử dụng
```

---

## 3. Cài đặt

### Yêu cầu
- Python 3.10 trở lên.
- Các hệ điều hành: macOS, Windows, Linux.

### Cài đặt môi trường

Khuyến nghị tạo môi trường ảo (`venv`) trước khi cài đặt:

```bash
# Tạo môi trường ảo
python3 -m venv .venv

# Kích hoạt môi trường ảo:
# Trên macOS / Linux:
source .venv/bin/activate
# Trên Windows:
# .venv\Scripts\activate

# Cài đặt thư viện
pip install -r requirements.txt
```

---

## 4. Hướng dẫn chạy chương trình

Chạy ứng dụng game 3D chính:

```bash
python raylib_app.py
```

*(Nếu hệ thống chưa trỏ `python` về Python 3, dùng `python3 raylib_app.py`)*

---

## 5. Phím điều khiển trong game

| Phím | Chức năng |
| :--- | :--- |
| `↑` `↓` `←` `→` hoặc `W` `A` `S` `D` | Lăn khối trụ theo 4 hướng |
| `Space` | Chuyển đổi giữa 2 khối con (khi đang ở trạng thái phân thân) |
| Nút `Solve` trên màn hình | Kích hoạt AI tự động giải màn hiện tại |
| Nút chọn thuật toán trên HUD | Đổi qua lại giữa các thuật toán: `A*`, `BFS`, `UCS`, `DFS` |
| `R` | Chơi lại màn hiện tại (Reset) |
| `M` | Bật / tắt nhạc nền (BGM) |
| `K` | Bật / tắt hiệu ứng âm thanh (SFX) |
| `Esc` | Quay về màn hình Menu |
| `F11` | Bật / tắt toàn màn hình |
