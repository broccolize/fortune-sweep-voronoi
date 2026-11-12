"""Measure the actual Tk playback timer and canvas on this desktop."""
# ruff: noqa: E402

import json
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from fortune.geometry import Box
from fortune.io import random_sites
from fortune.replay_view import launch


def main():
    ui = launch(
        random_sites(50, 2026),
        Box(0, 0, 1, 1),
        ROOT / "examples/sweep-replay-live.png",
        block=False,
    )
    starts = []
    draws = []
    ui.timer.remove_callback(ui.tick)

    def measured_tick():
        start = time.perf_counter()
        ui.tick()
        draws.append(time.perf_counter() - start)
        starts.append(start)

    ui.timer.add_callback(measured_tick)
    root = ui.figure.canvas.get_tk_widget().winfo_toplevel()
    result = {}

    def finish():
        ui.pause()
        intervals = [b - a for a, b in zip(starts, starts[1:])]
        if intervals:
            result.update(
                actual_timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
                sites=50,
                backend=matplotlib.get_backend(),
                callbacks=len(starts),
                observed_window_seconds=8.0,
                median_callback_interval_ms=1000 * statistics.median(intervals),
                median_callback_rate_hz=1 / statistics.median(intervals),
                median_tick_render_ms=1000 * statistics.median(draws),
                p95_tick_render_ms=1000 * sorted(draws)[int(0.95 * (len(draws) - 1))],
                scope="Actual visible Tk window, timer callbacks and blit submission; not a measurement of display scanout.",
                event_count=ui.model.event_count,
            )
            ui.save_frame()
        ui.close()
        plt.close(ui.figure)

    root.after(250, ui.toggle_play)
    root.after(8250, finish)
    plt.show()
    if not result:
        raise RuntimeError(
            "Native playback was interrupted before measurements completed"
        )
    (ROOT / "results/animation-preview/render-tk.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
