"""Generate the PWA icons into public/icons. Requires Pillow.

Run from the project root:  python scripts/make_icons.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "public" / "icons"
TOP, BOTTOM = (15, 118, 110), (29, 78, 216)


def gear(draw, cx, cy, r, teeth, color):
    pts = []
    for i in range(teeth * 4):
        ang = 2 * math.pi * i / (teeth * 4)
        rad = r if i % 4 in (0, 1) else r * 0.78
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=color)


def icon(size, scale, rounded):
    """scale: fraction of the canvas the artwork occupies (smaller for maskable icons)."""
    s = size * 4  # supersample, then shrink for smooth edges
    img = Image.new("RGBA", (s, s))
    px = img.load()
    for y in range(s):
        k = y / (s - 1)
        row = tuple(round(a + (b - a) * k) for a, b in zip(TOP, BOTTOM)) + (255,)
        for x in range(s):
            px[x, y] = row
    d = ImageDraw.Draw(img)
    cx = cy = s / 2
    r = s * 0.34 * scale
    gear(d, cx, cy, r, 10, (255, 255, 255, 255))
    d.ellipse([cx - r * 0.42, cy - r * 0.42, cx + r * 0.42, cy + r * 0.42], fill=TOP + (255,))
    # a two-link arm across the gear
    w = round(r * 0.13)
    a, b, c = (cx - r * 0.95, cy + r * 0.95), (cx - r * 0.05, cy - r * 0.15), (cx + r * 0.95, cy - r * 0.9)
    d.line([a, b, c], fill=(251, 191, 36, 255), width=w, joint="curve")
    for p in (a, b, c):
        d.ellipse([p[0] - w, p[1] - w, p[0] + w, p[1] + w], fill=(255, 255, 255, 255), outline=(251, 191, 36, 255), width=round(w * 0.5))
    if rounded:
        mask = Image.new("L", (s, s), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=round(s * 0.22), fill=255)
        img.putalpha(mask)
    return img.resize((size, size), Image.LANCZOS)


OUT.mkdir(parents=True, exist_ok=True)
icon(192, 1.0, True).save(OUT / "icon-192.png")
icon(512, 1.0, True).save(OUT / "icon-512.png")
icon(512, 0.72, False).save(OUT / "icon-maskable-512.png")
print("icons written to", OUT)
