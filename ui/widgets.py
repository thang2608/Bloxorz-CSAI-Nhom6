# ui/widgets.py — Các thành phần UI có thể tái sử dụng (Button, Keycap, Vignette, Circle)
try:
    import pyray as rl
except ImportError:
    from raylib import pyray as rl

from ui.font_manager import draw_text_ui, measure_text_ui

def check_button(rec):
    """Kiểm tra chuột có đang hover hoặc click vào nút không"""
    mp = rl.get_mouse_position()
    hover = rl.check_collision_point_rec(mp, rec)
    clicked = hover and rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT)
    return hover, clicked


def draw_styled_button(rec, text, font_size=18, is_hover=False, active=False, accent_col=None):
    """Vẽ nút bấm bo góc sang trọng có hiệu ứng hover phát quang & đổ bóng chữ"""
    if accent_col is None:
        accent_col = rl.Color(0, 240, 245, 255)

    ar = getattr(accent_col, 'r', accent_col[0] if isinstance(accent_col, (list, tuple)) else 0)
    ag = getattr(accent_col, 'g', accent_col[1] if isinstance(accent_col, (list, tuple)) else 240)
    ab = getattr(accent_col, 'b', accent_col[2] if isinstance(accent_col, (list, tuple)) else 245)

    if active:
        bg = rl.Color(28, 70, 88, 245)
        border = accent_col
        text_col = rl.Color(255, 255, 255, 255)
    elif is_hover:
        bg = rl.Color(34, 62, 80, 245)
        border = accent_col
        text_col = accent_col
        # Hào quang viền ngoài khi hover
        glow_rec = rl.Rectangle(rec.x - 3, rec.y - 3, rec.width + 6, rec.height + 6)
        rl.draw_rectangle_rounded(glow_rec, 0.28, 8, rl.Color(ar, ag, ab, 35))
    else:
        bg = rl.Color(16, 32, 44, 215)
        border = rl.Color(65, 90, 110, 180)
        text_col = rl.Color(215, 235, 245, 255)

    rl.draw_rectangle_rounded(rec, 0.28, 8, bg)
    rl.draw_rectangle_rounded_lines(rec, 0.28, 8, border)

    # Vệt phản chiếu ánh sáng thủy tinh (Glass Reflection Highlight)
    top_highlight = rl.Rectangle(rec.x + 2, rec.y + 2, rec.width - 4, rec.height * 0.40)
    rl.draw_rectangle_rounded(top_highlight, 0.28, 8, rl.Color(255, 255, 255, 12))

    tw = measure_text_ui(text, font_size, is_bold=True)
    tx = int(rec.x + rec.width / 2 - tw / 2)
    ty = int(rec.y + rec.height / 2 - font_size / 2)
    draw_text_ui(text, tx, ty, font_size, text_col, is_bold=True, shadow=True, glow=is_hover, glow_color=rl.Color(ar, ag, ab, 50))


def draw_keycap(x, y, w_key, h_key, label, font_size=14):
    """Vẽ một nút keycap bo góc hiện đại"""
    shadow_rec = rl.Rectangle(x + 1, y + 2, w_key, h_key)
    rl.draw_rectangle_rounded(shadow_rec, 0.32, 6, rl.Color(0, 0, 0, 100))
    rec = rl.Rectangle(x, y, w_key, h_key)
    rl.draw_rectangle_rounded(rec, 0.32, 6, rl.Color(38, 55, 70, 245))
    rl.draw_rectangle_rounded_lines(rec, 0.32, 6, rl.Color(100, 135, 160, 200))
    hl = rl.Rectangle(x + 2, y + 2, w_key - 4, h_key * 0.4)
    rl.draw_rectangle_rounded(hl, 0.32, 6, rl.Color(255, 255, 255, 18))
    tw = measure_text_ui(label, font_size, is_bold=True)
    tx = int(x + w_key / 2 - tw / 2)
    ty = int(y + h_key / 2 - font_size / 2)
    draw_text_ui(label, tx, ty, font_size, rl.Color(230, 245, 255, 255), is_bold=True)


def draw_star_circle(x, y, radius, col):
    """Vẽ vòng tròn phát quang hào quang sao an toàn tương thích mọi môi trường"""
    if hasattr(rl, "draw_circle"):
        try:
            rl.draw_circle(int(x), int(y), float(radius), col)
        except TypeError:
            try:
                rl.draw_circle(rl.Vector2(float(x), float(y)), float(radius), col)
            except Exception:
                pass
        except Exception:
            pass


def draw_cinematic_vignette(w, h):
    """Vẽ viền tối điện ảnh (Screen-Space Vignette) tạo chiều sâu tập trung"""
    if hasattr(rl, "draw_rectangle_gradient_v") and hasattr(rl, "draw_rectangle_gradient_h"):
        v_size = 96
        rl.draw_rectangle_gradient_v(0, 0, w, v_size, rl.Color(0, 0, 0, 130), rl.Color(0, 0, 0, 0))
        rl.draw_rectangle_gradient_v(0, h - v_size, w, v_size, rl.Color(0, 0, 0, 0), rl.Color(0, 0, 0, 150))
        rl.draw_rectangle_gradient_h(0, 0, v_size, h, rl.Color(0, 0, 0, 130), rl.Color(0, 0, 0, 0))
        rl.draw_rectangle_gradient_h(w - v_size, 0, v_size, h, rl.Color(0, 0, 0, 0), rl.Color(0, 0, 0, 130))
