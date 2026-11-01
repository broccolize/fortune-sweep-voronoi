"""Bounded half-plane intersection over sweep-generated neighbours only.

Angle sorting plus a deque costs O(k log k) for a cell of degree k. This avoids
the quadratic cost of repeatedly clipping a high-degree polygon. The four box
constraints make every nonempty result bounded.
"""

from collections import deque
from dataclasses import dataclass
import math
from .geometry import Point

EPS = 2e-13  # signed distance in the normalized construction frame


@dataclass(slots=True)
class HalfPlane:
    a: float
    b: float
    c: float  # unit-normal inequality a*x + b*y <= c
    neighbour: int | None = None

    def contains(self, point):
        return self.a * point.x + self.b * point.y <= self.c + EPS


def intersection(p, q):
    det = p.a * q.b - p.b * q.a
    if abs(det) < 2e-15:
        return None
    return Point((p.c * q.b - p.b * q.c) / det,
                 (p.a * q.c - p.c * q.a) / det)


def halfplane_polygon(planes):
    ordered = sorted(planes, key=lambda h: math.atan2(h.b, h.a))
    unique = []
    for h in ordered:
        if unique:
            p = unique[-1]
            if abs(p.a * h.b - p.b * h.a) < 2e-15 and p.a * h.a + p.b * h.b > 0:
                if h.c < p.c:
                    unique[-1] = h
                continue
        unique.append(h)
    active = deque()
    for h in unique:
        while len(active) > 1:
            p = intersection(active[-2], active[-1])
            if p is None:
                return [], []
            if h.contains(p):
                break
            active.pop()
        while len(active) > 1:
            p = intersection(active[0], active[1])
            if p is None:
                return [], []
            if h.contains(p):
                break
            active.popleft()
        if active and intersection(active[-1], h) is None:
            return [], []
        active.append(h)
    while len(active) > 2 and not active[0].contains(intersection(active[-2], active[-1])):
        active.pop()
    while len(active) > 2 and not active[-1].contains(intersection(active[0], active[1])):
        active.popleft()
    if len(active) < 3:
        return [], []
    active = list(active)
    vertices = [intersection(active[i - 1], active[i]) for i in range(len(active))]
    if any(p is None for p in vertices):
        return [], []
    # Concurrent constraints can make an edge mathematically zero-length.
    # Keeping its rounded endpoints creates a tiny, arbitrarily directed edge
    # that can reverse a convex-polygon containment test. Remove the redundant
    # supporting planes in one linear pass and recompute their true corners.
    active = [h for i, h in enumerate(active)
              if vertices[i].distance(vertices[(i + 1) % len(vertices)]) > 5e-15]
    if len(active) < 3:
        return [], []
    vertices = [intersection(active[i - 1], active[i]) for i in range(len(active))]
    return vertices, active


def clipped_cell(site, neighbours, points, box):
    p = points[site]
    planes = [HalfPlane(-1, 0, -box.xmin), HalfPlane(1, 0, box.xmax),
              HalfPlane(0, -1, -box.ymin), HalfPlane(0, 1, box.ymax)]
    for j in neighbours:
        q = points[j]
        dx, dy = q.x - p.x, q.y - p.y
        d = math.hypot(dx, dy)
        if not d:
            raise ArithmeticError("Duplicate site survived deduplication")
        a, b = dx / d, dy / d
        planes.append(HalfPlane(a, b, a * (p.x + q.x) / 2 + b * (p.y + q.y) / 2, j))
    return halfplane_polygon(planes)
