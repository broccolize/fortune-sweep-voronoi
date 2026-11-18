"""Deterministic priority queue: descending y, sites before circles, then x."""

import heapq
import itertools
import math
from dataclasses import dataclass, field
from fractions import Fraction

from .beachline import Arc
from .geometry import Point, circle_identity


def radical_difference_sign(a, b, c, d):
    """Exact sign of (a - sqrt(b)) - (c - sqrt(d)), for rational b,d >= 0."""
    delta = a - c
    if delta < 0:
        return -radical_difference_sign(c, d, a, b)
    if not delta:
        return (d > b) - (d < b)
    remainder = b - d - delta * delta
    if remainder < 0:
        return 1
    value = 4 * delta * delta * d - remainder * remainder
    return (value > 0) - (value < 0)


class SweepHeight:
    """Descending heap height, with exact radical comparisons near a tie.

    Most comparisons use doubles. Exact circumcircles are evaluated lazily only
    when the error intervals overlap; no rounded centre or epsilon decides a tie.
    """

    __slots__ = ("approx", "error", "points", "_exact")

    def __init__(self, event):
        self.approx = event.y
        centre = event.centre or Point(0, 0)
        self.error = 128 * math.ulp(
            max(1.0, abs(event.y), abs(centre.x), abs(centre.y))
        )
        self.points = event.circle_points
        self._exact = None

    def exact(self):
        if self._exact is None:
            if self.points is None:
                self._exact = Fraction(self.approx), Fraction(0)
            else:
                _, y, radius_squared = circle_identity(*self.points)
                self._exact = y, radius_squared
        return self._exact

    def compare(self, other):
        difference = self.approx - other.approx
        if abs(difference) > self.error + other.error:
            return 1 if difference > 0 else -1
        return radical_difference_sign(*self.exact(), *other.exact())

    def __lt__(self, other):
        return self.compare(other) > 0

    def __eq__(self, other):
        if not isinstance(other, SweepHeight):
            return NotImplemented
        return self.compare(other) == 0


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
    circle_points: tuple[Point, Point, Point] | None = None
    _height: SweepHeight | None = field(default=None, repr=False, compare=False)

    @property
    def height(self):
        if self._height is None:
            self._height = SweepHeight(self)
        return self._height


class EventQueue:
    def __init__(self):
        self._heap = []
        self._serial = itertools.count()
        self.peak_size = 0
        self.pushed = 0

    def push(self, event):
        heapq.heappush(
            self._heap, (event.height, event.kind, event.x, next(self._serial), event)
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
