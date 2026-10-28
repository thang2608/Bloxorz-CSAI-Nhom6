# app_state.py — Ngữ cảnh tập trung quản lý State, Game instance, Camera, Skin và Animation
import math
try:
    import pyray as rl
except ImportError:
    from raylib import pyray as rl

from game import BloxorzGame
from config import STATE_MENU, STATE_PLAYING, BLOCK_SKINS

class AppContext:
    def __init__(self):
        # 1. Trạng thái Trò chơi
        self.game = BloxorzGame(0)
        self.current_state = STATE_MENU

        # 2. Camera Orbital 3D
        self.camera = rl.Camera3D()
        self.camera.up = rl.Vector3(0.0, 1.0, 0.0)
        self.camera.fovy = 45.0
        self.camera.projection = rl.CAMERA_PERSPECTIVE

        self.target_yaw = -25.0
        self.target_pitch = 48.0
        self.target_dist = 18.0
        self.cam_yaw = -25.0
        self.cam_pitch = 48.0
        self.cam_dist = 18.0
        self.spin_timer = 0.0

        # 3. Hoạt ảnh Lật Vật lý 3D quanh Cạnh Đáy
        self.roll_animating = False
        self.anim_time = 0.0
        self.anim_duration = 0.14
        self.roll_angle = 0.0
        self.roll_y_offset = 0.0
        self.roll_info = {}
        self.buffered_move = None

        # 4. Quản lý Cô lập Trạng thái Tutorial
        self.tutorial_game = None
        self.current_tutorial_idx = 0
        self.completed_tutorials = set()
        self.show_tutorial_hint = False
        self.main_game_snapshot = None
        self.main_game_camera = None

        # 5. Hệ thống Điều khiển Thuật toán AI
        self.current_solver_idx = 0
        self.ai_move_queue = []
        self.ai_stats = None
        self.show_solvers_dropdown = False
        self.solver_names = ["A*", "BFS", "DFS", "UCS", "IDS"]

        # 6. Hệ thống 6 Skin Khối 3D Cao Cấp
        self.current_skin_idx = 0

    def cycle_skin(self, step=1):
        """Chuyển đổi qua lại giữa 6 Skin khối 3D"""
        self.current_skin_idx = (self.current_skin_idx + step) % len(BLOCK_SKINS)
        return self.current_skin_idx

    def get_current_skin(self):
        """Trả về dict cấu hình của Skin đang được chọn"""
        return BLOCK_SKINS[self.current_skin_idx % len(BLOCK_SKINS)]

    def reset_camera(self):
        """Căn chỉnh camera tự động bao quát chính giữa bàn cờ hiện tại"""
        self.target_yaw = -25.0
        self.target_pitch = 48.0
        self.target_dist = max(self.game.rows, self.game.cols) * 1.48 + 4.0
        self.cam_yaw = self.target_yaw
        self.cam_pitch = self.target_pitch
        self.cam_dist = self.target_dist

    def update_camera_coords(self):
        """Cập nhật tọa độ position và target cho Camera3D theo tọa độ cầu"""
        center_c = (self.game.cols - 1) / 2.0
        center_r = (self.game.rows - 1) / 2.0
        self.camera.target = rl.Vector3(center_c, 0.0, center_r)

        rad_yaw = math.radians(self.cam_yaw)
        rad_pitch = math.radians(self.cam_pitch)
        eye_x = center_c + self.cam_dist * math.cos(rad_pitch) * math.sin(rad_yaw)
        eye_y = self.cam_dist * math.sin(rad_pitch)
        eye_z = center_r + self.cam_dist * math.cos(rad_pitch) * math.cos(rad_yaw)
        self.camera.position = rl.Vector3(eye_x, eye_y, eye_z)

    def load_and_play_level(self, idx):
        """Nạp màn chơi và chuyển thẳng vào gameplay"""
        self.roll_animating = False
        self.buffered_move = None
        self.roll_angle = 0.0
        self.roll_y_offset = 0.0
        self.ai_move_queue.clear()
        self.game.load_level(idx)
        self.reset_camera()
        self.current_state = STATE_PLAYING

# Singleton Context dùng chung cho toàn bộ ứng dụng
ctx = AppContext()
