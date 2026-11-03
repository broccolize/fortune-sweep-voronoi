"""Independent O(n) / O(n^2) validators; never imported by the algorithm."""

import math
import random
from fortune.geometry import Point, polygon_area


def contains(polygon, p, tolerance=2e-10):
    if len(polygon) < 3:
        return False
    # Clipped cells are convex and ordered counterclockwise.
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        cross = (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)
        # Very short exported edges suffer endpoint subtraction error; the
        # cross-product uncertainty depends on coordinate ULP, not just length.
        ulp = math.ulp(max(abs(a.x),abs(a.y),abs(b.x),abs(b.y)))
        uncertainty = 8 * ulp * (abs(p.x-a.x)+abs(p.y-a.y))
        if cross < -tolerance * max(1e-30, a.distance(b)) - uncertainty:
            return False
    return True


def validate_cells(diagram, queries=300, seed=42):
    box, rng = diagram.box, random.Random(seed)
    scale = max(box.xmax - box.xmin, box.ymax - box.ymin)
    area = sum(polygon_area(c.vertices) for c in diagram.cells)
    assert math.isclose(area, (box.xmax - box.xmin) * (box.ymax - box.ymin),
                        rel_tol=2e-8, abs_tol=1e-11 * scale ** 2), ('area',area)
    for _ in range(queries):
        p = Point(rng.uniform(box.xmin, box.xmax), rng.uniform(box.ymin, box.ymax))
        owners = [c.site for c in diagram.cells if contains(c.vertices, p, 1e-10 * scale)]
        distances = [p.distance(s) for s in diagram.sites]
        nearest = min(distances)
        assert owners, ('hole',p)
        assert all(distances[i] <= nearest + 1e-8 * scale for i in owners), ('owner',p,owners)


def validate_empty_circles(diagram):
    for vertex in diagram.vertices:
        ds = [vertex.point.distance(p) for p in diagram.sites]
        defining = [ds[i] for i in vertex.defining]
        r = defining[0]
        # Exporting normalized results back near 1e9 necessarily rounds to a
        # world-coordinate ULP (~1e-7). Include that representational error.
        coordinate_ulp = math.ulp(max(abs(vertex.point.x), abs(vertex.point.y)))
        tolerance = 1e-8 * max(1, r) + 8 * coordinate_ulp
        assert max(defining) - min(defining) <= tolerance, ('equidistance',vertex)
        assert min(ds) >= r - tolerance, ('nonempty',vertex,min(ds),r)
