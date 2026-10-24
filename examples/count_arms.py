"""Count a sunflower's 47 spiral arms in the terminal.

Colors are the 16 standard ANSI codes, so the active VS Code theme picks the
actual hues: seeds use ansiBrightBlack, arms alternate ansiRed and ansiYellow.
"""

from __future__ import annotations

import math
import sys
import time

from sunflower import Sunflower

SIZE = 40  # dots across; each terminal cell holds two dots stacked with ▀
SEEDS = 600
LUCAS_ANGLE = 2 * math.pi / (3 + (math.sqrt(5) - 1) / 2)  # 99.50°

SEED, ARM_A, ARM_B = 90, 31, 33  # bright black, red, yellow


def nearest_seeds() -> list[list[int | None]]:
    """Map every dot in the grid to the seed that covers it, or None."""
    mid = (SIZE - 1) / 2
    c = (SIZE / 2) / math.sqrt(SEEDS)
    seeds = [
        (mid + c * math.sqrt(n) * math.cos(n * LUCAS_ANGLE),
         mid + c * math.sqrt(n) * math.sin(n * LUCAS_ANGLE))
        for n in range(1, SEEDS + 1)
    ]
    grid: list[list[int | None]] = []
    for y in range(SIZE):
        row: list[int | None] = []
        for x in range(SIZE):
            if math.hypot(x - mid, y - mid) > SIZE / 2:
                row.append(None)
                continue
            d, n = min((math.hypot(x - sx, y - sy), i + 1) for i, (sx, sy) in enumerate(seeds))
            row.append(n if d < 1.2 * c else None)
        grid.append(row)
    return grid


def arm_order(k: int) -> list[int]:
    # Arm r starts at seed r. Neighboring arms differ by another Lucas number,
    # so rank them by starting angle to count them side by side.
    by_angle = sorted(range(k), key=lambda r: (r * LUCAS_ANGLE) % (2 * math.pi))
    rank = [0] * k
    for i, r in enumerate(by_angle):
        rank[r] = i
    return rank


def frame(grid: list[list[int | None]], k: int, shown: int) -> str:
    rank = arm_order(k)

    def color(n: int | None) -> int | None:
        if n is None:
            return None
        arm = rank[n % k]
        return (ARM_B if arm % 2 else ARM_A) if arm < shown else SEED

    lines = []
    for top, bottom in zip(grid[::2], grid[1::2]):
        cells = []
        for t, b in zip(map(color, top), map(color, bottom)):
            fg = f"{t}" if t is not None else "39"
            bg = f"{b + 10}" if b is not None else "49"
            cells.append(f"\x1b[{fg};{bg}m▀" if t is not None else f"\x1b[{bg}m ")
        lines.append("".join(cells) + "\x1b[0m")
    lines.append(f"\x1b[{ARM_B}m{shown:>{SIZE // 2 + 1}}\x1b[0m of {k} arms")
    return "\n".join(lines)


def main() -> None:
    head = Sunflower("Helianthus")
    k = head.spirals
    grid = nearest_seeds()
    height = SIZE // 2 + 1
    for shown in range(k + 1):
        if shown:
            sys.stdout.write(f"\x1b[{height}F")
        sys.stdout.write(frame(grid, k, shown) + "\n")
        sys.stdout.flush()
        time.sleep(2.8 / k)
    print(f"{head.name}: {head.lucas()} · safe prime: {head.is_safe_prime()}")


if __name__ == "__main__":
    main()
