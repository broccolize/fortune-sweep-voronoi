"""Responsive playback, direct sweep dragging and position scrubbing."""

from pathlib import Path
from time import perf_counter

from .io import ensure_parent
from .replay import SweepReplay
from .replay_artists import CachedPainter, ReplayArtists, event_name
from .ui_text import replace_widget_text, ui_text

PLOT_RECT = (0.07, 0.30, 0.58, 0.60)
PANEL_RECT = (0.71, 0.31, 0.27, 0.58)


def draw_replay(model, axes, panel, *, labels=True):
    """Update persistent artists; also usable by headless frame/GIF exports."""
    scene = getattr(axes, "_fortune_replay_artists", None)
    if scene is None or scene.panel is not panel or scene.diagram is not model.diagram:
        scene = ReplayArtists(model, axes, panel, labels=labels)
        axes._fortune_replay_artists = scene
    scene.update(model)
    return scene


class ReplayController:
    def __init__(
        self,
        figure,
        axes,
        panel,
        model,
        *,
        output="replay.png",
        labels=True,
        clock=None,
    ):
        from matplotlib.widgets import Button, Slider

        self.figure, self.axes, self.panel, self.model = figure, axes, panel, model
        self.output, self.labels = Path(output), labels
        self.playing = self.closed = self._dragging = False
        self._clock = clock or perf_counter
        self._last_tick = self._clock()
        self._scene = self._painter = None
        self._paint_revision = None
        self.timer = figure.canvas.new_timer(interval=16)
        self.timer.add_callback(self.tick)
        self.status = ui_text(figure, 0.07, 0.025, "", fontsize=9, color="#344054")
        self.buttons = []
        for x, width, label, callback in (
            (0.07, 0.12, "Play", self.toggle_play),
            (0.21, 0.12, "Next event", self.next_event),
            (0.35, 0.12, "Reset", self.reset),
            (0.49, 0.14, "Save frame", self.save_frame),
        ):
            button = Button(
                figure.add_axes([x, 0.075, width, 0.045]), label, useblit=False
            )
            button.label = replace_widget_text(button.ax, button.label)
            button.drawon = False
            button.hovercolor = button.color
            button.on_clicked(callback)
            self.buttons.append(button)
        self.speed = Slider(
            figure.add_axes([0.76, 0.09, 0.18, 0.02]),
            "Events/s",
            0.5,
            30,
            valinit=6,
            valstep=0.5,
        )
        self.speed.label = replace_widget_text(self.speed.ax, self.speed.label)
        self.speed.valtext = replace_widget_text(self.speed.ax, self.speed.valtext)
        self.speed.drawon = False
        self.speed.on_changed(self.speed_changed)
        self.position = Slider(
            figure.add_axes([0.14, 0.15, 0.48, 0.022]),
            "Position",
            0,
            100,
            valinit=100 * model.position,
            valfmt="%1.0f%%",
        )
        self.position.label = replace_widget_text(self.position.ax, self.position.label)
        self.position.valtext = replace_widget_text(
            self.position.ax, self.position.valtext
        )
        self.position.drawon = False
        self.position.set_active(not model.special_case)
        self.position.on_changed(self.scrub)
        for name, callback in (
            ("key_press_event", self.key),
            ("close_event", self.close),
            ("button_press_event", self.press),
            ("motion_notify_event", self.motion),
            ("button_release_event", self.release),
        ):
            self.figure.canvas.mpl_connect(name, callback)
        self.redraw()

    def redraw(self, message=None, *, controls_changed=False):
        if self.closed:
            return
        try:
            self._scene = draw_replay(
                self.model, self.axes, self.panel, labels=self.labels
            )
        except (ValueError, ArithmeticError) as exc:
            self.pause()
            if self._scene:
                self._scene.hide_geometry()
            message = f"Replay drawing stopped: {exc}"
        if message is None:
            if self.model.special_case:
                message = "Collinear input: direct-bisector construction shown. Choose non-collinear sites to replay the sweep."
            elif self.model.done:
                message = f"Complete: {self.model.event_count} entries processed. Drag Position backward or Play to replay."
            elif self.model.last_event:
                message = f"Event {self.model.event_count}: {event_name(self.model, self.model.last_event)}"
                if self.model.last_stale:
                    message += " | stale prediction discarded"
                message += " | Drag the plot or Position; Space: play/pause; Right: next event."
            else:
                message = "Play or drag the plot / Position slider. Right: next event; R: reset."
        dirty = controls_changed or message != self.status.get_text()
        self.status.set_text(message)
        label = "Pause" if self.playing else "Play"
        dirty |= label != self.buttons[0].label.get_text()
        self.buttons[0].label.set_text(label)
        events = self.position.eventson
        self.position.eventson = False
        self.position.set_val(100 * self.model.position)
        self.position.eventson = events
        if self._scene is None:
            self.figure.canvas.draw_idle()
            return
        if self._painter is None:
            self._painter = CachedPainter(
                self.figure,
                self._scene.event_artists
                + [self.status, self.speed.ax]
                + [b.ax for b in self.buttons],
                self._scene.motion_artists + [self.position.ax],
                motion_regions=self.movement_regions,
            )
        dirty |= self._paint_revision != self._scene.revision
        self._painter.paint(event_dirty=dirty)
        self._paint_revision = self._scene.revision

    def movement_regions(self):
        from matplotlib.transforms import Bbox

        # Avoid copying the full Tk PhotoImage when only these regions move.
        scale = self.figure.dpi / 100
        slider = self.position.ax.bbox
        panel = self.panel.bbox
        baseline = panel.y0 + 0.055 * panel.height
        return (
            self.axes.bbox.padded(4 * scale),
            Bbox.from_extents(
                slider.x0 - 100 * scale,
                slider.y0 - 15 * scale,
                slider.x1 + 70 * scale,
                slider.y1 + 20 * scale,
            ),
            Bbox.from_extents(
                panel.x0 - 3 * scale,
                baseline - 10 * scale,
                panel.x1 + 3 * scale,
                baseline + 22 * scale,
            ),
        )

    def pause(self):
        self.playing = False
        self.timer.stop()

    def toggle_play(self, event=None):
        if self.model.special_case or self.closed:
            return
        if self.playing:
            self.pause()
        else:
            if self.model.done:
                self.model.reset()
            self.playing = True
            self._last_tick = self._clock()
            self.timer.start()
        self.redraw()

    def next_event(self, event=None):
        self.pause()
        try:
            self.model.step_event()
            self.redraw()
        except (ValueError, ArithmeticError) as exc:
            self.redraw(f"Replay stopped: {exc}")

    def tick(self):
        # Returning False would remove this callback from Matplotlib's timer.
        if not self.playing or self.closed:
            return
        now = self._clock()
        elapsed = min(0.25, max(0.0, now - self._last_tick))
        self._last_tick = now
        frame_started = perf_counter()
        try:
            self.model.advance(elapsed * self.speed.val)
            if self.model.done:
                self.pause()
            self.redraw()
        except (ValueError, ArithmeticError) as exc:
            self.pause()
            self.redraw(f"Replay stopped: {exc}")
        # Tk schedules its next callback after this one returns. Subtract the
        # drawing time instead of adding a fixed 16 ms delay to every frame.
        self.timer.interval = max(
            1, round(1000 / 60 - (perf_counter() - frame_started) * 1000)
        )

    def speed_changed(self, value):
        self._last_tick = self._clock()
        self.redraw(controls_changed=True)

    def scrub(self, value):
        self.pause()
        try:
            self.model.seek(float(value) / 100)
            self.redraw()
        except (ValueError, ArithmeticError) as exc:
            self.redraw(f"Replay stopped: {exc}")

    def _drag_y(self, value):
        self.pause()
        try:
            self.model.seek_y(min(self.model.top_y, max(self.model.bottom_y, value)))
            self.redraw()
        except (ValueError, ArithmeticError) as exc:
            self.redraw(f"Replay stopped: {exc}")

    def press(self, event):
        if (
            event.inaxes is self.axes
            and event.button == 1
            and event.ydata is not None
            and not self.model.special_case
            and self.axes.get_navigate_mode() is None
        ):
            self._dragging = True
            self._drag_y(event.ydata)

    def motion(self, event):
        if self._dragging and event.inaxes is self.axes and event.ydata is not None:
            self._drag_y(event.ydata)

    def release(self, event):
        if self._dragging and event.inaxes is self.axes and event.ydata is not None:
            self._drag_y(event.ydata)
        self._dragging = False

    def reset(self, event=None):
        self.pause()
        self.model.reset()
        self.redraw()

    def save_frame(self, event=None):
        try:
            if self._painter:
                with self._painter.full_render():
                    self.figure.savefig(ensure_parent(self.output), dpi=160)
            else:
                self.figure.savefig(ensure_parent(self.output), dpi=160)
            self.redraw(f"Saved current replay frame: {self.output.name}")
        except (OSError, ValueError) as exc:
            self.redraw(f"Could not save frame: {exc}")

    def key(self, event):
        if event.key in (" ", "space"):
            self.toggle_play()
        elif event.key == "right":
            self.next_event()
        elif event.key == "r":
            self.reset()

    def close(self, event=None):
        self.pause()
        self.closed = True
        if self._painter:
            self._painter.close()


def launch(sites, box=None, output="replay.png", *, block=True, labels=True):
    import matplotlib.pyplot as plt

    model = SweepReplay(sites, box)
    fig = plt.figure(figsize=(12, 7))
    fig.canvas.manager.set_window_title("Fortune sweep replay | smooth controls")
    axes = fig.add_axes(PLOT_RECT)
    panel = fig.add_axes(PANEL_RECT)
    controller = ReplayController(fig, axes, panel, model, output=output, labels=labels)
    fig.fortune_replay = controller
    plt.show(block=block)
    return controller
