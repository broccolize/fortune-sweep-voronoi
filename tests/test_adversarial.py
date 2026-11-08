import math
import random
import pytest
from fortune.diagram import construct
from validation import validate_cells, validate_empty_circles, contains
from fortune.geometry import polygon_area


@pytest.mark.parametrize('exponent', [8,11,13,14,15])
def test_tight_cluster_among_distant_sites(exponent):
    rng = random.Random(exponent)
    points = [(0,0),(1,0),(1,1),(0,1)] + [
        (.4+10**-exponent*rng.random(),.6+10**-exponent*rng.random()) for _ in range(6)]
    diagram = construct(points,debug=True)
    validate_cells(diagram,queries=200)
    validate_empty_circles(diagram)


@pytest.mark.parametrize('n', [8,32,100])
def test_high_degree_cell_and_cocircular_sites(n):
    ring = [(math.cos(2*math.pi*i/n),math.sin(2*math.pi*i/n)) for i in range(n)]
    for points in (ring,ring+[(0,0)]):
        diagram = construct(points,debug=True)
        validate_cells(diagram,queries=150)
        validate_empty_circles(diagram)


@pytest.mark.parametrize('exponent',[10,11,12,13,14,15])
def test_every_distinct_cluster_site_retains_a_positive_cell(exponent):
    rng=random.Random(exponent)
    points=[(0,0),(1,0),(1,1),(0,1)]+[
        (.4+10**-exponent*rng.random(),.6+10**-exponent*rng.random()) for _ in range(6)]
    d=construct(points)
    for c in d.cells:
        assert len(c.vertices)>=3,('missing cell',exponent,c.site)
        assert polygon_area(c.vertices)>0,('zero area',exponent,c.site)
        assert contains(c.vertices,d.sites[c.site]),('site outside own cell',exponent,c.site)
