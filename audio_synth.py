# audio_synth.py
"""
Bộ tổng hợp âm thanh Procedural WAV Synthesizer cho Bloxorz 3D.
Sử dụng wave, struct, math, random chuẩn của Python để tạo ra các tệp .wav chất lượng cao:
Tần số mẫu: 44100 Hz, 16-bit PCM.
"""

import os
import math
import wave
import struct
import random

SAMPLE_RATE = 44100


def clamp(val, low=-1.0, high=1.0):
    return max(low, min(high, val))


def write_wav(filepath, samples, sample_rate=44100, channels=1):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        raw = bytearray()
        for s in samples:
            if channels == 1:
                val = int(clamp(s) * 32767)
                raw.extend(struct.pack("<h", val))
            else:
                left, right = s
                val_l = int(clamp(left) * 32767)
                val_r = int(clamp(right) * 32767)
                raw.extend(struct.pack("<hh", val_l, val_r))
        wf.writeframes(raw)


def gen_bgm_ambient(filepath):
    """
    Bản nhạc nền Ambient Vũ trụ thư giãn, sang trọng và chuẩn độ lớn (Audible & Balanced).
    Thời lượng: 16.0 giây, stereo, nối vòng lặp mượt mà không khựng.
    Hợp âm Cmaj9 - Am9 - Fmaj7 - G6 kết hợp Bass ấm, Pad mượt và Arpeggio chuông sao.
    """
    duration = 16.0
    num_samples = int(SAMPLE_RATE * duration)
    raw_samples = []

    # 4 Hợp âm tương ứng với 4 ô nhịp (4.0s mỗi nhịp)
    chord_data = [
        # Cmaj9
        {
            "bass": 65.41,
            "pad": [130.81, 196.00, 246.94, 329.63, 392.00, 587.33],
            "arp": [261.63, 329.63, 392.00, 493.88, 587.33, 783.99],
        },
        # Am9
        {
            "bass": 55.00,
            "pad": [110.00, 164.81, 196.00, 261.63, 329.63, 493.88],
            "arp": [220.00, 261.63, 329.63, 392.00, 493.88, 659.25],
        },
        # Fmaj7
        {
            "bass": 43.65,
            "pad": [87.31, 130.81, 174.61, 220.00, 261.63, 329.63],
            "arp": [174.61, 220.00, 261.63, 329.63, 392.00, 523.25],
        },
        # G6
        {
            "bass": 49.00,
            "pad": [98.00, 146.83, 196.00, 246.94, 329.63, 440.00],
            "arp": [196.00, 246.94, 293.66, 329.63, 440.00, 587.33],
        },
    ]

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        bar_pos = (t / 4.0) % 4.0
        c_idx = int(bar_pos)
        c_next = (c_idx + 1) % 4
        blend = bar_pos - c_idx

        # Hòa âm cosine mượt mà chuyển giữa 2 hợp âm
        w1 = 0.5 + 0.5 * math.cos(blend * math.pi)
        w2 = 1.0 - w1

        # 1. Âm trầm Bass nền ấm (Sub & Warm 2nd harmonic)
        b_freq = chord_data[c_idx]["bass"] * w1 + chord_data[c_next]["bass"] * w2
        bass = (
            math.sin(2.0 * math.pi * b_freq * t) * 0.35 +
            math.sin(4.0 * math.pi * b_freq * t) * 0.15 +
            math.sin(6.0 * math.pi * b_freq * t) * 0.05
        )

        # 2. Dàn bè Pad Analog Stereo Chorus
        pad_l = 0.0
        pad_r = 0.0
        for f in chord_data[c_idx]["pad"]:
            p_l = math.sin(2.0 * math.pi * f * 0.9975 * t) + 0.3 * math.sin(4.0 * math.pi * f * 0.9975 * t)
            p_r = math.sin(2.0 * math.pi * f * 1.0025 * t) + 0.3 * math.sin(4.0 * math.pi * f * 1.0025 * t)
            pad_l += p_l * 0.07 * w1
            pad_r += p_r * 0.07 * w1
        for f in chord_data[c_next]["pad"]:
            p_l = math.sin(2.0 * math.pi * f * 0.9975 * t) + 0.3 * math.sin(4.0 * math.pi * f * 0.9975 * t)
            p_r = math.sin(2.0 * math.pi * f * 1.0025 * t) + 0.3 * math.sin(4.0 * math.pi * f * 1.0025 * t)
            pad_l += p_l * 0.07 * w2
            pad_r += p_r * 0.07 * w2

        # 3. Arpeggio chuông sao lung linh (Cosmic Crystal Bell)
        step = int(t * 2.5)  # 2.5 nốt mỗi giây
        step_t = (t * 2.5) - step
        arp_notes = chord_data[c_idx]["arp"]
        arp_freq = arp_notes[step % len(arp_notes)]
        bell_env = math.exp(-step_t * 4.0) * (1.0 - math.exp(-step_t * 50.0))
        b_phase = 2.0 * math.pi * arp_freq * t
        bell = (
            math.sin(b_phase) +
            0.35 * math.sin(b_phase * 2.0) +
            0.18 * math.sin(b_phase * 3.01)
        ) * bell_env * 0.28

        # Hiệu ứng Panning không gian chậm
        pan = 0.5 + 0.28 * math.sin(2.0 * math.pi * 0.2 * t)

        left = bass * 0.45 + pad_l + bell * pan
        right = bass * 0.45 + pad_r + bell * (1.0 - pan)
        raw_samples.append((left, right))

    # Chuẩn hóa âm lượng (Volume Normalization) đạt chuẩn Peak 0.85
    peak = max(max(abs(l), abs(r)) for l, r in raw_samples)
    norm_factor = 0.85 / max(0.001, peak)
    samples = [(clamp(l * norm_factor), clamp(r * norm_factor)) for l, r in raw_samples]

    write_wav(filepath, samples, SAMPLE_RATE, channels=2)


def gen_ui_nav(filepath):
    """Tiếng blip/tick ngắn, nhẹ và thanh (~0.05s) khi chuyển phím hoặc hover."""
    duration = 0.05
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Tần số quét nhanh 680Hz -> 920Hz
        freq = 680.0 + (920.0 - 680.0) * (t / duration)
        env = math.exp(-t * 95.0)
        s = math.sin(2.0 * math.pi * freq * t) * env * 0.45
        samples.append(s)
    write_wav(filepath, samples)


def gen_ui_select(filepath):
    """Tiếng chime xác nhận hai nốt đi lên (~0.12s) khi nhấn Enter/Click."""
    duration = 0.12
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Nốt 1 (0..0.045s): 587.33Hz (D5)
        # Nốt 2 (0.045..0.12s): 880.00Hz (A5)
        if t < 0.045:
            f = 587.33
            env = math.exp(-t * 40.0)
        else:
            t2 = t - 0.045
            f = 880.00
            env = math.exp(-t2 * 32.0)
        tone = math.sin(2.0 * math.pi * f * t) + 0.25 * math.sin(2.0 * math.pi * f * 2.0 * t)
        s = tone * env * 0.55
        samples.append(s)
    write_wav(filepath, samples)


def gen_ui_back(filepath):
    """Tiếng chime trầm đi xuống (~0.10s) khi nhấn ESC hoặc Quay lại."""
    duration = 0.10
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Quét tần số hạ dần 520Hz -> 310Hz
        freq = 520.0 - (520.0 - 310.0) * (t / duration)
        env = math.exp(-t * 35.0)
        tone = math.sin(2.0 * math.pi * freq * t) + 0.2 * math.sin(2.0 * math.pi * freq * 1.5 * t)
        s = tone * env * 0.50
        samples.append(s)
    write_wav(filepath, samples)


def gen_block_roll(filepath):
    """Tiếng lăn và tiếp đất trầm ấm, chắc chắn (~0.11s)."""
    duration = 0.11
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Sóng hạ âm trầm 95Hz -> 48Hz
        freq = 95.0 - (95.0 - 48.0) * math.pow(t / duration, 0.8)
        env_body = math.exp(-t * 26.0)
        body = math.sin(2.0 * math.pi * freq * t) + 0.35 * math.sin(2.0 * math.pi * freq * 2.0 * t)

        # Tiếng chạm nhẹ của cạnh đá ở đầu bước lăn
        tap_env = math.exp(-t * 180.0)
        tap = (random.random() * 2.0 - 1.0) * 0.15 * tap_env

        s = (body * env_body * 0.75 + tap) * 0.85
        samples.append(s)
    write_wav(filepath, samples)


def gen_fragile_warn(filepath):
    """Tiếng răng rắc cảnh báo (~0.15s) khi nằm trên sàn cam."""
    duration = 0.15
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    # Các xung micro-click bất quy tắc
    clicks = [0.015, 0.042, 0.078, 0.105, 0.128]
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        val = 0.0
        # Rung nền tần số thấp thể hiện áp lực sàn
        rumble = math.sin(2.0 * math.pi * 140.0 * t + math.sin(t * 80.0)) * math.exp(-t * 14.0) * 0.35
        val += rumble

        # Tiếng nứt gãy
        for c_t in clicks:
            if t >= c_t:
                dt = t - c_t
                if dt < 0.012:
                    click_freq = 1600.0 + (c_t * 5000.0) % 800.0
                    click_env = math.exp(-dt * 380.0)
                    val += math.sin(2.0 * math.pi * click_freq * dt) * click_env * 0.45

        samples.append(val * 0.8)
    write_wav(filepath, samples)


def gen_switch_soft(filepath):
    """Tiếng kích hoạt công tắc tròn mềm và mở cầu (~0.22s)."""
    duration = 0.22
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Quét nốt điện tử thanh thoát: 380Hz -> 760Hz
        freq = 380.0 + (760.0 - 380.0) * math.pow(t / duration, 0.6)
        env = math.exp(-t * 16.0) * math.sin(clamp(t / 0.02) * (math.pi / 2.0))
        # Họa âm chuông thanh khiết
        tone = math.sin(2.0 * math.pi * freq * t) + 0.4 * math.sin(2.0 * math.pi * freq * 2.0 * t)
        # Tiếng shimmer ngân nhẹ
        shimmer = math.sin(2.0 * math.pi * 1520.0 * t) * math.exp(-t * 22.0) * 0.2
        samples.append((tone * env * 0.65 + shimmer) * 0.8)
    write_wav(filepath, samples)


def gen_switch_heavy(filepath):
    """Tiếng kích hoạt công tắc chữ X nặng (~0.28s) - cơ khí trầm chắc."""
    duration = 0.28
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Cú nện cơ khí ban đầu (65Hz punch)
        punch_env = math.exp(-t * 22.0)
        punch = math.sin(2.0 * math.pi * 65.0 * t) * punch_env * 0.75

        # Âm cơ cấu cơ khí kim loại (metallic ring)
        metal_env = math.exp(-t * 18.0)
        metal = (math.sin(2.0 * math.pi * 420.0 * t) + 0.5 * math.sin(2.0 * math.pi * 840.0 * t)) * metal_env * 0.35

        # Âm giải phóng năng lượng mở cầu (laser/energy sweep)
        energy_env = math.sin(clamp(t / duration) * math.pi) * 0.3
        energy = math.sin(2.0 * math.pi * (260.0 + 380.0 * t) * t) * energy_env

        samples.append((punch + metal + energy) * 0.85)
    write_wav(filepath, samples)


def gen_switch_deny(filepath):
    """Tiếng buzz trầm ngắn (~0.12s) khi đè lên công tắc X mà không đủ lực."""
    duration = 0.12
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Hai tần số lệch pha tạo âm rè (115Hz & 123Hz)
        tone1 = math.sin(2.0 * math.pi * 115.0 * t)
        tone2 = math.sin(2.0 * math.pi * 123.0 * t)
        env = math.exp(-t * 28.0)
        # Sóng vuông nhẹ tạo âm buzz
        buzz = math.copysign(1.0, tone1 + tone2 * 0.8) * 0.5 + (tone1 + tone2) * 0.25
        samples.append(buzz * env * 0.65)
    write_wav(filepath, samples)


def gen_block_split(filepath):
    """Hiệu ứng phân thân lượng tử (~0.30s) khi tách thành 2 khối."""
    duration = 0.30
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        p = t / duration
        # Quét tần số tách đôi: một nhánh quét lên (400 -> 1200), một nhánh quét xuống (400 -> 200)
        f_up = 400.0 + 800.0 * (p * p)
        f_down = 400.0 - 200.0 * p
        env = math.sin(p * math.pi)
        tone_up = math.sin(2.0 * math.pi * f_up * t)
        tone_down = math.sin(2.0 * math.pi * f_down * t)
        sparkle = math.sin(2.0 * math.pi * 1800.0 * t) * math.exp(-t * 15.0) * 0.25
        s = (tone_up * 0.5 + tone_down * 0.35 + sparkle) * env * 0.75
        samples.append(s)
    write_wav(filepath, samples)


def gen_block_swap(filepath):
    """Tiếng ping cao độ rõ ràng (~0.08s) khi đổi quyền điều khiển khối nhỏ."""
    duration = 0.08
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Nốt C6 tinh tế (1046.5Hz)
        freq = 1046.5
        env = math.exp(-t * 60.0)
        tone = math.sin(2.0 * math.pi * freq * t) + 0.3 * math.sin(2.0 * math.pi * freq * 2.0 * t)
        samples.append(tone * env * 0.65)
    write_wav(filepath, samples)


def gen_block_merge(filepath):
    """Hợp âm hội tụ năng lượng (~0.32s) khi 2 khối nhỏ gộp lại."""
    duration = 0.32
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        p = t / duration
        # Hai nốt hội tụ về 523.25Hz (C5), sau đó ngân vang hợp âm C-E-G
        f1 = 280.0 + (523.25 - 280.0) * math.pow(p, 0.7)
        f2 = 780.0 - (780.0 - 523.25) * math.pow(p, 0.7)
        env = math.sin(clamp(p * 2.0, 0.0, 1.0) * math.pi / 2.0) * math.exp(-max(0.0, p - 0.4) * 5.0)

        tone = math.sin(2.0 * math.pi * f1 * t) * 0.45 + math.sin(2.0 * math.pi * f2 * t) * 0.45
        # Hòa âm ấm
        harmony = math.sin(2.0 * math.pi * 659.25 * t) * 0.25 + math.sin(2.0 * math.pi * 783.99 * t) * 0.25
        samples.append((tone + harmony) * env * 0.7)
    write_wav(filepath, samples)


def gen_undo(filepath):
    """Hiệu ứng tua ngược ngắn (~0.10s) khi nhấn Z hoàn tác."""
    duration = 0.10
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        p = t / duration
        # Quét tần số tăng nhanh (ngược với rơi)
        freq = 180.0 + 520.0 * (p * p)
        env = math.sin(p * math.pi)
        tone = math.sin(2.0 * math.pi * freq * t)
        samples.append(tone * env * 0.6)
    write_wav(filepath, samples)


def gen_reset(filepath):
    """Hiệu ứng khởi tạo lại màn chơi (~0.15s) khi nhấn R."""
    duration = 0.15
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        p = t / duration
        # Quét lượn sóng 420Hz -> 210Hz -> 420Hz
        freq = 315.0 + 105.0 * math.cos(p * 2.0 * math.pi)
        env = math.sin(p * math.pi)
        tone = math.sin(2.0 * math.pi * freq * t) + 0.2 * math.sin(2.0 * math.pi * freq * 2.0 * t)
        samples.append(tone * env * 0.6)
    write_wav(filepath, samples)


def gen_level_win(filepath):
    """Giai điệu Chiến thắng tươi sáng, ngân vang (~0.75s)."""
    duration = 0.75
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    # Chuỗi nốt Arpeggio: C5 (523.25) -> E5 (659.25) -> G5 (783.99) -> C6 (1046.50)
    notes = [
        (0.00, 523.25),
        (0.12, 659.25),
        (0.24, 783.99),
        (0.36, 1046.50),
    ]

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        val = 0.0
        for start_t, freq in notes:
            if t >= start_t:
                dt = t - start_t
                env = math.exp(-dt * 4.5) * math.sin(clamp(dt / 0.015) * (math.pi / 2.0))
                tone = math.sin(2.0 * math.pi * freq * dt) + 0.35 * math.sin(2.0 * math.pi * freq * 2.0 * dt)
                # Ngân vang shimmer
                shimmer = math.sin(2.0 * math.pi * freq * 3.0 * dt) * 0.1
                val += (tone + shimmer) * env * 0.35

        samples.append(clamp(val * 0.85))
    write_wav(filepath, samples)


def gen_lose_fall(filepath):
    """Hiệu ứng trượt rơi xuống vực thẳm (~0.50s)."""
    duration = 0.50
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        p = t / duration
        # Tần số rơi nhanh từ 380Hz xuống 42Hz
        freq = 380.0 * math.pow(0.12, p)
        env = math.pow(1.0 - p, 1.4)
        tone = math.sin(2.0 * math.pi * freq * t) + 0.3 * math.sin(2.0 * math.pi * freq * 0.5 * t)
        # Tiếng gió rít khi rơi
        wind = (random.random() * 2.0 - 1.0) * 0.15 * math.sin(p * math.pi)
        samples.append((tone * 0.75 + wind) * env * 0.8)
    write_wav(filepath, samples)


def gen_lose_break(filepath):
    """Tiếng vỡ sàn cam nham thạch giòn tan kèm tiếng rơi xuống vực (~0.55s)."""
    duration = 0.55
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        val = 0.0

        # Cú va chạm và vỡ vụn ban đầu (0..0.15s)
        if t < 0.18:
            crack_env = math.exp(-t * 28.0)
            # Tiếng gãy đá giòn
            crack = (
                math.sin(2.0 * math.pi * 920.0 * t) * 0.4 +
                math.sin(2.0 * math.pi * 1480.0 * t) * 0.3 +
                (random.random() * 2.0 - 1.0) * 0.45
            ) * crack_env
            val += crack

        # Tiếng rơi xuống vực thẳm theo sau
        if t >= 0.06:
            t_fall = t - 0.06
            p_fall = t_fall / (duration - 0.06)
            freq = 320.0 * math.pow(0.15, p_fall)
            fall_env = math.pow(1.0 - p_fall, 1.6) * 0.65
            tone = math.sin(2.0 * math.pi * freq * t_fall)
            val += tone * fall_env

        samples.append(clamp(val * 0.85))
    write_wav(filepath, samples)


SYNTH_GENERATORS = {
    "bgm_ambient.wav": gen_bgm_ambient,
    "ui_nav.wav": gen_ui_nav,
    "ui_select.wav": gen_ui_select,
    "ui_back.wav": gen_ui_back,
    "block_roll.wav": gen_block_roll,
    "fragile_warn.wav": gen_fragile_warn,
    "switch_soft.wav": gen_switch_soft,
    "switch_heavy.wav": gen_switch_heavy,
    "switch_deny.wav": gen_switch_deny,
    "block_split.wav": gen_block_split,
    "block_swap.wav": gen_block_swap,
    "block_merge.wav": gen_block_merge,
    "undo.wav": gen_undo,
    "reset.wav": gen_reset,
    "level_win.wav": gen_level_win,
    "lose_fall.wav": gen_lose_fall,
    "lose_break.wav": gen_lose_break,
}


def ensure_sound_assets(sounds_dir="assets/sounds"):
    """Tự động kiểm tra và sinh các tệp âm thanh nếu chưa tồn tại."""
    os.makedirs(sounds_dir, exist_ok=True)
    generated_count = 0
    for filename, generator in SYNTH_GENERATORS.items():
        filepath = os.path.join(sounds_dir, filename)
        if not os.path.exists(filepath):
            print(f"[AudioSynth] Generating procedural audio: {filename}...")
            generator(filepath)
            generated_count += 1
    if generated_count > 0:
        print(f"[AudioSynth] Successfully initialized {generated_count} WAV audio files.")
