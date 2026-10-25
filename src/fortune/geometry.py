"""Small geometric primitives, with explicit singular cases and filtered signs."""

from dataclasses import dataclass
from decimal import Decimal, localcontext
import math


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float

    def distance(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)


@dataclass(frozen=True, slots=True)
class Box:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    def __post_init__(self):
        if not all(math.isfinite(v) for v in self.as_tuple()):
            raise ValueError("Bounding-box coordinates must be finite")
        if self.xmin >= self.xmax or self.ymin >= self.ymax:
            raise ValueError("Bounding box must have positive width and height")

    def as_tuple(self):
        return self.xmin, self.ymin, self.xmax, self.ymax


def orient(a: Point, b: Point, c: Point) -> float:
    """Positive for CCW. Decimal fallback resolves cancellation of float products.

    This is a filtered predicate, not arbitrary-precision construction: input
    coordinates and returned circumcentres are still IEEE double precision.
    """
    ux, uy = b.x - a.x, b.y - a.y
    vx, vy = c.x - a.x, c.y - a.y
    left, right = ux * vy, uy * vx
    det = left - right
    if abs(det) > 8e-16 * (abs(left) + abs(right)):
        return det
    with localcontext() as ctx:
        ctx.prec = 80
        ax, ay = Decimal(a.x), Decimal(a.y)
        bx, by = Decimal(b.x), Decimal(b.y)
        cx, cy = Decimal(c.x), Decimal(c.y)
        exact = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    value = float(exact)
    if value == 0.0 and exact:
        return math.copysign(math.ulp(0.0), 1 if exact > 0 else -1)
    return value


def circumcircle(a: Point, b: Point, c: Point):
    """Return (centre, radius), or None for exactly collinear input.

    Translation to a local origin avoids subtracting large squared coordinates.
    For cancellation-prone determinants, recompute the construction in Decimal.
    """
    ux, uy = b.x - a.x, b.y - a.y
    vx, vy = c.x - a.x, c.y - a.y
    cross = ux * vy - uy * vx
    if abs(cross) <= 8e-16 * (abs(ux * vy) + abs(uy * vx)):
        with localcontext() as ctx:
            ctx.prec = 80
            ax, ay = Decimal(a.x), Decimal(a.y)
            u, v = Decimal(b.x) - ax, Decimal(b.y) - ay
            s, t = Decimal(c.x) - ax, Decimal(c.y) - ay
            d = 2 * (u * t - v * s)
            if not d:
                return None
            u2, s2 = u * u + v * v, s * s + t * t
            centre = Point(float(ax + (u2 * t - s2 * v) / d),
                           float(ay + (u * s2 - s * u2) / d))
    else:
        u2, v2 = ux * ux + uy * uy, vx * vx + vy * vy
        centre = Point(a.x + (u2 * vy - v2 * uy) / (2 * cross),
                       a.y + (ux * v2 - vx * u2) / (2 * cross))
    radius = centre.distance(a)
    if not math.isfinite(radius):
        raise ArithmeticError("Circumcircle is outside the supported float range")
    return centre, radius


def parabola_y(focus: Point, x: float, directrix: float) -> float:
    gap = focus.y - directrix
    if gap <= 0:
        raise ValueError("A finite beach parabola needs its focus above the directrix")
    return (x - focus.x) ** 2 / (2 * gap) + (focus.y + directrix) / 2


def breakpoint_x(left: Point, right: Point, directrix: float) -> float:
    """Breakpoint between consecutive arcs in a downward sweep.

    Equal-height sites give a linear equation. A focus on the directrix gives
    a vertical limiting arc. The remaining quadratic is solved with a stable
    two-root formula, in coordinates translated to the left focus.
    """
    if left.y == right.y:
        return left.x + (right.x - left.x) / 2
    dp, dq = left.y - directrix, right.y - directrix
    if dp <= 0:
        return left.x
    if dq <= 0:
        return right.x
    dx = right.x - left.x
    aa = right.y - left.y
    bb = 2 * dp * dx
    cc = -dp * dx * dx - aa * dp * dq
    discr = bb * bb - 4 * aa * cc
    # Roundoff may make a mathematically nonnegative discriminant slightly negative.
    if discr < 0:
        if discr < -2e-14 * (bb * bb + abs(4 * aa * cc)):
            raise ArithmeticError("Negative breakpoint discriminant")
        discr = 0.0
    q = -0.5 * (bb + math.copysign(math.sqrt(discr), bb))
    roots = (q / aa, cc / q) if q else (-bb / (2 * aa),) * 2
    root = min(roots) if left.y > right.y else max(roots)
    return left.x + root


def circle_bottom(centre: Point, through: Point) -> float:
    """Avoid cancellation in centre.y - radius when the centre is high above."""
    dx, dy = centre.x - through.x, centre.y - through.y
    radius = math.hypot(dx, dy)
    if dy >= 0 and radius + dy:
        return through.y - dx * dx / (radius + dy)
    return centre.y - radius


def polygon_area(points) -> float:
    if len(points) < 3:
        return 0.0
    origin = points[0]
    return abs(math.fsum(orient(origin, points[i], points[i + 1])
                         for i in range(1, len(points) - 1))) / 2
