"""Copy the small mutable event state for at most eight replay checkpoints.

Copying explicitly preserves live arc identities, heap serial priorities and
stale-event tombstones without following arbitrarily long neighbour cycles.
The construction algorithm does not use checkpoints.
"""

import itertools

from .beachline import Arc
from .events import Event
from .sweep import FortuneSweep, TraceEdge, Vertex


def clone_sweep(source, extra_event=None):
    result = FortuneSweep(
        source.points, debug=source.debug, original_points=source.original_points
    )
    arcs = {
        a: Arc(a.site, height=a.height, generation=a.generation, alive=a.alive)
        for a in source.beach
    }
    for old, new in list(arcs.items()):
        for link in ("left", "right", "parent", "prev", "next"):
            setattr(new, link, arcs.get(getattr(old, link)))
    result.beach.root = arcs.get(source.beach.root)
    result.beach.first = arcs.get(source.beach.first)
    result.beach.count = source.beach.count
    result.beach.max_height = source.beach.max_height

    def clone_event(event):
        if event is None:
            return None
        arc = event.arc
        if arc is not None and arc not in arcs:
            # A removed arc is only consulted by the stale-event guard.
            arcs[arc] = Arc(arc.site, generation=arc.generation, alive=arc.alive)
        return Event(
            event.y,
            event.x,
            event.kind,
            site=event.site,
            arc=arcs.get(arc),
            generation=event.generation,
            centre=event.centre,
            defining=event.defining,
        )

    result.queue._heap = [
        (*entry[:4], clone_event(entry[-1])) for entry in source.queue._heap
    ]
    # Each push consumes one serial; the next value equals the push count.
    result.queue._serial = itertools.count(source.queue.pushed)
    result.queue.peak_size = source.queue.peak_size
    result.queue.pushed = source.queue.pushed
    result.sweep_y = source.sweep_y
    result.neighbours = [set(ns) for ns in source.neighbours]
    result.edges = {
        key: TraceEdge(edge.sites, list(edge.vertices))
        for key, edge in source.edges.items()
    }
    result.vertices = [Vertex(v.point, set(v.defining)) for v in source.vertices]
    result._vertex_index = dict(source._vertex_index)
    result.statistics = dict(source.statistics)
    result._started = source._started
    if result.debug:
        result.beach.validate()
    return result, clone_event(extra_event)
