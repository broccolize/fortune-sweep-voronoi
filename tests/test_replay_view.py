from types import SimpleNamespace

import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle

from fortune.cli import main
from fortune.geometry import Box, Point
from fortune.interactive import InteractiveController
from fortune.io import random_sites
from fortune.replay import SweepReplay
from fortune.replay_view import PANEL_RECT, PLOT_RECT, ReplayController, draw_replay


def controller(monkeypatch, tmp_path, points=None):
    fig = Figure(figsize=(12, 7))
    FigureCanvasAgg(fig)
    # GUI coalesces draw_idle calls. Headless callbacks are checked without
    # synchronously rasterizing every intermediate frame during these tests.
    monkeypatch.setattr(fig.canvas, "draw_idle", lambda: None)
    axes = fig.add_axes(PLOT_RECT)
    panel = fig.add_axes(PANEL_RECT)
    model = SweepReplay(points or random_sites(8, 24), Box(0, 0, 1, 1))
    clock = SimpleNamespace(now=0.0)
    ui = ReplayController(
        fig, axes, panel, model, output=tmp_path / "frame.png", clock=lambda: clock.now
    )
    ui.test_clock = clock
    return ui


def test_play_pause_step_reset_keyboard_and_real_frame_export(monkeypatch, tmp_path):
    ui = controller(monkeypatch, tmp_path)
    assert not ui.playing and ui.model.event_count == 0
    ui.next_event()
    assert ui.model.event_count == 1 and not ui.playing
    ui.key(SimpleNamespace(key=" "))
    assert ui.playing
    for _ in range(13):
        ui.test_clock.now += 0.05
        ui.tick()
    assert ui.model.event_count >= 2
    ui.key(SimpleNamespace(key="right"))
    assert not ui.playing
    ui.save_frame()
    assert (tmp_path / "frame.png").read_bytes().startswith(b"\x89PNG")
    assert "Saved current replay frame" in ui.status.get_text()
    ui.key(SimpleNamespace(key="r"))
    assert ui.model.event_count == 0 and not ui.model.processed
    ui.toggle_play()
    ui.close()
    assert not ui.playing and ui.closed
    ui.tick()
    assert ui.model.event_count == 0


def test_complete_replay_restarts_and_collinear_input_is_explicit(
    monkeypatch, tmp_path
):
    ui = controller(monkeypatch, tmp_path)
    while not ui.model.done:
        ui.model.step_event()
    ui.redraw()
    assert "Complete" in ui.status.get_text()
    ui.toggle_play()
    assert ui.playing and ui.model.event_count == 0
    ui.close()
    line = controller(
        monkeypatch, tmp_path, [Point(0, 0), Point(0.5, 0.5), Point(1, 1)]
    )
    line.toggle_play()
    assert not line.playing and line.model.done
    assert "Collinear" in line.status.get_text()
    assert any("No beach-line sweep" in t.get_text() for t in line.panel.texts)


def test_last_valid_circle_stays_visible_and_stale_queue_is_labelled(
    monkeypatch, tmp_path
):
    ui = controller(monkeypatch, tmp_path)
    for _ in range(100):
        ui.model.step_event()
        e = ui.model.last_event
        if e.kind == 1 and not ui.model.last_stale and not ui.model.done:
            break
    else:
        pytest.fail("Expected an intermediate valid circle event")
    draw_replay(ui.model, ui.axes, ui.panel)
    assert any(isinstance(p, Circle) and p.get_visible() for p in ui.axes.patches)
    # Old predictions deliberately remain in the heap and are identified.
    while not ui.model.done:
        ui.redraw()
        if any(
            "[stale]" in t.get_text() and "Circle" in t.get_text()
            for t in ui.panel.texts
        ):
            break
        ui.model.step_event()
    else:
        pytest.fail("Expected stale entries in the queue view")


def test_drawing_failure_pauses_with_an_explicit_message(monkeypatch, tmp_path):
    ui = controller(monkeypatch, tmp_path)

    def fail():
        raise ArithmeticError("test precision limit")

    monkeypatch.setattr(ui.model, "curves", fail)
    ui.toggle_play()
    assert not ui.playing
    assert "Replay drawing stopped: test precision limit" == ui.status.get_text()


def test_cli_animate_uses_seeded_sites_and_rejects_ambiguous_modes(
    monkeypatch, tmp_path
):
    calls = []

    def launch(sites, box, output, **kwargs):
        calls.append((sites, box, output, kwargs))

    monkeypatch.setattr("fortune.replay_view.launch", launch)
    monkeypatch.setattr("fortune.replay_canvas.launch", launch)
    assert main(["--animate"]) == 0
    assert calls[0][0] == random_sites(8, 2026) and calls[0][1] == Box(0, 0, 1, 1)
    assert (
        main(
            [
                "--animate",
                "--random",
                "3",
                "--seed",
                "4",
                "--no-labels",
                "--output",
                str(tmp_path / "frame.svg"),
            ]
        )
        == 0
    )
    assert calls[-1][0] == random_sites(3, 4) and not calls[-1][3]["labels"]
    with pytest.raises(SystemExit):
        main(["--animate", "--interactive"])
    with pytest.raises(SystemExit):
        main(["--animate", "--csv", "bad.csv"])


def test_animate_button_copies_input_without_modifying_the_current_diagram(
    monkeypatch, tmp_path
):
    fig = Figure()
    FigureCanvasAgg(fig)
    monkeypatch.setattr(fig.canvas, "draw_idle", lambda: None)
    parent = InteractiveController(
        fig, fig.subplots(), output=str(tmp_path / "result.png")
    )
    parent.animate()
    assert "Add at least one" in parent.status.get_text()
    parent.sites = [Point(0.1, 0.1), Point(0.8, 0.2), Point(0.4, 0.9)]
    parent.compute()
    diagram = parent.diagram
    calls = []

    def launch(sites, box, output, **kwargs):
        calls.append((output, kwargs))
        return SimpleNamespace(model=SweepReplay(sites, box))

    monkeypatch.setattr("fortune.replay_canvas.launch", launch)
    parent.animate()
    assert parent.diagram is diagram and len(parent.replays) == 1
    assert calls[0][0].name == "result-replay.html" and calls[0][1]["block"] is False
    parent.sites.append(Point(0.7, 0.7))
    assert len(parent.replays[0].model.sites) == 3


def test_movement_reuses_artists_and_does_not_redraw_the_figure(monkeypatch, tmp_path):
    ui = controller(monkeypatch, tmp_path)
    artists = tuple(ui.axes.get_children())
    panel = tuple(ui.panel.get_children())

    def forbidden(*args, **kwargs):
        raise AssertionError("Full redraw or axes reconstruction during movement")

    monkeypatch.setattr(ui.figure.canvas, "draw", forbidden)
    monkeypatch.setattr(ui.axes, "clear", forbidden)
    monkeypatch.setattr(ui.panel, "clear", forbidden)
    for _ in range(18):
        ui.model.tick(4)
        ui.redraw()
    assert tuple(ui.axes.get_children()) == artists
    assert tuple(ui.panel.get_children()) == panel


def test_position_slider_dragging_and_backward_seek(monkeypatch, tmp_path):
    ui = controller(monkeypatch, tmp_path)
    ui.position.set_val(75)
    count = ui.model.event_count
    assert count > 0 and not ui.playing
    ui.position.set_val(20)
    assert ui.model.event_count < count
    assert ui.model.position == pytest.approx(0.2)
    ui.press(SimpleNamespace(inaxes=ui.axes, button=1, ydata=0.6))
    ui.motion(SimpleNamespace(inaxes=ui.axes, ydata=0.4))
    ui.release(SimpleNamespace(inaxes=ui.axes, ydata=0.3))
    assert ui.model.sweep_y == pytest.approx(0.3) and not ui._dragging
    ui.position.set_val(100)
    assert ui.model.done
    ui.position.set_val(0)
    assert not ui.model.processed and ui.model.event_count == 0


def test_resize_cache_export_and_fallback_rendering(monkeypatch, tmp_path):
    ui = controller(monkeypatch, tmp_path)
    ui.model.seek(0.6)
    ui.redraw()
    ui.figure.set_size_inches(10, 6)
    ui.figure.canvas.draw()
    ui.model.tick(4)
    ui.redraw()
    ui.save_frame()
    assert (tmp_path / "frame.png").stat().st_size > 10000
    assert ui._painter.base is not None
    # Unsupported backends retain the same data using ordinary painting.
    ui.close()
    fig = Figure()
    FigureCanvasAgg(fig)
    monkeypatch.setattr(fig.canvas, "supports_blit", False)
    other = ReplayController(
        fig,
        fig.add_axes(PLOT_RECT),
        fig.add_axes(PANEL_RECT),
        SweepReplay(random_sites(4, 4)),
    )
    assert not other._painter.enabled
    other.next_event()
    assert other.model.event_count == 1
    other.close()


def test_fast_interface_text_keeps_svg_text_and_multiline_rendering(tmp_path):
    from matplotlib import rc_context

    from fortune.ui_text import _bitmap, ui_text

    fig = Figure(figsize=(5, 3))
    FigureCanvasAgg(fig)
    axes = fig.subplots()
    axes.set_axis_off()
    ui_text(axes, 0.1, 0.8, "Site 7\nstale: discard", fontsize=11, va="top")
    fig.canvas.draw()
    hits = _bitmap.cache_info().hits
    fig.canvas.draw()
    assert _bitmap.cache_info().hits > hits
    assert _bitmap.cache_info().maxsize == 256
    with rc_context({"svg.fonttype": "none"}):
        fig.savefig(tmp_path / "text.svg")
    content = (tmp_path / "text.svg").read_text(encoding="utf-8")
    assert "Site 7" in content and "stale: discard" in content
    assert "<image" not in content
