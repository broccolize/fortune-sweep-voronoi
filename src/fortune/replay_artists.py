"""Persistent replay artists and a cached-background painter.

Axes, labels and widgets are created once. Event text is painted only when the
event state changes; movement frames redraw geometry and the position control.
NumPy and Matplotlib are presentation dependencies, never construction code.
"""

import math
import textwrap
from contextlib import contextmanager

import numpy as np
from matplotlib import colormaps
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle

from .geometry import Point
from .replay import stale
from .ui_text import ui_text

SWEEP = "#b42369"
BEACH = "#e37b12"
EDGE = "#344054"
CIRCLE = "#087f8c"


def event_name(model, event):
    if event.kind == 0:
        return f"Site {model.label(event.site)}"
    return "Circle " + "/".join(model.label(i) for i in event.defining)


def offsets(points):
    return np.asarray([(p.x, p.y) for p in points], dtype=float).reshape(-1, 2)


class ReplayArtists:
    def __init__(self, model, axes, panel, *, labels=True):
        self.axes, self.panel = axes, panel
        self.diagram = model.diagram
        self.revision = None
        self.event_changed = True
        axes.clear()
        panel.clear()
        panel.set_axis_off()
        b, view = model.box, model.view
        self.span = max(view.xmax - view.xmin, view.ymax - view.ymin)
        pad = self.span * 0.06
        self.xlim = (view.xmin - pad, view.xmax + pad)
        self.ylim = (view.ymin - pad, view.ymax + pad)
        axes.set(xlim=self.xlim, ylim=self.ylim, xlabel="x", ylabel="y")
        axes.set_aspect("equal", adjustable="box")
        if labels:
            for i, p in enumerate(model.sites):
                axes.annotate(
                    model.label(i),
                    (p.x, p.y),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=8,
                    color=EDGE,
                )
        axes.legend(
            handles=[
                Line2D([], [], color=SWEEP, label="Sweep line"),
                Line2D([], [], color=BEACH, lw=2, label="Beach line"),
                Line2D([], [], color=EDGE, label="Traced edges"),
                Line2D([], [], color=CIRCLE, ls="--", label="Event circle"),
            ],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.13),
            ncol=4,
            fontsize=8,
            framealpha=0.95,
        )
        ui_text(
            panel, 0, 1, "EVENT QUEUE", fontsize=12, weight="bold", va="top", color=EDGE
        )
        ui_text(
            panel,
            0,
            0.94,
            "Highest y first; sites win ties",
            fontsize=9,
            color="#667085",
        )
        self.rows = [
            ui_text(
                panel, 0, 0.84 - i * 0.073, "", fontsize=8.5, va="top", linespacing=1.1
            )
            for i in range(8)
        ]
        ui_text(
            panel,
            0,
            0.9,
            "Gray [stale] entries will be skipped",
            fontsize=8,
            color="#667085",
        )
        self.queue_size = ui_text(panel, 0, 0.23, "", fontsize=8.5, color="#667085")
        self.statistics = ui_text(
            panel, 0, 0.17, "", fontsize=9, va="top", linespacing=1.5
        )
        self.height = ui_text(panel, 0, 0.055, "", fontsize=9, color=SWEEP)
        self.order = ui_text(
            panel, 0, -0.04, "", fontsize=9, va="top", linespacing=1.5, color=EDGE
        )
        self.special = ui_text(
            panel, 0, 0.85, "", fontsize=10, va="top", linespacing=1.5
        )
        self.heading = ui_text(
            axes, 0.5, 1.035, "", transform=axes.transAxes, ha="center", fontsize=12
        )
        self.event_artists = [
            self.heading,
            *self.rows,
            self.queue_size,
            self.statistics,
            self.order,
            self.special,
        ]

        self.cells = PolyCollection(
            [[(p.x, p.y) for p in c.vertices] for c in model.diagram.cells],
            facecolors=[colormaps["tab20"](i % 20) for i in range(len(model.sites))],
            edgecolors="#3f4754",
            linewidths=0.6,
            alpha=0.65,
            zorder=1,
        )
        self.cells.set_visible(False)
        axes.add_collection(self.cells)
        self.edges = LineCollection([], colors=EDGE, linewidths=1.2, zorder=2)
        self.beach = LineCollection([], colors=BEACH, linewidths=2, zorder=4)
        self.limiting = LineCollection(
            [], colors=BEACH, linewidths=2, linestyles="dotted", zorder=4
        )
        for collection in (self.edges, self.beach, self.limiting):
            axes.add_collection(collection)
        self.pending = axes.scatter([], [], s=28, c="#a8b0bd", zorder=5)
        self.processed = axes.scatter([], [], s=28, c="#172b4d", zorder=5)
        self.breakpoints = axes.scatter([], [], s=13, c=BEACH, zorder=6)
        self.vertices = axes.scatter([], [], marker="s", s=24, c=EDGE, zorder=6)
        self.highlight = axes.scatter(
            [], [], s=130, facecolors="none", edgecolors=SWEEP, zorder=7
        )
        self.sweep = axes.axhline(0, color=SWEEP, lw=1.7, zorder=3)
        self.circle = Circle(
            (0, 0), 1, fill=False, ls="--", lw=1.2, color=CIRCLE, zorder=1
        )
        axes.add_patch(self.circle)
        self.outside = axes.text(
            0.02, 0.97, "", transform=axes.transAxes, color=SWEEP, fontsize=9, va="top"
        )
        self.boundary = Rectangle(
            (b.xmin, b.ymin),
            b.xmax - b.xmin,
            b.ymax - b.ymin,
            fill=False,
            ls="--",
            lw=1.2,
            color="#b42318",
            zorder=8,
        )
        axes.add_patch(self.boundary)
        self.motion_artists = [
            self.cells,
            self.circle,
            self.edges,
            self.sweep,
            self.beach,
            self.limiting,
            self.pending,
            self.processed,
            self.breakpoints,
            self.vertices,
            self.highlight,
            self.boundary,
            self.outside,
            self.height,
        ]

    def update(self, model):
        revision = (id(model.sweep), model.event_count, model.done, model.last_stale)
        self.event_changed = revision != self.revision
        if self.event_changed:
            self._update_event(model)
            self.revision = revision
        self.cells.set_visible(model.done)
        self.height.set_text(
            "" if model.special_case else f"Sweep y = {model.sweep_y:.6g}"
        )
        if model.done:
            self.hide_geometry()
            self.cells.set_visible(True)
            return
        curves = model.curves()
        for limiting, collection in ((False, self.beach), (True, self.limiting)):
            collection.set_segments(
                [
                    [(p.x, p.y) for p in c.points]
                    for c in curves
                    if c.limiting == limiting
                ]
            )
            collection.set_visible(True)
        breakpoints = model.breakpoints()
        self.breakpoints.set_offsets(offsets(p for _, p in breakpoints))
        self.breakpoints.set_visible(True)
        active = {}
        for key, p in breakpoints:
            active.setdefault(key, []).append(p)
        lines = []
        for key, edge in model.sweep.edges.items():
            ends = [model.world(model.sweep.vertices[v].point) for v in edge.vertices]
            moving = active.get(key, [])
            if len(ends) >= 2:
                lines.append((ends[0], ends[1]))
            elif ends:
                lines.extend((ends[0], p) for p in moving)
            elif len(moving) >= 2:
                lines.append((moving[0], moving[1]))
            elif moving and model.points[key[0]].y == model.points[key[1]].y:
                lines.append((moving[0], Point(moving[0].x, self.ylim[1])))
        self.edges.set_segments([[(p.x, p.y), (q.x, q.y)] for p, q in lines])
        self.edges.set_visible(True)
        y = model.sweep_y
        self.sweep.set_ydata([y, y])
        self.sweep.set_visible(self.ylim[0] <= y <= self.ylim[1])
        self.outside.set_visible(not self.sweep.get_visible())
        if self.outside.get_visible():
            above = y > self.ylim[1]
            self.outside.set_text("Sweep above view" if above else "Sweep below view")
            self.outside.set_position((0.02, 0.97 if above else 0.02))
            self.outside.set_verticalalignment("top" if above else "bottom")
        candidate = model.sweep.queue.peek()
        if (
            model.last_event
            and model.last_event.kind == 1
            and not model.last_stale
            and model._subframe == 0
        ):
            candidate = model.last_event
        self.circle.set_visible(False)
        if (
            candidate
            and candidate.kind == 1
            and (
                (candidate is model.last_event and not model.last_stale)
                or not stale(candidate)
            )
        ):
            radius = model.scale * (candidate.centre.y - candidate.y)
            if math.isfinite(radius) and 0 < radius < 1e6 * self.span:
                centre = model.world(candidate.centre)
                self.circle.center = (centre.x, centre.y)
                self.circle.set_radius(radius)
                self.circle.set_visible(True)

    def hide_geometry(self):
        for artist in (
            self.edges,
            self.beach,
            self.limiting,
            self.breakpoints,
            self.sweep,
            self.outside,
            self.circle,
            self.highlight,
        ):
            artist.set_visible(False)

    def _update_event(self, model):
        self.heading.set_text(
            "Completed clipped diagram"
            if model.done
            else "Fortune's sweep | drag to explore"
        )
        self.pending.set_offsets(
            offsets(p for i, p in enumerate(model.sites) if i not in model.processed)
        )
        self.processed.set_offsets(
            offsets(p for i, p in enumerate(model.sites) if i in model.processed)
        )
        self.vertices.set_offsets(
            offsets(model.world(v.point) for v in model.sweep.vertices)
        )
        points = (
            [model.sites[model.last_event.site]]
            if model.last_event and model.last_event.kind == 0 and not model.done
            else []
        )
        self.highlight.set_offsets(offsets(points))
        self.highlight.set_visible(bool(points))
        entries = [] if model.special_case else model.sweep.queue.preview(8)
        for row, event in zip(self.rows, entries + [None] * 8):
            text = ""
            if event:
                y = model.oy + model.scale * event.y
                text = f"{event_name(model, event)}   y={y:.5g}"
                if stale(event):
                    text += "  [stale]"
            row.set_text(text)
            row.set_color("#98a2b3" if event and stale(event) else EDGE)
        if model.special_case:
            self.special.set_text(
                textwrap.fill(
                    "Collinear special case: the production solver uses sorted neighbours and direct bisectors. No beach-line sweep is performed.",
                    30,
                )
            )
            self.queue_size.set_text("")
            self.statistics.set_text("")
            self.order.set_text("")
        else:
            self.special.set_text("Empty: sweep complete" if model.done else "")
            self.queue_size.set_text(
                f"{len(model.sweep.queue)} heap entries; top 8 shown"
            )
            stats = model.sweep.statistics
            self.statistics.set_text(
                f"Processed: {stats['site_events']} sites, {stats['circle_events']} circles\nDiscarded: {stats['stale_events']} stale events"
            )
            order = " | ".join(
                model.label(a.site) for a in list(model.sweep.beach)[:18]
            )
            if model.sweep.beach.count > 18:
                order += " | ..."
            self.order.set_text(
                "BEACH ORDER  (left to right)\n" + textwrap.fill(order or "(empty)", 33)
            )


class CachedPainter:
    """Two cached layers: static layout, then event text and control state."""

    def __init__(self, figure, event_artists, motion_artists, motion_regions=None):
        self.figure, self.canvas = figure, figure.canvas
        self.event_artists = event_artists
        self.motion_regions = motion_regions
        self.motion_artists = sorted(motion_artists, key=lambda a: a.get_zorder())
        self.artists = list(dict.fromkeys(event_artists + motion_artists))
        self.enabled = bool(self.canvas.supports_blit)
        self.base = self.event_background = None
        self.event_dirty = True
        for artist in self.artists:
            artist.set_animated(self.enabled)
        self.cid = self.canvas.mpl_connect("draw_event", self._on_draw)

    def _draw(self, artists):
        for artist in artists:
            if artist.get_visible():
                self.figure.draw_artist(artist)

    def _events(self):
        self.canvas.restore_region(self.base)
        self._draw(self.event_artists)
        self.event_background = self.canvas.copy_from_bbox(self.figure.bbox)
        self.event_dirty = False

    def _on_draw(self, event):
        if not self.enabled or self.canvas.is_saving():
            return
        self.base = self.canvas.copy_from_bbox(self.figure.bbox)
        self._events()
        self._draw(self.motion_artists)
        self.canvas.blit(self.figure.bbox)

    def paint(self, *, event_dirty=False):
        if not self.enabled:
            self.canvas.draw_idle()
            return
        self.event_dirty |= event_dirty
        if self.base is None:
            self.canvas.draw()
            return
        full_blit = self.event_dirty
        if self.event_dirty:
            self._events()
        self.canvas.restore_region(self.event_background)
        self._draw(self.motion_artists)
        if full_blit or self.motion_regions is None:
            self.canvas.blit(self.figure.bbox)
        else:
            for region in self.motion_regions():
                self.canvas.blit(region)

    def invalidate(self):
        self.base = self.event_background = None

    @contextmanager
    def full_render(self):
        states = [a.get_animated() for a in self.artists]
        try:
            for a in self.artists:
                a.set_animated(False)
            yield
        finally:
            for a, state in zip(self.artists, states):
                a.set_animated(state)
            self.invalidate()

    def close(self):
        self.canvas.mpl_disconnect(self.cid)
