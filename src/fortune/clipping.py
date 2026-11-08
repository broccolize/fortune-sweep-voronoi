"""Bounded half-plane intersection over sweep-generated neighbours only.

Angle sorting plus a deque costs O(k log k) for a cell of degree k. This avoids
the quadratic cost of repeatedly clipping a high-degree polygon. The four box
constraints make every nonempty result bounded.
"""

from collections import deque
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import cmp_to_key
import math
from .geometry import Point

@dataclass(slots=True)
class HalfPlane:
    a: float
    b: float
    c: float  # unit-normal inequality a*x + b*y <= c
    neighbour: int | None = None
    focuses: tuple[Point, Point] | None = None

    def exact(self):
        if self.focuses is None:
            return Decimal(self.a), Decimal(self.b), Decimal(self.c)
        p, q = self.focuses
        px, py, qx, qy = map(Decimal, (p.x, p.y, q.x, q.y))
        a, b = qx - px, qy - py
        return a, b, (a * (px + qx) + b * (py + qy)) / 2

    def rational(self):
        """Exact dyadic coefficients, used only for uncertain topology decisions."""
        if self.focuses is None:
            return Fraction(self.a),Fraction(self.b),Fraction(self.c)
        p,q=self.focuses
        px,py,qx,qy=map(Fraction,(p.x,p.y,q.x,q.y))
        a,b=qx-px,qy-py
        return a,b,(a*(px+qx)+b*(py+qy))/2


def parallel(p,q):
    if abs(p.a*q.b-p.b*q.a)>1e-12:
        return False
    a,b,_=p.rational();d,e,_=q.rational()
    return a*e-b*d==0


def angle_compare(p,q):
    hp=0 if p.b>0 or (p.b==0 and p.a>=0) else 1
    hq=0 if q.b>0 or (q.b==0 and q.a>=0) else 1
    if hp!=hq:return hp-hq
    cross=p.a*q.b-p.b*q.a
    if abs(cross)<=1e-12:
        a,b,_=p.rational();d,e,_=q.rational();cross=a*e-b*d
    return -1 if cross>0 else 1 if cross<0 else 0


def tighter(p,q):
    """Whether q is stricter than a parallel, same-direction plane p."""
    a,b,c=p.rational();d,e,f=q.rational()
    return c*max(abs(d),abs(e))>f*max(abs(a),abs(b))


def corner_inside(test,p,q):
    """Test a corner using exact rational signs when the float result is close.

    Comparing rounded corner coordinates with an epsilon can retain an invalid
    support. Instead evaluate the intersection in homogeneous coordinates, so
    the uncertain sign requires no inexact division.
    """
    point=intersection(p,q)
    if point is None:return False
    value=test.a*point.x+test.b*point.y-test.c
    if abs(value)>1e-10*(1+abs(test.c)+abs(point.x)+abs(point.y)):
        return value<0
    a,b,c=p.rational();d,e,f=q.rational();g,h,k=test.rational()
    determinant=a*e-b*d
    sign=g*(c*e-b*f)+h*(a*f-c*d)-k*determinant
    return sign<=0 if determinant>0 else sign>=0


def concurrent(p,q,r):
    a,b,c=p.rational();d,e,f=q.rational();g,h,k=r.rational()
    return a*(e*k-f*h)-b*(d*k-f*g)+c*(d*h-e*g)==0


def intersection(p, q):
    det = p.a * q.b - p.b * q.a
    if abs(det) < 1e-7:
        # Recompute from exact binary focus coordinates, not from rounded
        # normalized plane coefficients: close-site bisectors amplify that error.
        if parallel(p,q):
            return None
        with localcontext() as ctx:
            ctx.prec = 80
            a, b, c = p.exact()
            d, e, f = q.exact()
            denominator = a * e - b * d
            if not denominator:
                return None
            return Point(float((c * e - b * f) / denominator),
                         float((a * f - c * d) / denominator))
    return Point((p.c * q.b - p.b * q.c) / det,
                 (p.a * q.c - p.c * q.a) / det)


def halfplane_polygon(planes):
    ordered = sorted(planes, key=cmp_to_key(angle_compare))
    unique = []
    for h in ordered:
        if unique:
            p = unique[-1]
            if parallel(p,h) and p.a * h.a + p.b * h.b > 0:
                if tighter(p,h):
                    unique[-1] = h
                continue
        unique.append(h)
    active = deque()
    for h in unique:
        while len(active) > 1:
            p = intersection(active[-2], active[-1])
            if p is None:
                return [], []
            if corner_inside(h,active[-2],active[-1]):
                break
            active.pop()
        while len(active) > 1:
            p = intersection(active[0], active[1])
            if p is None:
                return [], []
            if corner_inside(h,active[0],active[1]):
                break
            active.popleft()
        if active and intersection(active[-1], h) is None:
            return [], []
        active.append(h)
    while len(active) > 2 and not corner_inside(active[0],active[-2],active[-1]):
        active.pop()
    while len(active) > 2 and not corner_inside(active[-1],active[0],active[1]):
        active.popleft()
    if len(active) < 3:
        return [], []
    active = list(active)
    vertices = [intersection(active[i - 1], active[i]) for i in range(len(active))]
    if any(p is None for p in vertices):
        return [], []
    # A short edge can be real: tiny cells must not be removed by a distance
    # cutoff. Discard a support only if three defining lines are truly concurrent.
    active = [h for i,h in enumerate(active)
              if not (vertices[i].distance(vertices[(i+1)%len(vertices)])<1e-12
                      and concurrent(active[i-1],h,active[(i+1)%len(active)]))]
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
        planes.append(HalfPlane(a, b, a * (p.x + q.x) / 2 + b * (p.y + q.y) / 2, j, (p, q)))
    return halfplane_polygon(planes)
