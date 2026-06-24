#!/usr/bin/env python3
"""Generate Band Training icon and store image assets.

Screenshots are captured from the live app separately so they match the
current HTML/CSS instead of a static mockup.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]

BG = (12, 14, 13, 255)
PANEL = (21, 25, 23, 255)
PANEL2 = (28, 33, 30, 255)
LINE = (42, 48, 44, 255)
INK = (242, 245, 241, 255)
MUTED = (139, 147, 140, 255)
LIME = (196, 255, 31, 255)
CYAN = (76, 196, 255, 255)
AMBER = (255, 210, 63, 255)
def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def supersample(size: tuple[int, int], factor: int = 3) -> tuple[Image.Image, ImageDraw.ImageDraw, int]:
    w, h = size
    img = Image.new("RGBA", (w * factor, h * factor), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), factor


def down(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    return img.resize(size, Image.Resampling.LANCZOS)


def rr(draw: ImageDraw.ImageDraw, box, r, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def gradient(size: tuple[int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", size, BG)
    px = img.load()
    for y in range(h):
        for x in range(w):
            gx = x / max(1, w - 1)
            gy = y / max(1, h - 1)
            glow = max(0, 1 - math.hypot(gx - 0.42, gy - 0.2) * 1.65)
            r = int(12 + 19 * glow + 7 * gy)
            g = int(14 + 31 * glow + 9 * gy)
            b = int(13 + 17 * glow + 8 * gy)
            px[x, y] = (r, g, b, 255)
    return img


def draw_band_mark(draw: ImageDraw.ImageDraw, box, stroke, scale=1, play=True):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    path = [
        (x0 + 0.23 * w, y0 + 0.54 * h),
        (x0 + 0.31 * w, y0 + 0.25 * h),
        (x0 + 0.58 * w, y0 + 0.18 * h),
        (x0 + 0.79 * w, y0 + 0.39 * h),
        (x0 + 0.68 * w, y0 + 0.69 * h),
        (x0 + 0.39 * w, y0 + 0.78 * h),
        (x0 + 0.23 * w, y0 + 0.54 * h),
    ]
    draw.line(path, fill=LIME, width=stroke, joint="curve")
    draw.line([(x0 + 0.18 * w, y0 + 0.67 * h), (x0 + 0.82 * w, y0 + 0.31 * h)], fill=CYAN, width=max(2, stroke // 3))
    joint_r = max(2, stroke // 2)
    for p in (path[0], path[2], path[4]):
        draw.ellipse((p[0] - joint_r, p[1] - joint_r, p[0] + joint_r, p[1] + joint_r), fill=AMBER)
    if play:
        cx, cy = x0 + 0.51 * w, y0 + 0.50 * h
        tri = [
            (cx - 0.07 * w, cy - 0.10 * h),
            (cx - 0.07 * w, cy + 0.10 * h),
            (cx + 0.11 * w, cy),
        ]
        draw.polygon(tri, fill=INK)


def icon(size: int, maskable: bool = False, transparent: bool = False) -> Image.Image:
    img, draw, s = supersample((size, size), 4)
    if not transparent:
        bg = gradient((size * s, size * s))
        img.alpha_composite(bg)
    pad = int(size * (0.18 if maskable else 0.10) * s)
    r = int(size * 0.18 * s)
    rr(draw, (pad, pad, size * s - pad, size * s - pad), r, (18, 22, 19, 245), (57, 67, 58, 255), max(1, size // 52 * s))
    draw_band_mark(draw, (pad + int(size * .08 * s), pad + int(size * .08 * s), size * s - pad - int(size * .08 * s), size * s - pad - int(size * .08 * s)), max(4, int(size * .055 * s)))
    return down(img, (size, size))


def notification(size: int) -> Image.Image:
    img, draw, s = supersample((size, size), 4)
    stroke = max(2, int(size * 0.08 * s))
    pad = int(size * 0.18 * s)
    box = (pad, pad, size * s - pad, size * s - pad)
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    pts = [
        (x0 + .18 * w, y0 + .55 * h), (x0 + .34 * w, y0 + .23 * h),
        (x0 + .66 * w, y0 + .23 * h), (x0 + .82 * w, y0 + .55 * h),
        (x0 + .50 * w, y0 + .79 * h), (x0 + .18 * w, y0 + .55 * h),
    ]
    draw.line(pts, fill=(255, 255, 255, 255), width=stroke, joint="curve")
    cx, cy = x0 + .50 * w, y0 + .50 * h
    draw.polygon([(cx - .05 * w, cy - .09 * h), (cx - .05 * w, cy + .09 * h), (cx + .12 * w, cy)], fill=(255, 255, 255, 255))
    return down(img, (size, size))


def splash(size: int) -> Image.Image:
    img = gradient((size, size))
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    card = (int(size * .17), int(size * .17), int(size * .83), int(size * .83))
    rr(d, card, int(size * .12), (17, 22, 18, 235), (55, 68, 50, 255), max(2, size // 150))
    draw_band_mark(d, (int(size * .27), int(size * .25), int(size * .73), int(size * .71)), max(8, int(size * .035)))
    title = "BAND"
    f = font(max(18, int(size * .075)), True)
    tw = d.textlength(title, font=f)
    d.text(((size - tw) / 2, size * .70), title, font=f, fill=INK)
    img.alpha_composite(overlay)
    return img


def feature_graphic() -> Image.Image:
    w, h = 1024, 500
    img = gradient((w, h))
    d = ImageDraw.Draw(img)
    for i in range(7):
        y = 70 + i * 58
        d.line([(570, y), (965, y + 85)], fill=(196, 255, 31, 34), width=18)
    draw_band_mark(d, (575, 85, 930, 405), 28)
    d.text((58, 78), "Band Training", font=font(64, True), fill=INK)
    d.text((62, 162), "Video-guided resistance work", font=font(30, True), fill=LIME)
    labels = ["Search videos", "Mark done", "Export log"]
    x = 62
    for label in labels:
        tw = d.textlength(label, font=font(22, True))
        rr(d, (x, 246, x + tw + 34, 296), 18, PANEL2, LINE, 2)
        d.text((x + 17, 257), label, font=font(22, True), fill=INK)
        x += int(tw) + 52
    d.text((64, 365), "Built for bands, mobility, speed and stability sessions.", font=font(24), fill=MUTED)
    return img


def save(path: str | Path, img: Image.Image) -> None:
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def main() -> None:
    for rel, size in {
        "icons/icon-192.png": 192,
        "icons/icon-192-maskable.png": 192,
        "icons/icon-512.png": 512,
        "icons/icon-512-maskable.png": 512,
        "store_icon.png": 512,
    }.items():
        save(rel, icon(size, maskable="maskable" in rel))

    for density, size in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
        save(f"app/src/main/res/mipmap-{density}/ic_launcher.png", icon(size))
    for density, size in {"mdpi": 82, "hdpi": 123, "xhdpi": 164, "xxhdpi": 246, "xxxhdpi": 328}.items():
        save(f"app/src/main/res/mipmap-{density}/ic_maskable.png", icon(size, maskable=True))
    for density, size in {"mdpi": 24, "hdpi": 36, "xhdpi": 48, "xxhdpi": 72, "xxxhdpi": 96}.items():
        save(f"app/src/main/res/drawable-{density}/ic_notification_icon.png", notification(size))
    for density, size in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
        save(f"app/src/main/res/drawable-{density}/shortcut_0.png", icon(size))
    for density, size in {"mdpi": 300, "hdpi": 450, "xhdpi": 600, "xxhdpi": 900, "xxxhdpi": 1200}.items():
        save(f"app/src/main/res/drawable-{density}/splash.png", splash(size))

    save("graphics/feature-graphic-1024x500.png", feature_graphic())

if __name__ == "__main__":
    main()
