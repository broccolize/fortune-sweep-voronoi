"""A uniform coordinate frame that preserves the input doubles exactly."""

import math
from dataclasses import dataclass

from .geometry import Box, Point


def site_extent(sites):
    xmin, xmax = min(p.x for p in sites), max(p.x for p in sites)
    ymin, ymax = min(p.y for p in sites), max(p.y for p in sites)
    span = max(xmax - xmin, ymax - ymin)
    if not span:
        span = max(1.0, abs(xmin) * 1e-6, abs(ymin) * 1e-6)
    if not math.isfinite(span):
        raise ValueError("Coordinate extent exceeds supported floating-point range")
    return xmin, ymin, xmax, ymax, span


def inferred_box(sites):
    """Pad supplied sites; use the unit square for an empty click canvas."""
    if not sites:
        return Box(0, 0, 1, 1)
    xmin, ymin, xmax, ymax, span = site_extent(sites)
    pad = span * 0.1
    return Box(
        min(xmin - pad, math.nextafter(xmin, -math.inf)),
        min(ymin - pad, math.nextafter(ymin, -math.inf)),
        max(xmax + pad, math.nextafter(xmax, math.inf)),
        max(ymax + pad, math.nextafter(ymax, math.inf)),
    )


def _origin(lo, hi):
    # Sterbenz's lemma makes this subtraction exact when the endpoints have
    # the same sign and lie within a factor of two. Otherwise, leave zero as
    # the origin: subtracting an arbitrary midpoint can erase small offsets.
    if lo == hi or (lo > 0 and hi <= 2 * lo):
        return lo
    if hi < 0 and lo >= 2 * hi:
        return hi
    return 0.0


@dataclass(frozen=True, slots=True)
class CoordinateFrame:
    ox: float
    oy: float
    exponent: int

    @classmethod
    def for_sites(cls, sites):
        xmin, ymin, xmax, ymax, span = site_extent(sites)
        exponent = min(1023, math.frexp(span)[1])
        frame = cls(_origin(xmin, xmax), _origin(ymin, ymax), exponent)
        for p in sites:
            q = frame.normalize(p)
            # Scaling by a power of two is exact unless it loses subnormal
            # bits. Reject that range rather than silently changing topology.
            if (
                math.ldexp(q.x, exponent) != p.x - frame.ox
                or math.ldexp(q.y, exponent) != p.y - frame.oy
            ):
                raise ValueError("Site distinctions exceed supported coordinate range")
        return frame

    @property
    def scale(self):
        return math.ldexp(1.0, self.exponent)

    def normalize(self, p):
        return Point(
            math.ldexp(p.x - self.ox, -self.exponent),
            math.ldexp(p.y - self.oy, -self.exponent),
        )

    def world(self, p):
        return Point(
            self.ox + math.ldexp(p.x, self.exponent),
            self.oy + math.ldexp(p.y, self.exponent),
        )

    def normalize_box(self, box):
        lo = self.normalize(Point(box.xmin, box.ymin))
        hi = self.normalize(Point(box.xmax, box.ymax))
        return Box(lo.x, lo.y, hi.x, hi.y)
