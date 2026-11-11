from fortune.beachline import Arc, BeachLine
from fortune.events import Event, EventQueue
from fortune.geometry import Point
from fortune.sweep import FortuneSweep


def _topology(sweep):
    """Freeze topology, including arc identities and mutable edge contents."""
    return (
        sweep.beach.root,
        sweep.beach.first,
        sweep.beach.count,
        tuple(
            (
                arc,
                arc.site,
                arc.left,
                arc.right,
                arc.parent,
                arc.prev,
                arc.next,
                arc.height,
                arc.generation,
                arc.alive,
            )
            for arc in sweep.beach
        ),
        tuple(frozenset(group) for group in sweep.neighbours),
        tuple(
            sorted(
                (key, edge.sites, tuple(edge.vertices))
                for key, edge in sweep.edges.items()
            )
        ),
        tuple(
            (vertex.point, frozenset(vertex.defining))
            for vertex in sweep.vertices
        ),
        dict(sweep._vertex_index),
    )


def _dispatch(sweep, event):
    sweep.sweep_y = min(sweep.sweep_y, event.y)
    if event.kind == 0:
        sweep.site_event(event.site)
    else:
        sweep.circle_event(event)
    sweep.beach.validate()


def _pending_triangle():
    # The clockwise triple (-2, 0), (0, 2), (2, 0) lies on
    # the circle centred at (0, 0), with bottom y = -2.
    sweep = FortuneSweep(
        [Point(0, 2), Point(-2, 0), Point(2, 0)],
        debug=True,
    )
    for site in range(3):
        sweep.sweep_y = sweep.points[site].y
        sweep.site_event(site)
        sweep.beach.validate()

    event = sweep.queue.pop()
    assert not sweep.queue
    assert event.defining == (1, 0, 2)
    assert event.centre == Point(0, 0)
    assert event.y == -2
    assert event.arc.alive
    return sweep, event


def test_site_insertion_supersedes_live_prediction_without_topology_changes():
    points = [
        Point(0, 2),
        Point(-2, 0),
        Point(2, 0),
        Point(-4, -1),
    ]
    sweep = FortuneSweep(points, debug=True)
    for site, point in enumerate(points):
        sweep.queue.push(Event(point.y, point.x, 0, site=site))

    # Process the initial three sites through the real event queue.
    for expected_site in range(3):
        event = sweep.queue.pop()
        assert event.kind == 0 and event.site == expected_site
        _dispatch(sweep, event)

    # Capture the prediction without removing it from the logical queue.
    site_event = sweep.queue.pop()
    assert site_event.kind == 0 and site_event.site == 3
    pending = sweep.queue.pop()
    assert not sweep.queue
    assert pending.defining == (1, 0, 2)
    assert pending.centre == Point(0, 0)
    assert pending.y == -2
    target = pending.arc
    old_predecessor = target.prev
    sweep.queue.push(pending)

    _dispatch(sweep, site_event)

    # The new site splits the left neighbour. The target survives, but its
    # predecessor is now a different Arc carrying the same site ID.
    assert target.alive
    assert target.prev is not old_predecessor
    assert target.prev.site == old_predecessor.site == 1
    assert (target.prev.site, target.site, target.next.site) == pending.defining
    assert target.generation != pending.generation
    assert sweep.statistics["site_events"] == 4

    # Dispatch any earlier replacement predictions normally. The old
    # prediction must still be harmless when its actual heap turn arrives.
    while True:
        assert sweep.queue
        event = sweep.queue.pop()
        if event is pending:
            break
        _dispatch(sweep, event)

    assert target.alive
    assert (target.prev.site, target.site, target.next.site) == pending.defining
    before = _topology(sweep)
    statistics = sweep.statistics.copy()
    _dispatch(sweep, event)

    assert _topology(sweep) == before
    assert sweep.statistics == {
        **statistics,
        "stale_events": statistics["stale_events"] + 1,
    }


def test_duplicate_circle_delivery_after_arc_removal_is_harmless():
    sweep, prediction = _pending_triangle()
    target = prediction.arc

    # Deliberately duplicate delivery of a genuine scheduled prediction.
    sweep.queue.push(prediction)
    sweep.queue.push(prediction)
    _dispatch(sweep, sweep.queue.pop())

    assert not target.alive
    assert all(arc is not target for arc in sweep.beach)
    assert sweep.statistics["circle_events"] == 1
    assert len(sweep.vertices) == 1
    assert sweep.vertices[0].point == Point(0, 0)
    assert sweep.vertices[0].defining == {0, 1, 2}
    assert set(sweep.edges) == {(0, 1), (0, 2), (1, 2)}

    before = _topology(sweep)
    statistics = sweep.statistics.copy()
    delayed = sweep.queue.pop()
    assert delayed is prediction
    _dispatch(sweep, delayed)

    assert not sweep.queue
    assert _topology(sweep) == before
    assert sweep.statistics == {
        **statistics,
        "stale_events": statistics["stale_events"] + 1,
    }


def test_two_child_deletion_preserves_queued_deep_successor_identity():
    beach = BeachLine()
    arcs = [Arc(site) for site in range(16)]
    previous = None
    for arc in arcs[:15]:
        beach.insert_after(previous, arc)
        previous = arc
    beach.insert_after(arcs[8], arcs[15])
    beach.validate()

    victim = arcs[7]
    successor = arcs[8]
    assert victim.left is not None and victim.right is not None
    assert successor is victim.next
    assert successor.parent is not victim
    assert successor.left is None
    assert successor.right is arcs[15]

    queue = EventQueue()
    prediction = Event(
        -10,
        0,
        1,
        arc=successor,
        generation=successor.generation,
        centre=Point(0, 0),
        defining=(7, 8, 15),
    )
    queue.push(prediction)
    survivors = [arc for arc in beach if arc is not victim]
    payloads = [(arc, arc.site, arc.generation) for arc in survivors]

    beach.remove(victim)
    beach.validate()

    assert not victim.alive
    assert list(beach) == survivors
    for arc, site, generation in payloads:
        assert arc.alive
        assert arc.site == site
        assert arc.generation == generation

    delivered = queue.pop()
    assert delivered is prediction
    assert delivered.arc is successor
    assert delivered.arc.alive
    assert delivered.arc.site == 8
    assert delivered.arc.generation == delivered.generation
    assert successor.prev is arcs[6]
    assert successor.next is arcs[15]

    # Use the retained handle, rather than searching for its site again.
    # The old neighbourhood prediction is not dispatched as a valid circle.
    beach.remove(delivered.arc)
    beach.validate()
    assert list(beach) == [arc for arc in survivors if arc is not successor]
    assert arcs[6].next is arcs[15]
    assert arcs[15].prev is arcs[6]


def test_exact_heap_priority_ties_are_fifo_across_interleaved_pushes():
    queue = EventQueue()
    circle_a = Event(5, 0, 1, arc=Arc(10))
    circle_b = Event(5, 0, 1, arc=Arc(11))
    site_a = Event(5, 0, 0, site=20)
    site_b = Event(5, 0, 0, site=21)
    higher = Event(6, 100, 1, arc=Arc(12))
    lower = Event(4, -100, 0, site=22)
    left_circle = Event(5, -1, 1, arc=Arc(13))

    for event in (
        circle_a,
        lower,
        site_a,
        circle_b,
        higher,
        left_circle,
        site_b,
    ):
        queue.push(event)

    assert queue.pop() is higher
    assert queue.pop() is site_a

    # New ties must follow older pending ties, even after partial draining.
    site_c = Event(5, 0, 0, site=23)
    circle_c = Event(5, 0, 1, arc=Arc(14))
    queue.push(circle_c)
    queue.push(site_c)

    expected = [
        site_b,
        site_c,
        left_circle,
        circle_a,
        circle_b,
        circle_c,
        lower,
    ]
    for event in expected:
        assert queue.pop() is event
    assert not queue
