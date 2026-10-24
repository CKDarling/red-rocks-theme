from __future__ import annotations

import json
from dataclasses import dataclass

LUCAS_SEED = (2, 1)  # Fibonacci's sibling: 2, 1, 3, 4, 7, 11, ...
_checked: int = 0


def is_prime(n: int) -> bool:
    global _checked
    _checked += 1
    return n > 1 and all(n % d for d in range(2, int(n**0.5) + 1))


@dataclass(frozen=True)
class Sunflower:
    """A seed head whose spirals count out the Lucas numbers."""

    name: str
    spirals: int = 47
    note: str | None = None

    def lucas(self) -> list[int]:
        seq = list(LUCAS_SEED)
        while seq[-1] < self.spirals:
            seq.append(seq[-1] + seq[-2])
        return seq

    def is_safe_prime(self) -> bool:
        # 47 = 2 * 23 + 1, and 23 is prime as well
        return is_prime(self.spirals) and is_prime((self.spirals - 1) // 2)


if __name__ == "__main__":
    head = Sunflower("Helianthus")
    print(f"{head.name}\t{head.lucas()}")
    print(json.dumps({"safe": head.is_safe_prime(), "checks": _checked}))
