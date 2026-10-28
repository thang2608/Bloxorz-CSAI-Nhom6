# audio_manager.py
"""
Hệ thống Quản lý Âm thanh Toàn diện cho Bloxorz 3D (Audio Manager).
Bao gồm:
- Tự động nạp hoặc tổng hợp tài nguyên âm thanh (BGM & SFX).
- Phát nhạc nền Ambient Cosmic lặp mượt mà không khựng.
- Phát hiệu ứng âm thanh (SFX) chính xác cho mọi tương tác gameplay & UI.
- Điều khiển Bật/Tắt Nhạc (phím M) và SFX (phím K).
- Khối try...except an toàn bao bọc toàn bộ tương tác Raylib Audio.
"""

import os
try:
    import pyray as rl
except ImportError:
    from raylib import pyray as rl

import audio_synth

# ── Cấu hình & Trạng thái Toàn cục ──
SOUNDS_DIR = "assets/sounds"
BGM_VOLUME = 0.65
SFX_VOLUME = 0.78

bgm_enabled = True
sfx_enabled = True
device_initialized = False

_sounds = {}
_music = None
_last_hovered_id = None


def init_audio():
    """Khởi tạo thiết bị Audio Raylib, chuẩn bị file âm thanh và nạp vào bộ nhớ."""
    global device_initialized, _music

    # 1. Tự động kiểm tra & sinh file WAV nếu chưa có
    try:
        audio_synth.ensure_sound_assets(SOUNDS_DIR)
    except Exception as e:
        print(f"[AudioManager] Warning: Cannot synthesize audio: {e}")

    # 2. Khởi tạo thiết bị âm thanh Raylib
    try:
        rl.init_audio_device()
        device_initialized = bool(rl.is_audio_device_ready())
    except Exception as e:
        print(f"[AudioManager] Cannot initialize audio device: {e}")
        device_initialized = False
        return

    if not device_initialized:
        print("[AudioManager] Audio device not ready, running in silent mode.")
        return

    # 3. Nạp danh sách các file SFX (.wav, .ogg, .mp3)
    supported_exts = (".wav", ".ogg", ".mp3")
    if os.path.exists(SOUNDS_DIR):
        for fname in os.listdir(SOUNDS_DIR):
            ext = os.path.splitext(fname)[1].lower()
            if ext in supported_exts:
                name_key = os.path.splitext(fname)[0]
                full_path = os.path.join(SOUNDS_DIR, fname)
                if name_key.startswith("bgm"):
                    continue
                try:
                    snd = rl.load_sound(full_path)
                    if hasattr(rl, "is_sound_valid") and rl.is_sound_valid(snd):
                        try:
                            rl.set_sound_volume(snd, SFX_VOLUME)
                        except Exception:
                            pass
                        _sounds[name_key] = snd
                except Exception as e:
                    print(f"[AudioManager] Failed to load sound {fname}: {e}")

    # 4. Nạp Nhạc nền Stream (BGM)
    bgm_candidates = ["bgm_ambient.wav", "bgm_ambient.ogg", "bgm_ambient.mp3"]
    for bgm_file in bgm_candidates:
        bgm_path = os.path.join(SOUNDS_DIR, bgm_file)
        if os.path.exists(bgm_path):
            try:
                m = rl.load_music_stream(bgm_path)
                if hasattr(rl, "is_music_valid") and rl.is_music_valid(m):
                    m.looping = True
                    try:
                        rl.set_music_volume(m, BGM_VOLUME)
                    except Exception:
                        pass
                    _music = m
                    if bgm_enabled:
                        rl.play_music_stream(_music)
                        rl.update_music_stream(_music)
                    break
            except Exception as e:
                print(f"[AudioManager] Failed to load music {bgm_file}: {e}")


def close_audio():
    """Giải phóng toàn bộ tài nguyên âm thanh và đóng thiết bị Audio."""
    global device_initialized, _music, _sounds

    if not device_initialized:
        return

    try:
        if _music is not None:
            try:
                rl.stop_music_stream(_music)
            except Exception:
                pass
            try:
                rl.unload_music_stream(_music)
            except Exception:
                pass
            _music = None

        for snd in _sounds.values():
            try:
                rl.unload_sound(snd)
            except Exception:
                pass
        _sounds.clear()

        rl.close_audio_device()
    except Exception as e:
        print(f"[AudioManager] Error while closing audio: {e}")
    finally:
        device_initialized = False


def update_music():
    """Cập nhật luồng nhạc nền mỗi khung hình. Phải được gọi trong vòng lặp game chính."""
    if not device_initialized or _music is None or not bgm_enabled:
        return
    try:
        rl.update_music_stream(_music)
        # Đảm bảo phát liên tục nếu bị ngắt quãng
        if not rl.is_music_stream_playing(_music):
            rl.play_music_stream(_music)
    except Exception:
        pass


def play_sfx(name):
    """Phát hiệu ứng âm thanh theo tên (ví dụ: 'block_roll', 'ui_select')."""
    if not device_initialized or not sfx_enabled:
        return
    snd = _sounds.get(name)
    if snd is not None:
        try:
            rl.play_sound(snd)
        except Exception:
            pass


def toggle_bgm():
    """Bật hoặc tắt nhạc nền."""
    global bgm_enabled
    bgm_enabled = not bgm_enabled
    if not device_initialized or _music is None:
        return bgm_enabled

    try:
        if bgm_enabled:
            rl.resume_music_stream(_music)
            if not rl.is_music_stream_playing(_music):
                rl.play_music_stream(_music)
        else:
            rl.pause_music_stream(_music)
    except Exception:
        pass
    return bgm_enabled


def toggle_sfx():
    """Bật hoặc tắt hiệu ứng âm thanh."""
    global sfx_enabled
    sfx_enabled = not sfx_enabled
    return sfx_enabled


def is_bgm_enabled():
    return bgm_enabled


def is_sfx_enabled():
    return sfx_enabled


def notify_hover(element_id):
    """
    Theo dõi hover chuột. Nếu vừa di chuột sang một phần tử UI mới,
    phát nhẹ âm thanh ui_nav.
    """
    global _last_hovered_id
    if element_id is not None and element_id != _last_hovered_id:
        play_sfx("ui_nav")
    _last_hovered_id = element_id


def reset_hover():
    """Đặt lại theo dõi hover khi chuyển màn hình."""
    global _last_hovered_id
    _last_hovered_id = None
