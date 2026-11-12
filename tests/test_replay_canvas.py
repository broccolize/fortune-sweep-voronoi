import json
import random
import shutil
import subprocess

import pytest

from fortune.geometry import Box, Point, breakpoint_x, parabola_y
from fortune.io import random_sites
from fortune.replay import SweepReplay, stale
from fortune.replay_canvas import build_payload, launch, write_replay


@pytest.mark.parametrize("seed", range(5))
def test_canvas_snapshots_are_exact_records_of_the_python_engine(seed):
    points = random_sites(12, seed)
    payload, _ = build_payload(points, Box(0, 0, 1, 1))
    expected = SweepReplay(points, Box(0, 0, 1, 1), debug=True)
    for i, state in enumerate(payload["states"]):
        if i:
            expected.step_event()
        assert state["arcs"] == [arc.site for arc in expected.sweep.beach]
        assert state["counts"] == [
            expected.sweep.statistics[k]
            for k in ("site_events", "circle_events", "stale_events")
        ]
        assert state["queued"] == len(expected.sweep.queue)
        assert [invalid for _, invalid in state["queue"]] == [
            stale(e) for e in expected.sweep.queue.preview(8)
        ]
    assert expected.done
    assert len(payload["vertices"]) == len(expected.sweep.vertices)
    assert [s["y"] for s in payload["states"]] == sorted(
        (s["y"] for s in payload["states"]), reverse=True
    )
    json.dumps(payload, allow_nan=False)


@pytest.mark.parametrize(
    "points",
    [
        [(0, 0)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 0), (0, 1), (0, 2)],
        [(0, 0), (1, 2), (2, 4)],
        [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
    ],
)
def test_canvas_minimal_collinear_cocircular_and_duplicate_inputs(points):
    data, model = build_payload(points)
    assert data["states"][-1]["done"] and data["cells"]
    assert len(data["sites"]) == len(set(points))
    assert data["special_case"] == model.special_case
    if len(set(points)) == 4:
        assert data["sites"][0][2] == "0/4"


def test_canvas_export_is_self_contained_and_launch_opens_only_the_local_file(
    monkeypatch, tmp_path
):
    path = tmp_path / "replay.html"
    replay = write_replay(random_sites(8, 4), Box(0, 0, 1, 1), path)
    text = path.read_text(encoding="utf-8")
    assert "__FORTUNE_" not in text
    assert "<script src=" not in text and "https://" not in text
    assert "pointermove" in text and "requestAnimationFrame" in text
    opened = []
    monkeypatch.setattr(
        "fortune.replay_canvas.webbrowser.open", lambda url: opened.append(url)
    )
    launch(random_sites(4, 2), output=path)
    assert opened == [replay.path.as_uri()]


def test_browser_presentation_geometry_matches_python():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is only needed for the JavaScript presentation cross-check")
    import fortune.replay_canvas as canvas

    script = str(canvas.Path(canvas.__file__).with_suffix(".js"))
    # The JS file is a renderer, not a second Fortune implementation.
    rng = random.Random(47)
    cases = []
    for _ in range(100):
        a, b = Point(rng.random(), rng.random()), Point(rng.random(), rng.random())
        d = min(a.y, b.y) - rng.uniform(0.01, 1)
        cases.append(([a.x, a.y], [b.x, b.y], d))
    command = """
const f = require(process.argv[1]);
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
console.log(JSON.stringify(cases.map(([a,b,d]) => [
  f.breakpointX(a,b,d), f.parabolaY(a,.31,d)
])));
"""
    result = subprocess.run(
        [node, "-e", command, script],
        input=json.dumps(cases),
        text=True,
        capture_output=True,
        check=True,
    )
    for (a, b, d), (x, y) in zip(cases, json.loads(result.stdout)):
        assert x == pytest.approx(
            breakpoint_x(Point(*a), Point(*b), d), rel=1e-11, abs=1e-12
        )
        assert y == pytest.approx(parabola_y(Point(*a), 0.31, d), rel=1e-11, abs=1e-12)


def test_canvas_pointer_follows_without_a_mouse_button():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is only needed for the Canvas event test")
    from pathlib import Path

    import fortune.replay_canvas as canvas

    payload, _ = build_payload(random_sites(8, 3), Box(0, 0, 1, 1))
    result = subprocess.run(
        [node, str(Path(__file__).with_name("canvas_pointer_check.js"))],
        input=json.dumps(
            {
                "payload": payload,
                "script": str(Path(canvas.__file__).with_suffix(".js")),
            }
        ),
        text=True,
        capture_output=True,
        check=True,
    )
    values = json.loads(result.stdout)
    assert values["first"]["follow"] and values["second"]["follow"]
    assert values["first"]["worldY"] == pytest.approx(0.9)
    assert values["second"]["worldY"] == pytest.approx(0.2)
    assert values["second"]["index"] > values["first"]["index"]
