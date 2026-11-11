"""Bounded, on-demand replay of the actual Fortune event engine.

The completed clipped diagram is prepared for the final frame. A fresh sweep
then uses FortuneSweep.step(), also used by batch construction. Intermediate
frames never infer a beach line from the completed polygons. No frame history
is retained. Exactly collinear inputs show the production solver's special case.
"""

import math
from dataclasses import dataclass

from .diagram import construct
from .geometry import Box, Point, breakpoint_x, parabola_y
from .sweep import FortuneSweep, all_collinear, collinear_neighbours

MAX_REPLAY_SITES = 200


@dataclass(frozen=True, slots=True)
class ArcCurve:
    site: int
    points: tuple[Point, ...]
    limiting: bool = False


def stale(event):
    return event.kind == 1 and (
        not event.arc.alive or event.arc.generation != event.generation
    )


class SweepReplay:
    def __init__(self, coordinates, box=None, *, debug=False):
        coordinates = [
            p if isinstance(p, Point) else Point(float(p[0]), float(p[1]))
            for p in coordinates
        ]
        if len(set(coordinates)) > MAX_REPLAY_SITES:
            raise ValueError(
                f"Replay supports at most {MAX_REPLAY_SITES} distinct sites; "
                "use batch mode for larger inputs."
            )
        self.diagram = construct(coordinates, box, debug=debug)
        self.sites, self.box = self.diagram.sites, self.diagram.box
        self.debug = debug
        xmin, xmax = min(p.x for p in self.sites), max(p.x for p in self.sites)
        ymin, ymax = min(p.y for p in self.sites), max(p.y for p in self.sites)
        self.scale = max(xmax - xmin, ymax - ymin) or max(
            1.0, abs(xmin) * 1e-6, abs(ymin) * 1e-6
        )
        self.ox, self.oy = xmin + (xmax - xmin) / 2, ymin + (ymax - ymin) / 2
        self.points = [self.normalize(p) for p in self.sites]
        b = self.box
        self.view = Box(
            min(b.xmin, xmin),
            min(b.ymin, ymin),
            max(b.xmax, xmax),
            max(b.ymax, ymax),
        )
        self.special_case = all_collinear(self.sites)
        self.reset()

    def normalize(self, p):
        return Point((p.x - self.ox) / self.scale, (p.y - self.oy) / self.scale)

    def world(self, p):
        return Point(self.ox + self.scale * p.x, self.oy + self.scale * p.y)

    @property
    def done(self):
        return self.special_case or not self.sweep.queue

    @property
    def sweep_y(self):
        return self.oy + self.scale * self.display_y

    def label(self, site):
        return "/".join(map(str, self.diagram.cells[site].input_indices))

    def reset(self):
        self.sweep = (
            collinear_neighbours(self.points)
            if self.special_case
            else FortuneSweep(
                self.points, debug=self.debug, original_points=self.sites
            ).start()
        )
        self.processed = set(range(len(self.sites))) if self.special_case else set()
        top = max(self.view.ymax, max(p.y for p in self.sites))
        span = max(self.view.xmax - self.view.xmin, self.view.ymax - self.view.ymin)
        self.display_y = (top + 0.1 * span - self.oy) / self.scale
        self.last_event = None
        self.last_stale = False
        self.event_count = 0
        self._subframe = 0
        self._segment_start = self.display_y

    def step_event(self):
        if self.done:
            return None
        previous_stale = self.sweep.statistics["stale_events"]
        event = self.sweep.step()
        self.display_y = self.sweep.sweep_y
        self.last_event = event
        self.last_stale = self.sweep.statistics["stale_events"] > previous_stale
        self.event_count += 1
        if event.kind == 0:
            self.processed.add(event.site)
        self._subframe = 0
        self._segment_start = self.display_y
        return event

    def tick(self, substeps=8):
        """Move toward, never past, the next event before processing it.

        Same-height events remain distinct steps. Subdivision is per event,
        avoiding arbitrarily long waits for far-away circumcircle bottoms.
        """
        if substeps < 1:
            raise ValueError("Substeps must be positive")
        if self.done:
            return None
        target = min(self.sweep.sweep_y, self.sweep.queue.peek().y)
        self._subframe += 1
        if self._subframe >= substeps or target == self.display_y:
            return self.step_event()
        fraction = self._subframe / substeps
        self.display_y = (1 - fraction) * self._segment_start + fraction * target
        return None

    def curves(self, samples=65):
        """Sample only each live arc's actual breakpoint interval."""
        if samples < 2:
            raise ValueError("At least two arc samples are required")
        if self.done:
            return []
        lo, hi = (
            self.normalize(Point(self.view.xmin, self.view.ymin)),
            self.normalize(Point(self.view.xmax, self.view.ymax)),
        )
        pad = 0.06 * max(hi.x - lo.x, hi.y - lo.y)
        result = []
        for arc in self.sweep.beach:
            focus = self.points[arc.site]
            if focus.y == self.display_y:
                # The new parabola is a vertical limiting fragment at birth.
                heights = [
                    parabola_y(self.points[a.site], focus.x, self.display_y)
                    for a in (arc.prev, arc.next)
                    if a and self.points[a.site].y > self.display_y
                ]
                top = min(hi.y + pad, min(heights) if heights else hi.y + pad)
                result.append(
                    ArcCurve(
                        arc.site,
                        (
                            self.world(focus),
                            self.world(Point(focus.x, max(focus.y, top))),
                        ),
                        True,
                    )
                )
                continue
            if focus.y < self.display_y:
                raise ArithmeticError("Replay arc focus lies below the sweep")
            left = (
                breakpoint_x(self.points[arc.prev.site], focus, self.display_y)
                if arc.prev
                else lo.x - pad
            )
            right = (
                breakpoint_x(focus, self.points[arc.next.site], self.display_y)
                if arc.next
                else hi.x + pad
            )
            left, right = max(left, lo.x - pad), min(right, hi.x + pad)
            if left >= right:
                continue
            points = []
            for i in range(samples):
                x = left + (right - left) * i / (samples - 1)
                y = parabola_y(focus, x, self.display_y)
                p = self.world(Point(x, y))
                points.append(
                    p
                    if math.isfinite(p.x) and math.isfinite(p.y)
                    else Point(math.nan, math.nan)
                )
            result.append(ArcCurve(arc.site, tuple(points)))
        return result

    def breakpoints(self):
        result = []
        if self.done:
            return result
        for left in self.sweep.beach:
            if left.next is None:
                continue
            right = left.next
            a, b = self.points[left.site], self.points[right.site]
            x = breakpoint_x(a, b, self.display_y)
            focus = a if a.y > self.display_y else b
            if focus.y <= self.display_y:
                continue
            p = self.world(Point(x, parabola_y(focus, x, self.display_y)))
            if math.isfinite(p.x) and math.isfinite(p.y):
                result.append((tuple(sorted((left.site, right.site))), p))
        return result
