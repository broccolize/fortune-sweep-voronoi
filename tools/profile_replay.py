"""Reproduce replay rendering CPU measurements; these are not desktop FPS."""
# ruff: noqa: E402

import argparse
import cProfile
import io
import json
import platform
import pstats
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from fortune.geometry import Box
from fortune.io import random_sites
from fortune.replay import SweepReplay
from fortune.replay_view import PANEL_RECT, PLOT_RECT, ReplayController


def make_controller(n, *, comparison_rects=False):
    fig = Figure(figsize=(12, 7))
    FigureCanvasAgg(fig)
    plot = (0.07, 0.22, 0.58, 0.69) if comparison_rects else PLOT_RECT
    panel = (0.71, 0.25, 0.27, 0.64) if comparison_rects else PANEL_RECT
    return ReplayController(
        fig,
        fig.add_axes(plot),
        fig.add_axes(panel),
        SweepReplay(random_sites(n, 2026), Box(0, 0, 1, 1)),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results/animation-preview/render-after.json",
    )
    args = parser.parse_args()
    profiler = cProfile.Profile()
    rows = []
    for n in (9, 50):
        ui = make_controller(n, comparison_rects=True)
        ui.redraw()
        geometry = []
        paint = []
        for _ in range(48):
            start = time.perf_counter()
            ui.model.tick(5)
            geometry.append(time.perf_counter() - start)
            start = time.perf_counter()
            if n == 9:
                profiler.enable()
            ui.redraw()
            if n == 9:
                profiler.disable()
            paint.append(time.perf_counter() - start)
        rows.append(
            dict(
                sites=n,
                frames=48,
                median_geometry_ms=1000 * statistics.median(geometry),
                median_redraw_ms=1000 * statistics.median(paint),
                p95_redraw_ms=1000 * sorted(paint)[45],
                median_frame_ms=1000
                * statistics.median([a + b for a, b in zip(geometry, paint)]),
            )
        )
        ui.close()
    scrub = []
    for n in (9, 50, 200):
        ui = make_controller(n)
        samples = []
        for position in (70, 20, 85, 35, 90, 45, 95, 60, 30, 80):
            start = time.perf_counter()
            ui.position.set_val(position)
            samples.append(time.perf_counter() - start)
        scrub.append(
            dict(
                sites=n,
                samples=len(samples),
                median_ms=1000 * statistics.median(samples),
                max_ms=1000 * max(samples),
            )
        )
        ui.close()
    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats(
        "cumulative"
    ).print_stats(20)
    result = dict(
        actual_timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        python=sys.version,
        platform=platform.platform(),
        scope="Same 1200x700 Agg canvas, inputs, 48-frame sequence and axes geometry as render-before.json; CPU rendering, not end-to-end desktop FPS. Nine-site measurements include cProfile overhead in both versions; 50-site measurements are unprofiled.",
        results=rows,
        position_scrubbing=scrub,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    args.output.with_suffix(".profile.txt").write_text(
        stream.getvalue(), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
