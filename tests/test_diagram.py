import math
import random
import pytest
from fortune.diagram import construct
from fortune.geometry import Box
from validation import validate_cells, validate_empty_circles


@pytest.mark.parametrize('seed', range(25))
def test_random_cells_and_empty_circles(seed):
    rng = random.Random(seed)
    diagram = construct([(rng.random(), rng.random()) for _ in range(35)],
                        Box(0, 0, 1, 1), debug=True)
    validate_cells(diagram, queries=150, seed=seed)
    validate_empty_circles(diagram)


CASES = {
    'single': [(0, 0)],
    'two': [(0, 0), (1, 1)],
    'horizontal': [(i, 0) for i in range(8)],
    'vertical': [(0, i) for i in range(8)],
    'slanted': [(i, 3*i + 1) for i in range(8)],
    'square': [(0, 0), (1, 0), (1, 1), (0, 1)],
    'cocircular': [(math.cos(2*math.pi*i/9), math.sin(2*math.pi*i/9)) for i in range(9)],
    'duplicates': [(0, 0), (1, 0), (0, 1), (0, 0), (1, 0)],
    'near': [(0, 0), (1e-11, 1e-11), (1, 0), (.3, .7), (0, 1)],
    'grid': [(x, y) for x in range(5) for y in range(5)],
    'equal_rows': [(0, 2), (1, 2), (2, 2), (.5, 1), (1.5, 1), (1, 0)],
}


@pytest.mark.parametrize('case', CASES)
def test_degenerate_cells(case):
    d = construct(CASES[case],debug=True)
    validate_cells(d,queries=400)
    validate_empty_circles(d)
    assert d.statistics['unique_sites'] == len(set(CASES[case]))


def test_repeatability_and_input_permutations():
    rng = random.Random(16)
    points = [(rng.random(),rng.random()) for _ in range(40)]
    first = construct(points)
    second = construct(points)
    assert [c.vertices for c in first.cells] == [c.vertices for c in second.cells]
    rng.shuffle(points)
    validate_cells(construct(points))


@pytest.mark.parametrize('scale,offset', [(1e-8,0),(1e8,0),(1,1e9)])
def test_coordinate_scaling(scale,offset):
    points = [(offset+scale*x,offset+scale*y) for x,y in [(0,0),(.2,.9),(.7,.3),(1,1)]]
    d = construct(points)
    validate_cells(d)
    validate_empty_circles(d)


def test_empty_and_nonfinite_rejected():
    with pytest.raises(ValueError):
        construct([])
    with pytest.raises(ValueError):
        construct([(0,math.inf)])
