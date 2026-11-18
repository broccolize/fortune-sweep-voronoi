"""Regressions for topology lost to normalization and close event arithmetic."""

import itertools
import json
from fractions import Fraction
from pathlib import Path

import pytest
from validation import validate_cells, validate_empty_circles

from fortune.diagram import construct
from fortune.events import Event, EventQueue
from fortune.frame import CoordinateFrame
from fortune.geometry import Point, circle_identity, polygon_area
from fortune.replay import SweepReplay

PRECISION_CASES = [
    [(0, 0), (2, 1e-16), (3, 0), (3, 2)],
    [
        (8.997599999142925e-16, 2.5500793136439805e-16),
        (8.650989386813507e-16, 3.134167580549946e-16),
        (0.11917669984214596, 0.2747612452227174),
        (0.6654330524247978, 0.11252900539650945),
    ],
    [
        (6.468485059726204e-16, 8.9716234366157e-16),
        (3.0739203679811424e-16, 8.956453016212751e-16),
        (6.046813899453629e-16, 5.270921846937124e-16),
        (0.8438568281093831, 0.6233620664046762),
    ],
    [
        (7.917505060353695e-16, 3.3305159749536654e-16),
        (1.2337502719508586e-16, 2.192321092974804e-16),
        (7.124433658633122e-16, 1.0000000000000009),
        (6.602117000460554e-16, 2.7987042112321583e-16),
    ],
]


def exact_empty_circles(diagram):
    for vertex in diagram.vertices:
        ids = sorted(vertex.defining)
        cx, cy, radius2 = circle_identity(*(diagram.sites[i] for i in ids[:3]))
        for p in diagram.sites:
            assert (Fraction(p.x) - cx) ** 2 + (Fraction(p.y) - cy) ** 2 >= radius2


@pytest.mark.parametrize("points", PRECISION_CASES)
def test_distinctions_and_empty_circles_survive_all_input_orders(points):
    for order in itertools.permutations(points):
        diagram = construct(order, debug=True)
        validate_cells(diagram, queries=40)
        validate_empty_circles(diagram)
        exact_empty_circles(diagram)
        b = diagram.box
        assert sum(polygon_area(c.vertices) for c in diagram.cells) == pytest.approx(
            (b.xmax - b.xmin) * (b.ymax - b.ymin), rel=2e-12
        )


@pytest.mark.parametrize(
    "points",
    [
        PRECISION_CASES[0],
        PRECISION_CASES[1],
        [(1e9, 1e9), (1e9 + 0.1, 1e9 + 1), (1e9 + 1, 1e9 + 0.2)],
        [(-1e9, -1e9), (-1e9 - 0.1, -1e9 - 1), (-1e9 - 1, -1e9 - 0.2)],
    ],
)
def test_frame_is_an_exact_uniform_transform_of_input_doubles(points):
    sites = [Point(*p) for p in points]
    frame = CoordinateFrame.for_sites(sites)
    for p in sites:
        q = frame.normalize(p)
        assert Fraction(q.x) == (Fraction(p.x) - Fraction(frame.ox)) / Fraction(
            frame.scale
        )
        assert Fraction(q.y) == (Fraction(p.y) - Fraction(frame.oy)) / Fraction(
            frame.scale
        )
        assert frame.world(q) == p


def test_underflow_of_a_site_coordinate_is_rejected_explicitly():
    with pytest.raises(ValueError, match="coordinate range"):
        construct([(0, 0), (1e-300, 1e-300), (1e100, 1e100)])


def test_exact_circle_height_orders_events_with_identical_float_bottoms():
    a, c = Point(-1, 0), Point(1, 0)
    circle = Event(-1, 0, 1, circle_points=(a, Point(0, 1), c))
    # Its true bottom is slightly above -1, although its float bottom is -1.
    higher = Event(-1, 0, 1, circle_points=(a, Point(1e-16, 1), c))
    site = Event(-1, 0, 0, site=3)
    queue = EventQueue()
    for event in (circle, site, higher):
        queue.push(event)
    assert [queue.pop(), queue.pop(), queue.pop()] == [higher, site, circle]


def test_close_grid_event_order_retains_all_cell_boundaries():
    points = json.loads(
        (Path(__file__).parent / "data/precision-grid.json").read_text()
    )
    for coordinates in (points, list(reversed(points))):
        diagram = construct(coordinates, debug=True)
        validate_cells(diagram, queries=400)
        exact_empty_circles(diagram)


def test_replay_and_batch_use_the_same_precision_frame_and_topology():
    replay = SweepReplay(PRECISION_CASES[0], debug=True)
    replay.seek(1)
    assert replay.points == [replay.frame.normalize(p) for p in replay.diagram.sites]
    assert len(replay.sweep.vertices) == len(replay.diagram.vertices)
    assert {frozenset(v.defining) for v in replay.sweep.vertices} == {
        frozenset(v.defining) for v in replay.diagram.vertices
    }
