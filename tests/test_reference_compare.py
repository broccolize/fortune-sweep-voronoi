import pytest

pytest.importorskip(
    "scipy", reason="Install requirements-reference.txt for independent comparison"
)

from reference_compare.compare import compare_case, main, reference_cells  # noqa: E402

from fortune.diagram import construct  # noqa: E402
from fortune.geometry import Box  # noqa: E402
from fortune.io import random_sites  # noqa: E402


@pytest.mark.parametrize("seed", [0, 7, 2026])
def test_scipy_geometry_and_delaunay_match_independent_engine(seed):
    points = random_sites(20, seed)
    result = compare_case("random", points, seed=seed, topology=True, queries=30)
    assert result["discrepancies"] == []
    assert result["reference"]["status"] == "passed"
    assert result["reference"]["delaunay_edges_compared"] > 0


@pytest.mark.parametrize(
    "points",
    [
        [(i, 0) for i in range(4)],
        [(0, 0), (1, 0), (1, 1), (0, 1)],
        [(0, 0), (2, 1e-16), (3, 0), (3, 2)],
    ],
)
def test_exact_oracle_covers_degenerate_reference_inputs(points):
    result = compare_case("degenerate", points, queries=30)
    assert not result["discrepancies"]
    assert result["reference"]["status"] in (
        "passed",
        "unsupported",
        "precision_limited",
    )


def test_validator_detects_an_intentionally_overlapping_cell():
    d = construct([(0, 0), (1, 0), (0, 1)])
    d.cells[0].vertices = d.cells[1].vertices[:]
    result = compare_case("corrupted", d.sites, diagram=d, queries=40)
    assert result["status"] == "failed"
    assert any(issue["kind"] == "cell_geometry" for issue in result["discrepancies"])


def test_reference_can_return_empty_clipped_cells():
    d = construct([(-3, 0), (-2, 0)], Box(0, -1, 1, 1))
    cells = reference_cells(d.sites, d.box)
    assert cells[0] == [] and len(cells[1]) == 4


def test_cli_writes_reproducible_inputs_and_reference_limitations(tmp_path):
    import json

    output = tmp_path / "reference.json"
    assert main(["--seeds", "1", "--queries", "10", "--output", str(output)]) == 0
    result = json.loads(output.read_text())
    assert result["summary"]["failed"] == 0
    assert "horizontal" in result["summary"]["reference_limitations"]
    assert all("input" in case and "seed" in case for case in result["cases"])
