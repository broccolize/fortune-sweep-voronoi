"""Fortune's event-driven sweep, producing adjacency and traced Voronoi edges.

No cell is constructed here using comparisons with every other site. The
adjacency graph is generated only by site splits and disappearing arcs.
"""

from dataclasses import dataclass, field
import math
from .beachline import Arc, BeachLine
from .events import Event, EventQueue
from .circle import candidate_circle
from .geometry import Point, orient


@dataclass(slots=True)
class Vertex:
    point: Point
    defining: set[int]


@dataclass(slots=True)
class TraceEdge:
    sites: tuple[int, int]
    vertices: list[int] = field(default_factory=list)


class FortuneSweep:
    def __init__(self, points, debug=False):
        self.points = points
        self.debug = debug
        self.beach = BeachLine()
        self.queue = EventQueue()
        self.sweep_y = math.inf
        self.neighbours = [set() for _ in points]
        self.edges = {}
        self.vertices = []
        self._vertex_index = {}
        self.statistics = dict(site_events=0, circle_events=0, stale_events=0)

    def edge(self, a, b, vertex=None):
        if a == b:
            raise ArithmeticError("An edge cannot separate a site from itself")
        key = (min(a, b), max(a, b))
        if key not in self.edges:
            self.edges[key] = TraceEdge(key)
            self.neighbours[a].add(b)
            self.neighbours[b].add(a)
        edge = self.edges[key]
        if vertex is not None and vertex not in edge.vertices:
            edge.vertices.append(vertex)
        return edge

    def schedule(self, arc):
        if arc is None or not arc.alive:
            return
        arc.generation += 1
        if arc.prev is None or arc.next is None:
            return
        ids = (arc.prev.site, arc.site, arc.next.site)
        result = candidate_circle(*(self.points[i] for i in ids), self.sweep_y)
        if result:
            centre, bottom = result
            self.queue.push(Event(bottom, centre.x, 1, arc=arc,
                                  generation=arc.generation, centre=centre,
                                  defining=ids))

    def site_event(self, site):
        self.statistics['site_events'] += 1
        if self.beach.root is None:
            self.beach.insert_after(None, Arc(site))
            return
        point = self.points[site]
        old = self.beach.locate(point.x, self.sweep_y, self.points)
        before, after = old.prev, old.next
        old.generation += 1
        if self.points[old.site].y == point.y:
            # A whole equal-height batch has vertical limiting parabolas. It
            # inserts an adjacent arc instead of splitting a finite parabola.
            new = Arc(site)
            self.beach.insert_after(old if point.x >= self.points[old.site].x
                                    else old.prev, new)
            self.edge(old.site, site)
            for arc in (before, old, new, after):
                self.schedule(arc)
            return
        new, right = Arc(site), Arc(old.site)
        self.beach.insert_after(old, new)
        self.beach.insert_after(new, right)
        self.edge(old.site, site)
        for arc in (before, old, new, right, after):
            self.schedule(arc)

    def circle_event(self, event):
        middle = event.arc
        if not middle.alive or middle.generation != event.generation:
            self.statistics['stale_events'] += 1
            return
        left, right = middle.prev, middle.next
        if left is None or right is None or (left.site, middle.site, right.site) != event.defining:
            raise ArithmeticError("A valid circle event lost its neighbourhood")
        key = (round(event.centre.x, 14), round(event.centre.y, 14))
        vertex = self._vertex_index.get(key)
        if vertex is None:
            vertex = len(self.vertices)
            self.vertices.append(Vertex(event.centre, set(event.defining)))
            self._vertex_index[key] = vertex
        else:
            self.vertices[vertex].defining.update(event.defining)
        self.edge(left.site, middle.site, vertex)
        self.edge(middle.site, right.site, vertex)
        self.edge(left.site, right.site, vertex)
        self.beach.remove(middle)
        self.statistics['circle_events'] += 1
        self.schedule(left)
        self.schedule(right)

    def run(self):
        for i, p in enumerate(self.points):
            self.queue.push(Event(p.y, p.x, 0, site=i))
        while self.queue:
            event = self.queue.pop()
            self.sweep_y = min(self.sweep_y, event.y)
            if event.kind == 0:
                self.site_event(event.site)
            else:
                self.circle_event(event)
            if self.debug:
                self.beach.validate()
        self.statistics.update(queue_peak=self.queue.peak_size,
                               events_pushed=self.queue.pushed,
                               beach_max_height=self.beach.max_height,
                               trace_edges=len(self.edges))
        return self


def collinear_neighbours(points):
    """One-dimensional degeneration: consecutive sites alone share bisectors."""
    sweep = FortuneSweep(points)
    order = sorted(range(len(points)), key=lambda i: (points[i].x, points[i].y))
    for a, b in zip(order, order[1:]):
        sweep.edge(a, b)
    sweep.statistics['collinear_special_case'] = True
    return sweep


def all_collinear(points):
    if len(points) < 3:
        return True
    a, b = min(points, key=lambda p: (p.x, p.y)), max(points, key=lambda p: (p.x, p.y))
    return all(orient(a, b, p) == 0 for p in points)
