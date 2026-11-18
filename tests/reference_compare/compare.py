"""Compare Fortune with SciPy/Qhull and a separate exact clipping oracle.

Setup: python -m pip install -r requirements-reference.txt
Run: python tests/reference_compare/compare.py --output evidence/reference-comparison.json

SciPy supplies independent Voronoi ridges and Delaunay triangles. A validation-
only Sutherland-Hodgman clipper uses exact Fraction inequalities against ALL
sites, independently of the production sweep and angle-sorted clipping code.
This also covers collinear inputs and records Qhull's precision limits rather
than perturbing sites with QJ or silently treating missing sites as a pass.

API: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Voronoi.html
"""

import argparse
import json
import math
import platform
import random
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import scipy  # noqa: E402
from scipy.spatial import Delaunay, QhullError, Voronoi, cKDTree  # noqa: E402

from fortune.diagram import construct  # noqa: E402

QHULL_OPTIONS = "Qbb Qc Qz"


def _fraction_points(points):
    return [(Fraction(p.x), Fraction(p.y)) for p in points]


def clip(polygon, a, b, c):
    """Independent iterative exact clipping by a*x+b*y <= c."""
    result = []
    if not polygon:
        return result
    previous = polygon[-1]
    before = a * previous[0] + b * previous[1] - c
    for current in polygon:
        after = a * current[0] + b * current[1] - c
        if (before > 0) != (after > 0):
            t = before / (before - after)
            result.append(tuple(p + t * (q - p) for p, q in zip(previous, current)))
        if after <= 0:
            result.append(current)
        previous, before = current, after
    return result


def reference_cells(points, box, neighbours=None):
    """Exact all-pairs oracle, or exact clipping of SciPy-generated neighbours."""
    points = _fraction_points(points)
    xmin, ymin, xmax, ymax = map(Fraction, box.as_tuple())
    rectangle = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    cells = []
    for i, p in enumerate(points):
        polygon = rectangle[:]
        for j in range(len(points)) if neighbours is None else sorted(neighbours[i]):
            if j == i:
                continue
            q = points[j]
            a, b = q[0] - p[0], q[1] - p[1]
            c = (q[0] * q[0] + q[1] * q[1] - p[0] * p[0] - p[1] * p[1]) / 2
            polygon = clip(polygon, a, b, c)
            if not polygon:
                break
        cells.append([(float(x), float(y)) for x, y in polygon])
    return cells


def _area(polygon):
    if not polygon:
        return 0.0
    x0, y0 = polygon[0]
    return (
        abs(
            math.fsum(
                (a[0] - x0) * (b[1] - y0) - (a[1] - y0) * (b[0] - x0)
                for a, b in zip(polygon, polygon[1:] + polygon[:1])
            )
        )
        / 2
    )


def _boundary_distance(point, polygon):
    closest = math.inf
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length2 = dx * dx + dy * dy
        t = (
            max(0, min(1, ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / length2))
            if length2
            else 0
        )
        closest = min(
            closest, math.hypot(point[0] - a[0] - t * dx, point[1] - a[1] - t * dy)
        )
    return closest


def cell_discrepancies(actual, expected, distance_tolerance, area_tolerance):
    issues = []
    if len(actual) != len(expected):
        issues.append(
            dict(kind="cell_count", actual=len(actual), expected=len(expected))
        )
    for i, (polygon, reference) in enumerate(zip(actual, expected)):
        if bool(polygon) != bool(reference):
            issues.append(dict(cell=i, kind="empty_cell_mismatch"))
            continue
        if not polygon:
            continue
        error = max(
            max(_boundary_distance(p, reference) for p in polygon),
            max(_boundary_distance(p, polygon) for p in reference),
        )
        area_error = abs(_area(polygon) - _area(reference))
        if error > distance_tolerance or area_error > area_tolerance:
            issues.append(
                dict(
                    cell=i,
                    kind="cell_geometry",
                    boundary_error=error,
                    area_error=area_error,
                )
            )
    return issues


def _contains(polygon, point, tolerance):
    if not polygon:
        return False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        if dx * (point[1] - a[1]) - dy * (point[0] - a[0]) < -tolerance * math.hypot(
            dx, dy
        ):
            return False
    return True


def compare_case(
    name, coordinates, *, seed=2026, queries=200, box=None, topology=False, diagram=None
):
    diagram = construct(coordinates, box) if diagram is None else diagram
    sites, box = diagram.sites, diagram.box
    span = max(box.xmax - box.xmin, box.ymax - box.ymin)
    ulp = math.ulp(max(abs(v) for v in box.as_tuple()))
    distance_tolerance = 2e-8 * span + 16 * ulp
    area_tolerance = 2e-8 * span**2 + 32 * ulp * span
    actual = [[(p.x, p.y) for p in cell.vertices] for cell in diagram.cells]
    oracle = reference_cells(sites, box)
    issues = cell_discrepancies(actual, oracle, distance_tolerance, area_tolerance)

    # Check query ownership against a separate nearest-neighbour implementation.
    rng = random.Random(seed)
    tree = cKDTree([(p.x, p.y) for p in sites])
    for _ in range(queries):
        point = (rng.uniform(box.xmin, box.xmax), rng.uniform(box.ymin, box.ymax))
        nearest, _ = tree.query(point)
        owners = [
            i
            for i, poly in enumerate(actual)
            if _contains(poly, point, distance_tolerance)
        ]
        if not owners or any(
            math.hypot(sites[i].x - point[0], sites[i].y - point[1])
            > nearest + distance_tolerance
            for i in owners
        ):
            issues.append(dict(kind="query_ownership", point=point, owners=owners))
            break

    reference = dict(engine="scipy.spatial.Voronoi/Qhull", qhull_options=QHULL_OPTIONS)
    values = np.array([(p.x, p.y) for p in sites])
    # Give Qhull a separate local frame so a large world-coordinate offset does
    # not dominate its precision checks. Exact clipping still uses original
    # input doubles and the original bounding box.
    origin = values[0].copy()
    reference_scale = max(float(np.ptp(values, axis=0).max()), 1e-300)
    values = (values - origin) / reference_scale
    reference.update(origin=origin.tolist(), scale=reference_scale)
    try:
        voronoi = Voronoi(values, qhull_options=QHULL_OPTIONS)
        neighbours = [set() for _ in sites]
        for i, j in voronoi.ridge_points:
            neighbours[i].add(int(j))
            neighbours[j].add(int(i))
        missing = [i for i, adjacent in enumerate(neighbours) if not adjacent]
        scipy_cells = reference_cells(sites, box, neighbours)
        reference_issues = cell_discrepancies(
            scipy_cells, oracle, distance_tolerance, area_tolerance
        )
        reference.update(
            status="passed",
            ridge_count=len(voronoi.ridge_points),
            missing_sites=missing,
        )
        if missing or reference_issues:
            reference.update(status="precision_limited", discrepancies=reference_issues)
        else:
            issues += [
                dict(issue, source="SciPy")
                for issue in cell_discrepancies(
                    actual, scipy_cells, distance_tolerance, area_tolerance
                )
            ]
        if topology and reference["status"] == "passed":
            triangulation = Delaunay(values, qhull_options=QHULL_OPTIONS + " Q12")
            reference_edges = {
                tuple(sorted((int(a), int(b))))
                for triangle in triangulation.simplices
                for a, b in zip(triangle, np.roll(triangle, -1))
            }
            actual_edges = set(diagram.delaunay_edges)
            if actual_edges != reference_edges:
                issues.append(
                    dict(
                        kind="delaunay_adjacency",
                        missing=sorted(reference_edges - actual_edges),
                        extra=sorted(actual_edges - reference_edges),
                    )
                )
            reference["delaunay_edges_compared"] = len(reference_edges)
    except QhullError as exc:
        reference.update(status="unsupported", reason=str(exc).splitlines()[0])
    return dict(
        name=name,
        seed=seed,
        input=[list(p) if not hasattr(p, "x") else [p.x, p.y] for p in coordinates],
        bbox=box.as_tuple(),
        unique_sites=len(sites),
        queries=queries,
        tolerances=dict(distance=distance_tolerance, area=area_tolerance),
        oracle="independent exact all-pairs Sutherland-Hodgman clipping",
        reference=reference,
        discrepancies=issues,
        status="failed" if issues else "passed",
    )


def cases(seeds):
    for seed in range(seeds):
        rng = random.Random(seed)
        yield dict(
            name=f"uniform-{seed}",
            seed=seed,
            topology=True,
            coordinates=[(rng.random(), rng.random()) for _ in range(10 + seed % 31)],
        )
    rng = random.Random(2026)
    base = [(rng.random(), rng.random()) for _ in range(20)]
    for scale, offset in ((1e-8, 0), (1e8, 0), (1, 1e9)):
        yield dict(
            name=f"scaled-{scale}-{offset}",
            topology=True,
            coordinates=[(offset + scale * x, offset + scale * y) for x, y in base],
        )
    fixed = {
        "single": [(0, 0)],
        "two": [(0, 0), (1, 1)],
        "horizontal": [(i, 0) for i in range(8)],
        "vertical": [(0, i) for i in range(8)],
        "slanted": [(i, 3 * i + 1) for i in range(8)],
        "square": [(0, 0), (1, 0), (1, 1), (0, 1)],
        "integer-circle": [
            (5, 0),
            (4, 3),
            (3, 4),
            (0, 5),
            (-3, 4),
            (-4, 3),
            (-5, 0),
            (-4, -3),
            (-3, -4),
            (0, -5),
            (3, -4),
            (4, -3),
        ],
        "grid": [(x, y) for x in range(5) for y in range(5)],
        "equal-rows": [(0, 2), (1, 2), (2, 2), (0.5, 1), (1.5, 1), (1, 0)],
        "duplicates": base + base[:3],
        "near-collinear": [(0, 0), (2, 1e-16), (3, 0), (3, 2)],
        "near-cluster": [
            (8.997599999142925e-16, 2.5500793136439805e-16),
            (8.650989386813507e-16, 3.134167580549946e-16),
            (0.11917669984214596, 0.2747612452227174),
            (0.6654330524247978, 0.11252900539650945),
        ],
    }
    for name, points in fixed.items():
        yield dict(name=name, coordinates=points, topology=name == "duplicates")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "evidence/reference-comparison.json"
    )
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--queries", type=int, default=200)
    args = parser.parse_args(argv)
    if args.seeds < 1 or args.queries < 1:
        parser.error("--seeds and --queries must be positive")
    records = []
    for case in cases(args.seeds):
        try:
            records.append(compare_case(**case, queries=args.queries))
        except Exception as exc:
            records.append(
                dict(
                    name=case["name"],
                    status="failed",
                    input=case["coordinates"],
                    discrepancies=[dict(kind="exception", error=repr(exc))],
                )
            )
    failed = sum(r["status"] == "failed" for r in records)
    limitations = [
        r["name"]
        for r in records
        if r.get("reference", {}).get("status") in ("unsupported", "precision_limited")
    ]
    result = dict(
        schema_version=1,
        executed_at=datetime.now(timezone.utc).isoformat(),
        python=platform.python_version(),
        scipy=scipy.__version__,
        numpy=np.__version__,
        status="failed"
        if failed
        else "passed_with_reference_limitations"
        if limitations
        else "passed",
        summary=dict(
            cases=len(records),
            passed=len(records) - failed,
            failed=failed,
            scipy_fully_compared=sum(
                r.get("reference", {}).get("status") == "passed" for r in records
            ),
            reference_limitations=limitations,
        ),
        criteria="Exact clipped cells and sampled ownership for every case; SciPy cells when all sites resolve; Delaunay edge equality for general-position cases. Cocircular triangulations may use different valid diagonals.",
        cases=records,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=False), encoding="utf-8"
    )
    print(
        json.dumps(
            dict(status=result["status"], **result["summary"], output=str(args.output)),
            indent=2,
        )
    )
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())
