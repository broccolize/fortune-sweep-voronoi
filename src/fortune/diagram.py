"""Public construction API and ordered clipped-cell output model."""

import math
from dataclasses import dataclass, field
from time import perf_counter

from .clipping import clipped_cell
from .frame import CoordinateFrame, inferred_box
from .geometry import Box, Point, orient, polygon_area
from .sweep import FortuneSweep, Vertex, all_collinear, collinear_neighbours


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
    delaunay_edges: list[tuple[int, int]] = field(default_factory=list)


def hull_order(points):
    """Convex-hull boundary, retaining collinear sites along a hull edge."""
    ids = sorted(range(len(points)), key=lambda i: (points[i].x, points[i].y))
    lower, upper = [], []
    for i in ids:
        while (
            len(lower) > 1
            and orient(points[lower[-2]], points[lower[-1]], points[i]) < 0
        ):
            lower.pop()
        lower.append(i)
    for i in reversed(ids):
        while (
            len(upper) > 1
            and orient(points[upper[-2]], points[upper[-1]], points[i]) < 0
        ):
            upper.pop()
        upper.append(i)
    return lower[:-1] + upper[:-1]


def delaunay_triangulation(sites, sweep, zero_edges):
    """Dual edges, with a deterministic fan for each exactly cocircular face.

    A Voronoi vertex shared by more than three sites defines a convex polygon
    with several valid Delaunay triangulations. Use its lexicographically first
    site as the fan anchor, so the diagonals do not depend on event/input order.
    Collinear input retains the consecutive-site chain.
    """
    edges = set(sweep.edges) - zero_edges
    for vertex in sweep.vertices:
        if len(vertex.defining) <= 3:
            continue
        ids = sorted(vertex.defining)
        ring = [ids[i] for i in hull_order([sites[i] for i in ids])]
        for other in ring[2:-1]:
            edges.add(tuple(sorted((ring[0], other))))
    return sorted(edges)


def construct(coordinates, box=None, *, debug=False):
    """Build a Voronoi diagram; exact duplicates share one cell and index list.

    Geometric calculations use an exactly representable uniform transform.
    Distinct near-coincident points are not deliberately merged. Coordinate
    ranges that lose subnormal bits in that transform are rejected explicitly.
    """
    started = perf_counter()
    sites, groups, index = [], [], {}
    input_count = 0
    for i, value in enumerate(coordinates):
        p = (
            value
            if isinstance(value, Point)
            else Point(float(value[0]), float(value[1]))
        )
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
    frame = CoordinateFrame.for_sites(sites)
    world = frame.world
    if box is None:
        box = inferred_box(sites)
    elif not isinstance(box, Box):
        box = Box(*box)
    nbox = frame.normalize_box(box)
    normalized = [frame.normalize(p) for p in sites]
    collinear = all_collinear(sites)
    sweep_start = perf_counter()
    sweep = (
        collinear_neighbours(normalized)
        if collinear
        else FortuneSweep(normalized, debug=debug, original_points=sites).run()
    )
    sweep_seconds = perf_counter() - sweep_start
    hull = [] if collinear else hull_order(sites)
    boundary = set(range(len(sites))) if collinear else set(hull)
    hull_edges = {tuple(sorted((a, b))) for a, b in zip(hull, hull[1:] + hull[:1])}
    # A single-ended trace is a ray only on a hull adjacency. Otherwise it is
    # a zero-length diagonal of a cocircular triangulation, not a real boundary.
    zero_edges = {
        key
        for key, edge in sweep.edges.items()
        if len(edge.vertices) == 1 and key not in hull_edges and not collinear
    }
    dual = delaunay_triangulation(sites, sweep, zero_edges)
    vertices = [Vertex(world(v.point), set(v.defining)) for v in sweep.vertices]
    for identity, i in sweep._vertex_index.items():
        vertices[i].point = Point(float(identity[0]), float(identity[1]))
    cells, edges = [], []
    for i in range(len(sites)):
        neighbours = [
            j
            for j in sorted(sweep.neighbours[i])
            if tuple(sorted((i, j))) not in zero_edges
        ]
        polygon, planes = clipped_cell(i, neighbours, normalized, nbox)
        output_polygon = [world(p) for p in polygon]
        p = sites[i]
        if (
            box.xmin <= p.x <= box.xmax
            and box.ymin <= p.y <= box.ymax
            and (len(output_polygon) < 3 or polygon_area(output_polygon) <= 0)
        ):
            raise ArithmeticError(
                f"Site {i}: output precision cannot retain a positive cell"
            )
        cells.append(
            Cell(
                i,
                groups[i],
                output_polygon,
                i in boundary,
                [h.neighbour for h in planes],
            )
        )
        # Plane k supports the edge from vertex k to vertex k+1 (cyclic).
        for k, h in enumerate(planes):
            j = h.neighbour
            if j is None or i >= j:
                continue
            p, q = polygon[k], polygon[(k + 1) % len(polygon)]
            if p == q:
                continue  # zero-length diagonal at a cocircular vertex
            trace = sweep.edges[(i, j)]
            ends = trace.vertices
            kind = "segment" if len(ends) >= 2 else ("ray" if ends else "line")
            origin = vertices[ends[0]].point if ends else None
            direction = None
            if kind == "ray":
                centre = sweep.vertices[ends[0]].point
                endpoint = p if centre.distance(p) > centre.distance(q) else q
                length = centre.distance(endpoint)
                if length:
                    direction = Point(
                        (endpoint.x - centre.x) / length,
                        (endpoint.y - centre.y) / length,
                    )
            elif kind == "line":
                length = p.distance(q)
                direction = Point((q.x - p.x) / length, (q.y - p.y) / length)
            edges.append(
                Edge(
                    (i, j),
                    world(p),
                    world(q),
                    kind != "segment",
                    kind,
                    origin,
                    direction,
                )
            )
    statistics = dict(sweep.statistics)
    statistics.update(
        input_sites=input_count,
        unique_sites=len(sites),
        duplicates=input_count - len(sites),
        cells=len(cells),
        vertices=len(vertices),
        edges=len(edges),
        delaunay_edges=len(dual),
        sweep_seconds=sweep_seconds,
        construction_seconds=perf_counter() - started,
    )
    return Diagram(sites, cells, edges, vertices, box, statistics, dual)
