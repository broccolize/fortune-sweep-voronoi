"""Circle-event eligibility for three consecutive arcs in a downward sweep."""

import math

from .geometry import circle_bottom, circumcircle, orient


def candidate_circle(a, b, c, sweep_y):
    if a == c or a == b or b == c or orient(a, b, c) >= 0:
        return None
    circle = circumcircle(a, b, c)
    if circle is None:
        return None
    centre, _ = circle
    bottom = circle_bottom(centre, b)
    # Permit same-level events (essential for cocircular sites), but never a
    # materially earlier event. The allowance is tied to arithmetic precision.
    allowance = 64 * math.ulp(max(1.0, abs(sweep_y)))
    if bottom > sweep_y + allowance:
        return None
    return centre, min(bottom, sweep_y)
