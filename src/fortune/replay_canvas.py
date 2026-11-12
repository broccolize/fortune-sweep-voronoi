"""Export an offline, pointer-following Canvas replay of real Python events.

Fortune construction stays in Python. The browser receives immutable event
states and draws their parabolas; pointer movement makes no Python calls.
This bounded educational replay may store O(n^2) arc/queue snapshot data at
the 200-site cap. Normal construction and its benchmarks do not collect it.
"""

import heapq
import json
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .geometry import Point
from .replay import SweepReplay, stale


def build_payload(coordinates, box=None, *, labels=True):
    model = SweepReplay(coordinates, box)
    engine = model.sweep
    events = {}
    edges = {}
    states = []

    def capture(step, last=None, discarded=False):
        for entry in engine.queue._heap:
            serial, event = entry[3], entry[-1]
            if serial not in events:
                events[serial] = dict(
                    kind=event.kind,
                    y=event.y,
                    x=event.x,
                    site=event.site,
                    defining=event.defining,
                    centre=[event.centre.x, event.centre.y] if event.centre else None,
                )
        for key, edge in engine.edges.items():
            record = edges.setdefault(key, dict(sites=list(key), created=step, ends=[]))
            for vertex in edge.vertices:
                if not any(end[0] == vertex for end in record["ends"]):
                    record["ends"].append([vertex, step])
        states.append(
            dict(
                y=engine.sweep_y if step else model.normalize(Point(0, model.top_y)).y,
                arcs=[arc.site for arc in engine.beach],
                queue=[
                    [e[3], stale(e[-1])] for e in heapq.nsmallest(8, engine.queue._heap)
                ],
                queued=len(engine.queue),
                last=last,
                discarded=discarded,
                counts=[
                    engine.statistics["site_events"],
                    engine.statistics["circle_events"],
                    engine.statistics["stale_events"],
                ],
                done=not bool(engine.queue),
            )
        )

    capture(0)
    step = 0
    while engine.queue:
        serial = engine.queue._heap[0][3]
        before = engine.statistics["stale_events"]
        model.step_event()
        step += 1
        capture(step, serial, engine.statistics["stale_events"] > before)
    view = model.view
    span = max(view.xmax - view.xmin, view.ymax - view.ymin)
    left = model.normalize(Point(view.xmin - 0.1 * span, view.ymin - 0.1 * span))
    right = model.normalize(Point(view.xmax + 0.1 * span, view.ymax + 0.1 * span))
    b = model.box
    low = model.normalize(Point(b.xmin, b.ymin))
    high = model.normalize(Point(b.xmax, b.ymax))
    payload = dict(
        generated_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        source="Python FortuneSweep.step; no browser Voronoi implementation",
        sites=[[p.x, p.y, model.label(i)] for i, p in enumerate(model.points)],
        vertices=[[v.point.x, v.point.y] for v in engine.vertices],
        edges=list(edges.values()),
        events={str(k): v for k, v in events.items()},
        states=states,
        cells=[
            [[model.normalize(p).x, model.normalize(p).y] for p in c.vertices]
            for c in model.diagram.cells
        ],
        view=[left.x, left.y, right.x, right.y],
        box=[low.x, low.y, high.x, high.y],
        world=[model.ox, model.oy, model.scale],
        labels=labels,
        special_case=model.special_case,
    )
    return payload, model


def write_replay(coordinates, box=None, output="replay.html", *, labels=True):
    payload, model = build_payload(coordinates, box, labels=labels)
    folder = Path(__file__).parent
    template = (folder / "replay_canvas.html").read_text(encoding="utf-8")
    script = (folder / "replay_canvas.js").read_text(encoding="utf-8")
    data = json.dumps(
        payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    )
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    html = template.replace("__FORTUNE_DATA__", data).replace(
        "__FORTUNE_SCRIPT__", script
    )
    path = Path(output).with_suffix(".html")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return CanvasReplay(path.resolve(), model)


@dataclass
class CanvasReplay:
    path: Path
    model: SweepReplay


def launch(
    sites,
    box=None,
    output="replay.html",
    *,
    block=False,
    labels=True,
    open_browser=True,
):
    replay = write_replay(sites, box, output, labels=labels)
    if open_browser:
        webbrowser.open(replay.path.as_uri())
    return replay
