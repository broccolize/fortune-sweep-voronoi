import math

import pytest

from fortune.geometry import (
    Box,
    Point,
    breakpoint_x,
    circle_bottom,
    circle_identity,
    circumcircle,
    orient,
    parabola_y,
)


def test_orientation_and_collinearity():
    a, b, c = Point(0, 0), Point(2, 0), Point(0, 3)
    assert orient(a, b, c) == 6
    assert orient(c, b, a) == -6
    assert orient(a, b, Point(1, 0)) == 0
    assert orient(Point(0, 0), Point(1e200, 0), Point(0, 1e200)) > 0
    assert orient(Point(0, 0), Point(1e-200, 0), Point(0, 1e-200)) > 0


def test_circle_and_translation():
    for offset in (0, 1e9):
        result = circumcircle(
            Point(offset, offset), Point(offset + 2, offset), Point(offset, offset + 2)
        )
        assert result[0] == Point(offset + 1, offset + 1)
        assert result[1] == pytest.approx(math.sqrt(2))
    assert circumcircle(Point(0, 0), Point(1, 1), Point(2, 2)) is None


@pytest.mark.parametrize(
    "left,right,directrix",
    [
        (Point(0, 2), Point(1, 1), 0),
        (Point(1, 1), Point(0, 2), 0),
        (Point(-2, 3), Point(4, 3), -1),
        (Point(0.1, 0.7), Point(0.9, 0.70000000001), -0.1),
        (Point(-1, 1), Point(0.1, 0.2), 0.199999999),
    ],
)
def test_breakpoint_lies_on_both_parabolas(left, right, directrix):
    x = breakpoint_x(left, right, directrix)
    assert parabola_y(left, x, directrix) == pytest.approx(
        parabola_y(right, x, directrix), rel=2e-7, abs=2e-9
    )


def test_breakpoint_singular_limits():
    assert breakpoint_x(Point(0, 1), Point(2, 1), 1) == 1
    assert breakpoint_x(Point(1, 0), Point(0, 1), 0) == 1
    assert breakpoint_x(Point(0, 1), Point(2, 0), 0) == 2
    with pytest.raises(ValueError):
        parabola_y(Point(0, 0), 1, 0)


def test_stable_circle_bottom():
    centre, through = Point(0, 1e15), Point(1, 0)
    assert circle_bottom(centre, through) == pytest.approx(-5e-16)


def test_invalid_box():
    with pytest.raises(ValueError):
        Box(0, 0, 0, 1)
    with pytest.raises(ValueError):
        Box(0, 0, math.inf, 1)


def test_circle_identity_merges_only_the_same_exact_circle():
    a, b, c, d = Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)
    assert circle_identity(a, b, c) == circle_identity(a, c, d)
    # These centres round into the same old 14-decimal bucket, but define
    # different circles and must retain distinct vertices and connecting edges.
    close = Point(0, 2 + 1e-15)
    assert circle_identity(a, b, d) != circle_identity(a, b, close)
