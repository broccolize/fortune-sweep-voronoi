"""Deterministic priority queue: descending y, sites before circles, then x."""

import heapq
import itertools
from dataclasses import dataclass

from .beachline import Arc
from .geometry import Point


@dataclass(slots=True)
class Event:
    y: float
    x: float
    kind: int  # 0 = site, 1 = circle
    site: int | None = None
    arc: Arc | None = None
    generation: int = 0
    centre: Point | None = None
    defining: tuple[int, int, int] | None = None


class EventQueue:
    def __init__(self):
        self._heap = []
        self._serial = itertools.count()
        self.peak_size = 0
        self.pushed = 0

    def push(self, event):
        heapq.heappush(
            self._heap, (-event.y, event.kind, event.x, next(self._serial), event)
        )
        self.pushed += 1
        self.peak_size = max(self.peak_size, len(self._heap))

    def pop(self):
        return heapq.heappop(self._heap)[-1]

    def peek(self):
        """Inspect the next event without changing its heap priority."""
        return self._heap[0][-1] if self._heap else None

    def preview(self, limit=8):
        """Read a bounded, priority-ordered view, including stale entries."""
        if limit < 0:
            raise ValueError("Preview limit must be nonnegative")
        return [item[-1] for item in heapq.nsmallest(limit, self._heap)]

    def __len__(self):
        return len(self._heap)

    def __bool__(self):
        return bool(self._heap)
