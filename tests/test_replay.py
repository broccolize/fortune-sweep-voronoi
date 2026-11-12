import math

import pytest

from fortune.events import Event, EventQueue
from fortune.geometry import Box, Point, parabola_y
from fortune.io import random_sites
from fortune.replay import SweepReplay, stale
from fortune.sweep import FortuneSweep


def signature(sweep):
    return (
        tuple((v.point, frozenset(v.defining)) for v in sweep.vertices),
        tuple((key, tuple(e.vertices)) for key, e in sorted(sweep.edges.items())),
        tuple(frozenset(ns) for ns in sweep.neighbours),
        dict(sweep.statistics),
    )


def test_queue_preview_is_ordered_without_popping():
    queue = EventQueue()
    events = [Event(2, 0, 1), Event(2, 1, 0), Event(3, 0, 0), Event(2, 0, 0)]
    for e in events:
        queue.push(e)
    before = tuple(queue._heap)
    assert queue.preview(3) == [events[2], events[3], events[1]]
    assert tuple(queue._heap) == before
    assert queue.peek() is events[2] and len(queue) == 4
    assert queue.preview(0) == []
    with pytest.raises(ValueError):
        queue.preview(-1)


@pytest.mark.parametrize("seed", range(8))
def test_stepping_matches_batch_and_keeps_invariants(seed):
    points = random_sites(18, seed)
    batch = FortuneSweep(points, debug=True).run()
    stepped = FortuneSweep(points, debug=True).start()
    previous = math.inf
    while (event := stepped.step()) is not None:
        assert event.y <= previous
        previous = event.y
        stepped.beach.validate()
    assert signature(stepped) == signature(batch)
    assert stepped.step() is None
    assert signature(stepped.run()) == signature(batch)


@pytest.mark.parametrize("seed", range(5))
def test_replay_frames_do_not_cross_pending_events(seed):
    replay = SweepReplay(random_sites(10, seed), Box(0, 0, 1, 1), debug=True)
    previous = replay.display_y
    stale_count = 0
    frames = 0
    while not replay.done:
        target = min(replay.sweep.sweep_y, replay.sweep.queue.peek().y)
        event = replay.tick(4)
        assert target <= replay.display_y <= previous
        previous = replay.display_y
        replay.curves()
        if event is not None and replay.last_stale:
            stale_count += 1
        frames += 1
        assert frames < 500
    assert stale_count == replay.sweep.statistics["stale_events"]
    assert len(replay.processed) == 10
    expected = FortuneSweep(
        replay.points, debug=True, original_points=replay.sites
    ).run()
    assert signature(replay.sweep) == signature(expected)


def test_arc_samples_are_true_parabolas_and_reset_is_repeatable():
    replay = SweepReplay([(0.1, 0.85), (0.8, 0.65), (0.35, 0.15)], Box(0, 0, 1, 1))
    replay.step_event()
    replay.step_event()
    replay.tick(6)
    assert replay.curves()
    for curve in replay.curves():
        assert not curve.limiting
        for p in curve.points:
            q = replay.normalize(p)
            assert q.y == pytest.approx(
                parabola_y(replay.points[curve.site], q.x, replay.display_y)
            )
    first = []
    replay.reset()
    while (event := replay.step_event()) is not None:
        first.append((event.kind, event.y, event.x, replay.last_stale))
    replay.reset()
    second = []
    while (event := replay.step_event()) is not None:
        second.append((event.kind, event.y, event.x, replay.last_stale))
    assert first == second


@pytest.mark.parametrize(
    "points",
    [
        [(0, 0)],
        [(0, 0), (1, 0)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 0), (0, 1), (0, 2)],
        [(0, 0), (1, 2), (2, 4)],
    ],
)
def test_collinear_solver_is_shown_without_a_fabricated_sweep(points):
    replay = SweepReplay(points)
    assert replay.special_case and replay.done
    assert replay.step_event() is None and replay.curves() == []
    assert len(replay.diagram.cells) == len(points)


def test_equal_heights_cocircularity_duplicates_and_stale_queue():
    replay = SweepReplay([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)], debug=True)
    assert len(replay.sites) == 4 and replay.label(0) == "0/4"
    found_stale = False
    while not replay.done:
        replay.step_event()
        replay.curves()
        found_stale |= any(stale(e) for e in replay.sweep.queue.preview(100))
    assert found_stale
    assert len(replay.sweep.vertices) == 1
    assert replay.sweep.vertices[0].defining == {0, 1, 2, 3}


def test_replay_input_errors_and_capacity_are_explicit():
    with pytest.raises(ValueError):
        SweepReplay([])
    with pytest.raises(ValueError):
        SweepReplay([(math.nan, 0)])
    with pytest.raises(ValueError, match="at most 200"):
        SweepReplay(random_sites(201, 2))
    replay = SweepReplay(random_sites(4, 2))
    with pytest.raises(ValueError):
        replay.tick(0)
    with pytest.raises(ValueError):
        replay.curves(1)


@pytest.mark.parametrize("exponent", [10, 13, 15])
def test_near_coincident_replay_geometry_remains_inspectable(exponent):
    delta = 10 ** (-exponent)
    points = [
        Point(0, 0),
        Point(1, 0),
        Point(0, 1),
        Point(1, 1),
        Point(0.5, 0.5),
        Point(0.5 + delta, 0.5 + 2 * delta),
        Point(0.5 - delta, 0.5 + delta),
    ]
    replay = SweepReplay(points, Box(0, 0, 1, 1), debug=True)
    frames = 0
    while not replay.done:
        replay.tick(3)
        replay.curves()
        replay.breakpoints()
        frames += 1
        assert frames < 200
    assert len(replay.diagram.cells) == 7


def test_rendered_arc_intervals_follow_the_processed_parabola_envelope():
    replay = SweepReplay(random_sites(15, 87), Box(0, 0, 1, 1))
    checked = 0
    while not replay.done:
        replay.tick(3)
        for curve in replay.curves(13):
            if curve.limiting:
                continue
            for p in curve.points[1:-1:3]:
                q = replay.normalize(p)
                values = [
                    parabola_y(replay.points[i], q.x, replay.display_y)
                    for i in replay.processed
                    if replay.points[i].y > replay.display_y
                ]
                assert q.y == pytest.approx(min(values), rel=2e-8, abs=2e-8)
                checked += 1
    assert checked > 100


def test_scrubbing_replays_real_topology_in_both_directions():
    replay = SweepReplay(random_sites(20, 42), Box(0, 0, 1, 1), debug=True)
    for position in (0.7, 0.2, 0.9, 0.4, 1.0, 0.0, 0.6):
        replay.seek(position)
        replay.sweep.beach.validate()
        expected = SweepReplay(replay.sites, Box(0, 0, 1, 1), debug=True)
        expected.seek(position)
        assert signature(replay.sweep) == signature(expected.sweep)
        assert replay.processed == expected.processed
        replay.curves()
    with pytest.raises(ValueError):
        replay.seek(-0.1)
    with pytest.raises(ValueError):
        replay.seek_y(math.nan)


def test_playback_uses_elapsed_time_instead_of_frame_count():
    slow = SweepReplay(random_sites(15, 37), Box(0, 0, 1, 1))
    fast = SweepReplay(random_sites(15, 37), Box(0, 0, 1, 1))
    for _ in range(12):
        slow.advance(0.2)
    for _ in range(120):
        fast.advance(0.02)
    assert slow.event_count == fast.event_count
    assert slow.display_y == pytest.approx(fast.display_y)
    assert signature(slow.sweep) == signature(fast.sweep)
    with pytest.raises(ValueError):
        slow.advance(-1)


def test_checkpoint_clone_is_independent_and_preserves_future_event_order():
    from fortune.replay_state import clone_sweep

    source = FortuneSweep(random_sites(30, 5), debug=True).start()
    for _ in range(24):
        source.step()
    before = signature(source)
    heap = tuple(source.queue._heap)
    cloned, _ = clone_sweep(source)
    assert signature(cloned) == before
    assert cloned.beach.root is not source.beach.root
    assert all(a is not b for a, b in zip(source.beach, cloned.beach))
    cloned.run()
    assert signature(source) == before and tuple(source.queue._heap) == heap
    source.run()
    assert signature(source) == signature(cloned)


def test_scrub_checkpoints_remain_bounded_and_are_not_mutated_by_restoring():
    replay = SweepReplay(random_sites(90, 12), Box(0, 0, 1, 1), debug=True)
    replay.seek(1)
    originals = [signature(s[0]) for s in replay._checkpoints.values()]
    for position in (0.1, 0.8, 0.4, 0.9, 0.2, 0.6, 1.0):
        replay.seek(position)
    assert len(replay._checkpoints) <= 8
    assert [signature(s[0]) for s in replay._checkpoints.values()] == originals
