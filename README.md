# 🧊 Bloxorz 3D — AI Solver Edition

> **Đồ án môn học:** Cơ sở Trí tuệ Nhân tạo (CSAI) — **Nhóm 6**  
> Mô phỏng tựa game giải đố kinh điển **Bloxorz** với đồ họa 3D thời gian thực (Raylib) tích hợp hệ thống giải tự động bằng các thuật toán tìm kiếm kinh điển trong AI.

---

## 📌 Giới thiệu dự án

Dự án tái hiện trọn vẹn trò chơi **Bloxorz** trên không gian 3D hiện đại và ứng dụng các kỹ thuật tìm kiếm không gian trạng thái (State Space Search) để tìm đường đi tối ưu đưa khối trụ rơi chuẩn xác vào lỗ đích.

### 🌟 Tính năng nổi bật
* **Đồ họa 3D tương tác mượt mà (Raylib)**: Đạt 60 FPS ổn định, hỗ trợ xoay góc nhìn, hiệu ứng đổ bóng, ánh sáng động, hiệu ứng hạt va chạm (spark particles) và hệ thống skin đa dạng.
* **Mô phỏng đầy đủ cơ chế Bloxorz chuẩn**:
  * 12 màn chơi từ cơ bản đến phức tạp (Đầy đủ chướng ngại, sàn hẹp, bẫy cam).
  * Ô sàn cam sụt lún (Fragile tiles - vỡ khi khối đứng thẳng).
  * Công tắc tròn mềm (Soft switch) & công tắc chữ X nặng (Heavy switch).
  * Công tắc phân tách khối (Split switch) biến khối $1 \times 1 \times 2$ thành 2 khối nhỏ $1 \times 1 \times 1$.
  * Hệ thống cầu cơ học nâng hạ / chuyển đổi trạng thái logic linh hoạt.
* **Hệ thống AI Solvers toàn diện**:
  * **BFS (Breadth-First Search)**: Tìm đường đi ngắn nhất theo số bước di chuyển.
  * **DFS / IDS (Depth-First Search / Iterative Deepening)**: Tìm kiếm theo chiều sâu với cơ chế giới hạn trạng thái thông minh.
  * **UCS (Uniform Cost Search)**: Tìm kiếm đường đi tối ưu theo hàm chi phí trọng số.
  * **A\* (A-Star Search)**: Sử dụng hàm Heuristic khoảng cách Manhattan 3D được thiết kế tối ưu, tính toán chính xác trên cả trạng thái khối đơn lẫn khối phân thân.
* **Trực quan hóa bước giải (Auto-Play Visualizer)**: Cho phép xem AI tự động thực thi từng bước đi trực tiếp trên bàn cờ 3D.
* **Bộ đo kiểm Benchmark & Vẽ biểu đồ**: Tự động đo thời gian tính toán ($ms$), bộ nhớ RAM ($KB$), số trạng thái đã duyệt (Nodes Expanded) và xuất biểu đồ so sánh chi tiết.
* **Âm thanh tổng hợp (Procedural Audio)**: Tự tạo BGM Ambient Cosmic và SFX chân thực hoàn toàn bằng mã nguồn Python mà không cần tải tài nguyên âm thanh ngoài.

---

## 📁 Cấu trúc thư mục

```text
Bloxorz-CSAI-Nhom6/
├── assets/                     # Tài nguyên âm thanh và font chữ
│   └── sounds/                 # Âm thanh SFX & BGM được tự động sinh
├── solvers/                    # Các thuật toán tìm kiếm AI
│   ├── base.py                 # Mô hình hóa không gian trạng thái & hàm mô phỏng
│   ├── astar.py                # Thuật toán A* & hàm Heuristic tối ưu
│   ├── bfs.py                  # Thuật toán Breadth-First Search
│   ├── dfs.py                  # Thuật toán Depth-First Search & IDS
│   └── ucs_solver.py           # Thuật toán Uniform Cost Search
├── ui/                         # Hệ thống giao diện đồ họa 3D & 2D HUD (Raylib)
│   ├── animation.py            # Xử lý chuyển động lăn khối & mượt hóa
│   ├── effects.py              # Hiệu ứng hạt va chạm, vũ trụ không gian
│   ├── font_manager.py         # Quản lý font chữ và hiển thị tiếng Việt có dấu
│   ├── render3d.py             # Dựng bàn cờ, khối trụ, công tắc và hiệu ứng 3D
│   ├── widgets.py              # Các nút bấm, nhãn và hộp thoại UI
│   └── screens/                # Các màn hình: Menu, Chọn màn, Hướng dẫn, HUD
├── ai_controller.py            # Bộ điều phối luồng chạy AI trên giao diện
├── app.py                      # Bản giao diện Web API (Flask)
├── app_state.py                # Quản lý trạng thái ứng dụng toàn cục
├── audio_manager.py            # Điều khiển phát nhạc nền & hiệu ứng âm thanh
├── audio_synth.py              # Bộ tổng hợp âm thanh Procedural WAV
├── benchmark.py                # Kịch bản benchmark tự động 4 thuật toán trên 12 màn
├── config.py                   # Bảng màu, cấu hình đồ họa, danh sách màn chơi
├── game.py                     # Quy tắc và logic lõi trò chơi Bloxorz
├── levels.py                   # Dữ liệu ma trận và cơ chế của 12 màn chơi
├── raylib_app.py               # Điểm khởi chạy chính của trò chơi (Main 3D App)
├── requirements.txt            # Danh sách các thư viện phụ thuộc
└── README.md                   # Hướng dẫn sử dụng dự án
```

---

## 🛠️ Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống
* **Python**: Phiên bản `3.10` trở lên (Khuyến nghị Python 3.11 hoặc 3.12).
* Hệ điều hành: macOS, Windows, Linux.

### 2. Thiết lập môi trường ảo (Khuyến nghị)

```bash
# Clone repository về máy (nếu chưa clone)
git clone https://github.com/thang2608/Bloxorz-CSAI-Nhom6.git
cd Bloxorz-CSAI-Nhom6

# Khởi tạo môi trường ảo
python3 -m venv .venv

# Kích hoạt môi trường ảo:
# Trên macOS / Linux:
source .venv/bin/activate
# Trên Windows:
# .venv\Scripts\activate
```

### 3. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

---

## 🚀 Hướng dẫn khởi chạy

### 🎮 1. Chạy trò chơi đồ họa 3D (Raylib - Ứng dụng chính)
```bash
python raylib_app.py
```
*(Nếu trên máy tính của bạn lệnh `python` chưa gắn với Python 3, hãy chạy `python3 raylib_app.py`)*

### 🌐 2. Chạy phiên bản Web (Flask)
```bash
python app.py
```
Sau đó mở trình duyệt tại địa chỉ: `http://127.0.0.1:5000`

### 📊 3. Chạy đo kiểm Benchmark thuật toán AI
Để đo thời gian thực thi, dung lượng RAM và số bước đi của 4 thuật toán trên cả 12 màn:
```bash
python benchmark.py
```
Kết quả đo sẽ được xuất tự động ra file `benchmark_results.csv`.

---

## 🎮 Hướng dẫn điều khiển trong trò chơi

| Phím bấm / Thao tác | Chức năng |
| :--- | :--- |
| `↑` `↓` `←` `→` hoặc `W` `A` `S` `D` | Lăn khối trụ theo 4 hướng |
| `SPACE` | Đổi quyền điều khiển giữa 2 khối nhỏ (khi bị phân tách) |
| Nút `Solve` / `AI Solver` | Kích hoạt AI giải tự động màn hiện tại |
| Nút chọn thuật toán trên HUD | Chuyển đổi giữa các thuật toán: `A*`, `BFS`, `UCS`, `DFS` |
| `R` | Chơi lại màn hiện tại (Reset) |
| `M` | Bật / Tắt nhạc nền (BGM) |
| `K` | Bật / Tắt hiệu ứng âm thanh (SFX) |
| `ESC` | Quay lại Menu chính |
| `F11` | Bật / Tắt chế độ Toàn màn hình (Fullscreen) |

---

## 🧠 Tổng quan các thuật toán AI

1. **A\* Search (Thuật toán chính)**:
   * Sử dụng hàm đánh giá $f(n) = g(n) + h(n)$.
   * Hàm $h(n)$ dựa trên khoảng cách Manhattan 3D mở rộng có tính đến kích thước khối và vị trí ô đích. Đối với trạng thái phân thân (Split), heuristic lấy tổng khoảng cách kết hợp hai khối để đảm bảo tính nhất quán (Consistent) và chấp nhận được (Admissible).
2. **Breadth-First Search (BFS)**:
   * Mở rộng theo từng tầng, bảo đảm luôn tìm ra lời giải có số bước di chuyển ít nhất.
3. **Uniform Cost Search (UCS)**:
   * Tìm kiếm theo chi phí đường đi tăng dần, phù hợp khi các bước di chuyển có trọng số khác nhau (ví dụ: hành động đổi khối `SWITCH` có chi phí nhỏ hơn di chuyển thông thường).
4. **Depth-First Search (DFS)**:
   * Mở rộng nhánh sâu nhất có thể, tích hợp tập trạng thái đã duyệt (Visited Set) và giới hạn độ sâu/số nút để tránh vòng lặp vô tận.

---

## 👥 Nhóm tác giả

* **Đồ án Cơ sở Trí tuệ Nhân tạo (CSAI) — Nhóm 6**
* Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM
