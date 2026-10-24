"""Render images/count-arms.gif: a Lucas-angle sunflower lighting up its 47 spiral arms.

Mirrors examples/count_arms.py for the README, where code can't run. Needs Pillow.
Drawn at 2x and scaled down for anti-aliasing.

    python3 scripts/make_count_arms.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "images" / "count-arms.gif"

W, H, HEAD = 360, 400, 340
SS = 2  # supersampling factor
SEEDS = 1700
ARMS = 47
LUCAS_ANGLE = 2 * math.pi / (2 + (1 + math.sqrt(5)) / 2)  # 99.50°

INK, SEED = "#16171f", "#3a3b3c"
RUST, SANDSTONE, SHALE = "#cc6550", "#c9a371", "#7d746d"


def font(size):
    for path in ("/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default(size)


def arm_rank():
    # Arm r starts at seed r. Neighboring arms differ by another Lucas number,
    # so rank them by starting angle to light them up side by side.
    by_angle = sorted(range(ARMS), key=lambda r: (r * LUCAS_ANGLE) % (2 * math.pi))
    rank = [0] * ARMS
    for i, r in enumerate(by_angle):
        rank[r] = i
    return rank


def frame(shown, rank, label_font):
    img = Image.new("RGB", (W * SS, H * SS), INK)
    draw = ImageDraw.Draw(img)
    mid = W * SS / 2
    c = (HEAD * SS / 2 * 0.95) / math.sqrt(SEEDS)
    for n in range(1, SEEDS + 1):
        r = c * math.sqrt(n)
        x = mid + r * math.cos(n * LUCAS_ANGLE)
        y = mid + r * math.sin(n * LUCAS_ANGLE)
        s = c * (0.36 + 0.14 * math.sqrt(n / SEEDS))
        arm = rank[n % ARMS]
        fill = (SANDSTONE if arm % 2 else RUST) if arm < shown else SEED
        draw.ellipse((x - s, y - s, x + s, y + s), fill=fill)

    count, rest = f"{shown}", f" of {ARMS} arms"
    rest_w = draw.textlength(rest, font=label_font)
    count_w = draw.textlength(count, font=label_font)
    x = W * SS - 12 * SS - rest_w
    y = H * SS - 34 * SS
    draw.text((x - count_w, y), count, font=label_font, fill=RUST)
    draw.text((x, y), rest, font=label_font, fill=SHALE)
    return img.resize((W, H), Image.LANCZOS)


def main():
    rank = arm_rank()
    label_font = font(13 * SS)
    frames = [frame(shown, rank, label_font) for shown in range(ARMS + 1)]
    durations = [700] + [60] * (ARMS - 1) + [3200]
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    print(f"wrote {OUT.relative_to(OUT.parent.parent)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
