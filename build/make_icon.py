#!/usr/bin/env python3
"""Generates build/icon.ico (a football + "FM" mark) from scratch with PIL.

Usage:  python build/make_icon.py
Output: build/icon.ico  (multi-size Windows icon)
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "icon.ico")

SIZE = 256


def _font(size):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_football(d, cx, cy, r):
    """Simple stylized football (white panel + dark pentagon + seams)."""
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(245, 245, 250, 255))
    # central pentagon
    pr = r * 0.34
    pent = []
    for i in range(5):
        ang = -90 + i * 72
        import math
        x = cx + pr * math.cos(math.radians(ang))
        y = cy + pr * math.sin(math.radians(ang))
        pent.append((x, y))
    d.polygon(pent, fill=(24, 24, 28, 255), outline=(24, 24, 28, 255))
    # seam lines
    for i in range(5):
        ax, ay = pent[i]
        bx, by = pent[(i + 1) % 5]
        mx, my = (ax + bx) / 2, (ay + by) / 2
        dx, dy = mx - cx, my - cy
        if (dx, dy) == (0, 0):
            continue
        length = (dx * dx + dy * dy) ** 0.5
        ex = mx + dx / length * r
        ey = my + dy / length * r
        d.line((mx, my, ex, ey), fill=(24, 24, 28, 255), width=max(2, int(r * 0.045)))


def _render(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Rounded-square background
    margin = int(size * 0.045)
    radius = int(size * 0.22)
    d.rounded_rectangle((margin, margin, size - margin, size - margin),
                        radius=radius, fill=(18, 18, 20, 255))
    # Accent border
    d.rounded_rectangle((margin, margin, size - margin, size - margin),
                        radius=radius, outline=(108, 92, 231, 255), width=max(2, int(size * 0.02)))

    # Football in upper area
    ball_r = int(size * 0.26)
    _draw_football(d, size * 0.5, size * 0.40, ball_r)

    # "FM" label
    font = _font(int(size * 0.20))
    text = "FM"
    try:
        bbox = d.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (size - tw) / 2 - bbox[0]
        ty = size * 0.70 - bbox[1]
        d.text((tx, ty), text, font=font, fill=(241, 241, 245, 255))
    except Exception:
        pass
    return img


def main():
    base = _render(SIZE)
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base.save(OUT, format="ICO", sizes=sizes)
    print(f"Wrote {OUT} ({len(sizes)} sizes)")


if __name__ == "__main__":
    main()
