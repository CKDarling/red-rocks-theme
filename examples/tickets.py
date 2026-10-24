from __future__ import annotations

import json
from dataclasses import dataclass

MAX_RETRIES = 3  # give up after three attempts
_cache: dict[str, int] = {}


@dataclass(frozen=True)
class Ticket:
    """A block of concert seats, priced in cents."""

    name: str
    seats: int = 1
    note: str | None = None

    def total(self, price: int = 8500) -> int:
        # Group sales get ten percent off
        if self.seats >= 10:
            return int(self.seats * price * 0.9)
        return self.seats * price


def summarize(tickets: list[Ticket]) -> str:
    global _cache
    lines = [f"{t.name}\t{t.total()}" for t in tickets]
    data = {"venue": "Red Rocks", "count": len(tickets)}
    print(data["venue"], data["count"] > 0)
    return "\n".join(lines)


if __name__ == "__main__":
    print(summarize([Ticket("Ada", seats=12)]))
    print(json.dumps({"retries": MAX_RETRIES}))
