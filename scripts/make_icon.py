"""Render images/icon.png: two tilted sandstone monoliths with syntax-colored sound waves on night-sky ink.

Pure stdlib. Each shape is a signed distance field; coverage = clamp(0.5 - d)
gives one-pixel anti-aliasing without supersampling.

    python3 scripts/make_icon.py
"""
import math
import struct
import zlib
from pathlib import Path

SIZE = 256
OUT = Path(__file__).resolve().parent.parent / "images" / "icon.png"


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


BG_TOP, BG_BOTTOM = hexrgb("#1f2130"), hexrgb("#101118")
SIENNA, CRIMSON, BRONZE = hexrgb("#a0522d"), hexrgb("#990000"), hexrgb("#c77926")
CHARCOAL, BONE, SANDSTONE = hexrgb("#3a3b3c"), hexrgb("#cac1b2"), hexrgb("#c9a371")
WAVES = [("#cc6550", 26), ("#909465", 42), ("#7395ab", 58)]  # rust, sagebrush, big sky
STAGE = (128, 210)
STARS = [(46, 46, 1.6), (84, 30, 1.2), (122, 56, 1.4), (150, 30, 1.0), (106, 84, 1.0), (60, 76, 1.0), (214, 112, 1.2)]

# Ship Rock (left) and Creation Rock (right): slabs leaning away from the stage
LEFT = [(6, 256), (16, 128), (34, 76), (50, 64), (72, 104), (100, 256)]
RIGHT = [(156, 256), (176, 132), (204, 92), (220, 90), (238, 128), (252, 256)]


def clamp(v):
    return 0.0 if v < 0 else 1.0 if v > 1 else v


def cov(d):
    return clamp(0.5 - d)


def sd_round_rect(x, y, x0, y0, x1, y1, r):
    cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - r, (y1 - y0) / 2 - r
    qx, qy = abs(x - cx) - hw, abs(y - cy) - hh
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - r


def sd_polygon(x, y, pts):
    d = (x - pts[0][0]) ** 2 + (y - pts[0][1]) ** 2
    s = 1
    j = len(pts) - 1
    for i in range(len(pts)):
        (ax, ay), (bx, by) = pts[i], pts[j]
        ex, ey, wx, wy = bx - ax, by - ay, x - ax, y - ay
        t = clamp((wx * ex + wy * ey) / (ex * ex + ey * ey))
        d = min(d, (wx - ex * t) ** 2 + (wy - ey * t) ** 2)
        c = (y >= ay, y < by, ex * wy > ey * wx)
        if all(c) or not any(c):
            s = -s
        j = i
    return s * math.sqrt(d)


def over(dst, color, a):
    return tuple(d * (1 - a) + c * a for d, c in zip(dst, color))


def rock(c, x, y, pts, lit, shade, tilt):
    """Fill a slab with tilted strata, lit on one face and shaded toward the other."""
    a = cov(sd_polygon(x, y, pts) - 3)
    if a == 0:
        return c
    xs = [p[0] for p in pts]
    u = (x - min(xs)) / (max(xs) - min(xs))
    body = over(lit, shade, clamp(u if tilt < 0 else 1 - u) * 0.75)
    band = 0.5 + 0.5 * math.sin((x * math.sin(tilt) + y * math.cos(tilt)) / 5.5)
    body = over(body, (0, 0, 0), 0.16 * band * band)
    return over(c, body, a)


def pixel(x, y):
    tile = cov(sd_round_rect(x, y, 0, 0, SIZE, SIZE, 56))
    if tile == 0:
        return (0, 0, 0, 0)
    c = over(BG_TOP, BG_BOTTOM, y / SIZE)

    # Stars and a crescent moon
    for sx, sy, r in STARS:
        c = over(c, BONE, 0.85 * cov(math.hypot(x - sx, y - sy) - r))
    moon = max(math.hypot(x - 196, y - 56) - 17, -(math.hypot(x - 205, y - 50) - 15))
    c = over(c, SANDSTONE, cov(moon))

    c = rock(c, x, y, LEFT, BRONZE, SIENNA, -0.5)
    c = rock(c, x, y, RIGHT, SIENNA, CRIMSON, 0.55)

    # Sound waves: arcs rising from the stage, fading toward their ends
    dx, dy = x - STAGE[0], y - STAGE[1]
    ang = math.atan2(dx, -dy)
    if dy < 4 and abs(ang) < 0.85:
        fade = 1 - (abs(ang) / 0.85) ** 3
        for color, r in WAVES:
            d = abs(math.hypot(dx, dy) - r) - 2.6
            c = over(c, hexrgb(color), cov(d) * fade)

    # Amphitheater seating: a charcoal bowl with faint row lines
    bowl = (y - 218) + 0.0012 * (x - 128) ** 2
    if bowl > -1:
        c = over(c, CHARCOAL, cov(-bowl))
        row = abs(((bowl - 9) % 10) - 5) - 0.6
        c = over(c, BG_BOTTOM, 0.3 * cov(row) * clamp(bowl / 6))
    c = over(c, BRONZE, cov(math.hypot((x - STAGE[0]) / 3, y - 216) - 2.4))

    return (*c, tile)


def write_png(path, rows):
    raw = b"".join(b"\x00" + bytes(round(v * 255) for px in row for v in px) for row in rows)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"
                     + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw, 9))
                     + chunk(b"IEND", b""))


if __name__ == "__main__":
    write_png(OUT, [[pixel(x + 0.5, y + 0.5) for x in range(SIZE)] for y in range(SIZE)])
    print(OUT)
