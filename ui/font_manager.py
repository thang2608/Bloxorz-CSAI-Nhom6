# ui/font_manager.py — Quản lý phông chữ vector độ nét cao hỗ trợ tiếng Việt có dấu
import os
try:
    import pyray as rl
except ImportError:
    from raylib import pyray as rl

from config import VIETNAMESE_CODEPOINTS

ui_font_bold = None
ui_font_regular = None

def init_fonts():
    """Nạp phông chữ vector độ nét cao hỗ trợ 100% Tiếng Việt có dấu, triệt tiêu lỗi dấu hỏi chấm"""
    global ui_font_bold, ui_font_regular

    font_bold_candidates = [
        # Đường dẫn trên Windows
        b"C:/Windows/Fonts/arialbd.ttf",
        b"C:/Windows/Fonts/segoeuib.ttf",
        # Đường dẫn trên macOS
        b"/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        b"/System/Library/Fonts/Supplemental/Trebuchet MS Bold.ttf",
    ]
    font_reg_candidates = [
        # Đường dẫn trên Windows
        b"C:/Windows/Fonts/arial.ttf",
        b"C:/Windows/Fonts/segoeui.ttf",
        # Đường dẫn trên macOS
        b"/System/Library/Fonts/Supplemental/Arial.ttf",
        b"/System/Library/Fonts/Supplemental/Trebuchet MS.ttf",
    ]

    try:
        from raylib import _raylib_cffi
        ffi = _raylib_cffi.ffi
        lib = _raylib_cffi.lib
        c_arr = ffi.new("int[]", VIETNAMESE_CODEPOINTS)
        num_cp = len(VIETNAMESE_CODEPOINTS)

        for p in font_bold_candidates:
            if os.path.exists(p.decode("utf-8")):
                try:
                    ui_font_bold = lib.LoadFontEx(p, 56, c_arr, num_cp)
                    rl.set_texture_filter(ui_font_bold.texture, rl.TEXTURE_FILTER_BILINEAR)
                    break
                except Exception:
                    pass

        for p in font_reg_candidates:
            if os.path.exists(p.decode("utf-8")):
                try:
                    ui_font_regular = lib.LoadFontEx(p, 40, c_arr, num_cp)
                    rl.set_texture_filter(ui_font_regular.texture, rl.TEXTURE_FILTER_BILINEAR)
                    break
                except Exception:
                    pass
    except Exception:
        pass


def measure_text_ui(text, font_size, is_bold=False):
    """Đo chiều rộng text chính xác theo font TTF hoặc font mặc định"""
    font = ui_font_bold if (is_bold and ui_font_bold) else (ui_font_regular or ui_font_bold)
    if font is not None and hasattr(rl, "measure_text_ex"):
        try:
            vec = rl.measure_text_ex(font, str(text), float(font_size), 1.0)
            return int(vec.x)
        except Exception:
            pass
    return rl.measure_text(str(text), int(font_size))


def draw_text_ui(text, x, y, font_size, color, is_bold=False, shadow=False, shadow_color=None, glow=False, glow_color=None):
    """Vẽ chữ chất lượng cao Anti-Aliased kèm hiệu ứng đổ bóng 3D & phát quang Neon"""
    font = ui_font_bold if (is_bold and ui_font_bold) else (ui_font_regular or ui_font_bold)
    s_text = str(text)

    # 1. Hào quang Neon (Glow Aura)
    if glow:
        cr = getattr(color, 'r', color[0] if isinstance(color, (list, tuple)) else 255)
        cg = getattr(color, 'g', color[1] if isinstance(color, (list, tuple)) else 255)
        cb = getattr(color, 'b', color[2] if isinstance(color, (list, tuple)) else 255)
        g_col = glow_color if glow_color is not None else rl.Color(cr, cg, cb, 35)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            if font is not None and hasattr(rl, "draw_text_ex"):
                try:
                    rl.draw_text_ex(font, s_text, rl.Vector2(float(x + dx), float(y + dy)), float(font_size), 1.0, g_col)
                    continue
                except Exception:
                    pass
            rl.draw_text(s_text, int(x + dx), int(y + dy), int(font_size), g_col)

    # 2. Đổ bóng chiều sâu 3D (Drop Shadow)
    if shadow:
        sh_col = shadow_color if shadow_color is not None else rl.Color(0, 0, 0, 160)
        sh_offset = 2 if font_size >= 24 else 1
        if font is not None and hasattr(rl, "draw_text_ex"):
            try:
                rl.draw_text_ex(font, s_text, rl.Vector2(float(x + sh_offset), float(y + sh_offset)), float(font_size), 1.0, sh_col)
            except Exception:
                rl.draw_text(s_text, int(x + sh_offset), int(y + sh_offset), int(font_size), sh_col)
        else:
            rl.draw_text(s_text, int(x + sh_offset), int(y + sh_offset), int(font_size), sh_col)

    # 3. Lớp chữ chính siêu nét
    if font is not None and hasattr(rl, "draw_text_ex"):
        try:
            rl.draw_text_ex(font, s_text, rl.Vector2(float(x), float(y)), float(font_size), 1.0, color)
            return
        except Exception:
            pass
    rl.draw_text(s_text, int(x), int(y), int(font_size), color)
