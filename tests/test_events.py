import pytest
from fortune.events import Event, EventQueue
from fortune.circle import candidate_circle
from fortune.geometry import Point
from fortune.sweep import FortuneSweep


def test_queue_order_and_stable_ties():
    queue = EventQueue()
    events = [Event(1, 0, 1), Event(2, 3, 0), Event(1, 1, 0), Event(1, 0, 0)]
    for event in events:
        queue.push(event)
    assert [queue.pop() for _ in events] == [events[1], events[3], events[2], events[0]]


def test_circle_clockwise_and_future_only():
    a, b, c = Point(-1, 1), Point(0, 2), Point(1, 1)
    centre, bottom = candidate_circle(a, b, c, 1)
    assert centre == Point(0, 1)
    assert bottom == 0
    assert candidate_circle(c, b, a, 1) is None
    assert candidate_circle(a, b, c, -1) is None
    assert candidate_circle(a, b, a, 1) is None


def test_triangle_sweep_emits_vertex_and_three_edges():
    sweep = FortuneSweep([Point(0, 0), Point(2, 0), Point(1, 2)],debug=True).run()
    assert len(sweep.vertices) == 1
    assert sweep.vertices[0].point == Point(1, 0.75)
    assert len(sweep.edges) == 3
    assert sweep.statistics['circle_events'] == 1


def test_cocircular_square_merges_simultaneous_vertices():
    sweep = FortuneSweep([Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)],debug=True).run()
    assert len(sweep.vertices) == 1
    assert sweep.vertices[0].point == Point(.5, .5)
    assert sweep.vertices[0].defining == {0, 1, 2, 3}
