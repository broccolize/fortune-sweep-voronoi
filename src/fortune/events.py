"""Deterministic priority queue: descending y, sites before circles, then x."""

from dataclasses import dataclass
import heapq
import itertools
from .geometry import Point
from .beachline import Arc


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
        heapq.heappush(self._heap, (-event.y, event.kind, event.x,
                                  next(self._serial), event))
        self.pushed += 1
        self.peak_size = max(self.peak_size, len(self._heap))

    def pop(self):
        return heapq.heappop(self._heap)[-1]

    def __bool__(self):
        return bool(self._heap)
