import itertools

import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
from validation import validate_cells

from fortune.cli import main
from fortune.diagram import construct
from fortune.geometry import Box, Point, orient
from fortune.interactive import InteractiveController
from fortune.visualize import draw


def _coordinate_edges(diagram):
    return {
        frozenset(diagram.sites[i] for i in edge) for edge in diagram.delaunay_edges
    }


def test_full_dual_is_retained_when_box_hides_voronoi_edges():
    d = construct([(0, 0), (2, 0), (0, 2)], Box(-0.1, -0.1, 0.1, 0.1))
    assert len(d.edges) == 0
    assert d.delaunay_edges == [(0, 1), (0, 2), (1, 2)]


def test_cocircular_triangulation_is_deterministic_and_has_one_diagonal():
    points = [(0, 0), (1, 0), (1, 1), (0, 1)]
    expected = _coordinate_edges(construct(points))
    for order in itertools.permutations(points):
        d = construct(order)
        assert len(d.delaunay_edges) == 5
        assert _coordinate_edges(d) == expected
    assert frozenset((Point(0, 0), Point(1, 1))) in expected
    assert frozenset((Point(0, 1), Point(1, 0))) not in expected


def test_cocircular_fan_is_planar_and_complete():
    ring = [
        (5, 0),
        (4, 3),
        (3, 4),
        (0, 5),
        (-3, 4),
        (-4, 3),
        (-5, 0),
        (-4, -3),
        (-3, -4),
        (0, -5),
        (3, -4),
        (4, -3),
    ]
    d = construct(ring)
    assert len(d.delaunay_edges) == 2 * len(ring) - 3
    for first, second in itertools.combinations(d.delaunay_edges, 2):
        if set(first) & set(second):
            continue
        a, b = (d.sites[i] for i in first)
        c, e = (d.sites[i] for i in second)
        assert not (
            orient(a, b, c) * orient(a, b, e) < 0
            and orient(c, e, a) * orient(c, e, b) < 0
        )


@pytest.mark.parametrize(
    "points,count",
    [([(0, 0)], 0), ([(0, 0), (1, 1)], 1), ([(i, 0) for i in range(5)], 4)],
)
def test_degenerate_dual_is_a_consecutive_chain(points, count):
    assert len(construct(points).delaunay_edges) == count


def test_nonunit_interactive_input_infers_bounds_and_toggles_overlay(tmp_path):
    fig = Figure()
    FigureCanvasAgg(fig)
    axes = fig.subplots()
    points = [Point(100, 100), Point(101, 100), Point(100, 101)]
    ui = InteractiveController(fig, axes, points, output=str(tmp_path / "ui.png"))
    assert axes.get_xlim() == pytest.approx((99.9, 101.1))
    assert axes.get_ylim() == pytest.approx((99.9, 101.1))
    ui.compute()
    assert ui.diagram is not None and all(c.vertices for c in ui.diagram.cells)
    validate_cells(ui.diagram)
    assert not any(isinstance(c, LineCollection) for c in axes.collections)
    ui.toggle_delaunay()
    lines = [c for c in axes.collections if isinstance(c, LineCollection)]
    assert len(lines) == 1 and len(lines[0].get_segments()) == 3
    ui.export()
    assert (tmp_path / "ui.json").is_file()
    ui.toggle_delaunay()
    assert axes.get_legend() is None


def test_empty_interactive_canvas_and_explicit_bounds_are_preserved():
    fig = Figure()
    FigureCanvasAgg(fig)
    axes = fig.subplots()
    assert InteractiveController(fig, axes).box == Box(0, 0, 1, 1)
    bounds = Box(-2, -3, 2, 3)
    assert InteractiveController(fig, axes, [(100, 100)], bounds).box == bounds


def test_interactive_cli_file_and_real_checkbox(monkeypatch, tmp_path):
    import matplotlib.pyplot as plt

    from fortune import interactive

    source = tmp_path / "nonunit.txt"
    source.write_text("100 100\n101 100\n100 101\n")
    original_launch = interactive.launch
    controllers = []

    def launch(*args, **kwargs):
        controller = original_launch(*args, **kwargs)
        controllers.append(controller)
        return controller

    monkeypatch.setattr(plt, "show", lambda: None)
    monkeypatch.setattr(interactive, "launch", launch)
    assert main(["--interactive", "--input", str(source), "--delaunay"]) == 0
    controller = controllers[0]
    controller.compute()
    assert controller.diagram is not None
    assert controller.box == controller.diagram.box == Box(99.9, 99.9, 101.1, 101.1)
    assert controller.delaunay and controller.dual_control.get_status() == [True]
    controller.dual_control.set_active(0)
    assert not controller.delaunay
    assert not any(isinstance(c, LineCollection) for c in controller.axes.collections)
    plt.close(controller.figure)


def test_delaunay_batch_cli_writes_overlay_and_export(tmp_path, capsys):
    import json

    image, output = tmp_path / "dual.png", tmp_path / "dual.json"
    assert (
        main(
            [
                "--random",
                "12",
                "--delaunay",
                "--output",
                str(image),
                "--json",
                str(output),
            ]
        )
        == 0
    )
    payload = json.loads(output.read_text())
    assert payload["delaunay_edges"]
    assert image.read_bytes().startswith(b"\x89PNG")
    assert json.loads(capsys.readouterr().out)["delaunay_edges"] == len(
        payload["delaunay_edges"]
    )


def test_drawing_removes_overlay_when_disabled():
    fig = Figure()
    axes = fig.subplots()
    d = construct([(0, 0), (1, 0), (0, 1)])
    draw(d, axes, delaunay=True)
    assert axes.get_legend() is not None
    draw(d, axes)
    assert axes.get_legend() is None
    assert not any(isinstance(c, LineCollection) for c in axes.collections)
