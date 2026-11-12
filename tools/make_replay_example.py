"""Generate a real replay frame and optional GIF for reviewing the feature branch."""
# ruff: noqa: E402

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from PIL import Image

from fortune.geometry import Box
from fortune.io import read_sites
from fortune.replay import SweepReplay
from fortune.replay_view import PANEL_RECT, PLOT_RECT, draw_replay


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "examples/sites.txt")
    parser.add_argument(
        "--gif", action="store_true", help="Also write the offline GIF preview"
    )
    args = parser.parse_args()
    model = SweepReplay(read_sites(args.input), Box(0, 0, 1, 1))
    fig = Figure(figsize=(12, 7), dpi=80)
    canvas = FigureCanvasAgg(fig)
    axes = fig.add_axes(PLOT_RECT)
    panel = fig.add_axes(PANEL_RECT)
    status = fig.text(
        0.07,
        0.05,
        "Program-generated replay preview | same event engine as the app",
        fontsize=10,
    )
    frames = []
    selected = None
    png = ROOT / "examples/sweep-replay.png"
    gif = ROOT / "examples/sweep-replay.gif"

    def render_frame():
        draw_replay(model, axes, panel)
        status.set_text(
            f"Replay | {model.event_count} heap entries processed | sweep y = {model.sweep_y:.4g}"
        )
        if args.gif:
            canvas.draw()
            im = Image.frombuffer(
                "RGBA",
                canvas.get_width_height(),
                canvas.buffer_rgba(),
                "raw",
                "RGBA",
                0,
                1,
            )
            frames.append(
                im.convert("RGB").convert(
                    "P", palette=Image.Palette.ADAPTIVE, colors=192
                )
            )

    render_frame()
    while not model.done:
        event = model.tick(2)
        render_frame()
        if (
            selected is None
            and event
            and event.kind == 1
            and not model.last_stale
            and not model.done
        ):
            fig.savefig(png, dpi=160)
            selected = dict(
                event_count=model.event_count,
                site_events=model.sweep.statistics["site_events"],
                circle_events=model.sweep.statistics["circle_events"],
                sweep_y=model.sweep_y,
            )
    if selected is None:
        fig.savefig(png, dpi=160)
    if args.gif:
        durations = [180] * len(frames)
        durations[0] = 700
        durations[-1] = 1500
        frames[0].save(
            gif, save_all=True, append_images=frames[1:], duration=durations, loop=0
        )
    meta = dict(
        actual_timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        input=str(args.input.relative_to(ROOT))
        if args.input.is_relative_to(ROOT)
        else args.input.name,
        generated_by="tools/make_replay_example.py using actual SweepReplay state",
        png="examples/sweep-replay.png",
        selected_frame=selected,
        gif="examples/sweep-replay.gif" if args.gif else None,
        frames=len(frames),
    )
    (ROOT / "evidence/animation-preview.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
