"""Public construction API and ordered clipped-cell output model."""

from dataclasses import dataclass, field
import math
from time import perf_counter
from .geometry import Point, Box, orient
from .sweep import FortuneSweep, collinear_neighbours, all_collinear, Vertex
from .clipping import clipped_cell


@dataclass(slots=True)
class Cell:
    site: int
    input_indices: list[int]
    vertices: list[Point]
    unbounded: bool
    boundary_neighbours: list[int | None] = field(default_factory=list)


@dataclass(slots=True)
class Edge:
    sites: tuple[int, int]
    start: Point
    end: Point
    unbounded: bool
    kind: str
    origin: Point | None
    direction: Point | None


@dataclass(slots=True)
class Diagram:
    sites: list[Point]
    cells: list[Cell]
    edges: list[Edge]
    vertices: list[Vertex]
    box: Box
    statistics: dict = field(default_factory=dict)


def hull_sites(points):
    """Convex-hull boundary, retaining collinear sites along a hull edge."""
    ids = sorted(range(len(points)), key=lambda i: (points[i].x, points[i].y))
    lower, upper = [], []
    for i in ids:
        while len(lower) > 1 and orient(points[lower[-2]], points[lower[-1]], points[i]) < 0:
            lower.pop()
        lower.append(i)
    for i in reversed(ids):
        while len(upper) > 1 and orient(points[upper[-2]], points[upper[-1]], points[i]) < 0:
            upper.pop()
        upper.append(i)
    return set(lower + upper)


def construct(coordinates, box=None, *, debug=False):
    """Build a Voronoi diagram; exact duplicates share one cell and index list.

    Geometric calculations use a translated, uniformly scaled frame. Distinct
    near-coincident points are not deliberately merged. Extremely disparate
    coordinates that collapse in normalization are rejected explicitly.
    """
    started = perf_counter()
    sites, groups, index = [], [], {}
    input_count = 0
    for i, value in enumerate(coordinates):
        p = value if isinstance(value, Point) else Point(float(value[0]), float(value[1]))
        if not math.isfinite(p.x) or not math.isfinite(p.y):
            raise ValueError(f"Site {i} has a non-finite coordinate")
        key = (p.x, p.y)
        if key not in index:
            index[key] = len(sites)
            sites.append(p)
            groups.append([])
        groups[index[key]].append(i)
        input_count += 1
    if not sites:
        raise ValueError("At least one finite site is required")
    xmin, xmax = min(p.x for p in sites), max(p.x for p in sites)
    ymin, ymax = min(p.y for p in sites), max(p.y for p in sites)
    scale = max(xmax - xmin, ymax - ymin)
    if not scale:
        scale = max(1.0, abs(xmin) * 1e-6, abs(ymin) * 1e-6)
    if not math.isfinite(scale):
        raise ValueError("Coordinate extent exceeds supported floating-point range")
    ox, oy = xmin + (xmax - xmin) / 2, ymin + (ymax - ymin) / 2

    def normalize(p):
        return Point((p.x - ox) / scale, (p.y - oy) / scale)

    def world(p):
        return Point(ox + scale * p.x, oy + scale * p.y)

    if box is None:
        pad = scale * 0.1
        box = Box(xmin - pad, ymin - pad, xmax + pad, ymax + pad)
    elif not isinstance(box, Box):
        box = Box(*box)
    nbox = Box((box.xmin - ox) / scale, (box.ymin - oy) / scale,
               (box.xmax - ox) / scale, (box.ymax - oy) / scale)
    normalized = [normalize(p) for p in sites]
    if len(set(normalized)) != len(sites):
        raise ValueError("Distinct sites collapse at this floating-point scale")
    collinear = all_collinear(sites)
    sweep_start = perf_counter()
    sweep = (collinear_neighbours(normalized) if collinear
             else FortuneSweep(normalized, debug=debug,original_points=sites).run())
    sweep_seconds = perf_counter() - sweep_start
    boundary = set(range(len(sites))) if collinear else hull_sites(sites)
    vertices = [Vertex(world(v.point), set(v.defining)) for v in sweep.vertices]
    cells, edges = [], []
    for i in range(len(sites)):
        polygon, planes = clipped_cell(i, sorted(sweep.neighbours[i]), normalized, nbox)
        cells.append(Cell(i, groups[i], [world(p) for p in polygon], i in boundary,
                          [h.neighbour for h in planes]))
        # Plane k supports the edge from vertex k to vertex k+1 (cyclic).
        for k, h in enumerate(planes):
            j = h.neighbour
            if j is None or i >= j:
                continue
            p, q = polygon[k], polygon[(k + 1) % len(polygon)]
            if p==q:
                continue  # zero-length diagonal at a cocircular vertex
            trace = sweep.edges[(i, j)]
            ends = trace.vertices
            kind = 'segment' if len(ends) >= 2 else ('ray' if ends else 'line')
            origin = vertices[ends[0]].point if ends else None
            direction = None
            if kind == 'ray':
                centre = sweep.vertices[ends[0]].point
                endpoint = p if centre.distance(p) > centre.distance(q) else q
                length = centre.distance(endpoint)
                if length:
                    direction = Point((endpoint.x - centre.x) / length,
                                      (endpoint.y - centre.y) / length)
            elif kind == 'line':
                length = p.distance(q)
                direction = Point((q.x - p.x) / length, (q.y - p.y) / length)
            edges.append(Edge((i, j), world(p), world(q), kind != 'segment',
                              kind, origin, direction))
    statistics = dict(sweep.statistics)
    statistics.update(input_sites=input_count, unique_sites=len(sites),
                      duplicates=input_count - len(sites), cells=len(cells),
                      vertices=len(vertices), edges=len(edges),
                      sweep_seconds=sweep_seconds,
                      construction_seconds=perf_counter() - started)
    return Diagram(sites, cells, edges, vertices, box, statistics)
