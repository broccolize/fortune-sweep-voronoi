"""Reproduce the expanded normalization/event-order regression sweep.

Run: python tools/check_precision.py --output evidence/precision-validation.json
All 800 deterministic configurations use the production engine and independent
area, ownership and empty-circle validators from tests/validation.py.
"""

import argparse
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]

from validation import validate_cells, validate_empty_circles  # noqa: E402

from fortune.diagram import construct  # noqa: E402


def cases():
    for n in (3, 4, 5, 10, 30, 100):
        for seed in range(30):
            rng = random.Random(seed)
            yield (
                f"uniform n={n} seed={seed}",
                [(rng.random(), rng.random()) for _ in range(n)],
            )
    for seed in range(60):
        rng = random.Random(seed)
        for epsilon in (0, 1e-6, 1e-12, 1e-15):
            yield (
                f"grid epsilon={epsilon} seed={seed}",
                [
                    (
                        rng.randrange(5) + epsilon * rng.random(),
                        rng.randrange(5) + epsilon * rng.random(),
                    )
                    for _ in range(20)
                ],
            )
            yield (
                f"cluster epsilon={epsilon} seed={seed}",
                [(epsilon * rng.random(), epsilon * rng.random()) for _ in range(10)]
                + [(rng.random(), rng.random()) for _ in range(10)],
            )
    for n in (4, 5, 6, 8, 12, 24, 50):
        for seed in range(20):
            rng = random.Random(seed)
            angle = rng.random() * math.pi
            points = [
                (
                    math.cos(angle + 2 * math.pi * i / n),
                    math.sin(angle + 2 * math.pi * i / n),
                )
                for i in range(n)
            ]
            rng.shuffle(points)
            yield f"ring n={n} seed={seed}", points


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "evidence/precision-validation.json"
    )
    args = parser.parse_args(argv)
    started = perf_counter()
    failures = []
    count = 0
    for name, points in cases():
        count += 1
        try:
            diagram = construct(points, debug=True)
            validate_cells(diagram, queries=100, seed=13)
            validate_empty_circles(diagram)
        except Exception as exc:
            failures.append(dict(case=name, input=points, error=repr(exc)))
    result = dict(
        executed_at=datetime.now(timezone.utc).isoformat(),
        status="failed" if failures else "passed",
        configurations=count,
        queries_per_case=100,
        failed=len(failures),
        failures=failures,
        seconds=perf_counter() - started,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
