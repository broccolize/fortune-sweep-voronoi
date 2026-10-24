# Validation and Benchmark Evidence

Status as recorded on 10 November 2026: no project tests or benchmarks have
been run in this workspace. Environment checks are not correctness tests.
Do not describe unchecked earlier results as passing.

## Test run record

| Field | Value to record |
| --- | --- |
| Actual timestamp and timezone | Pending run |
| Commit or source snapshot | Pending source inspection |
| OS and interpreter | Record separately for Windows and WSL |
| Dependency versions | Exact installed versions |
| Command and working directory | Literal reproducible invocation |
| Input/seed | File, generator and seed |
| Result | Passed / failed / skipped counts and reasons |
| Raw evidence | stdout/stderr or machine-readable result path |
| Interpretation | What the checks establish and what remains unverified |

## Validation design

Independently locate sampled queries in the exported cell polygons, then compare
their owners with a linear nearest-site scan. A core nearest-site helper that
itself just scans all sites does not validate constructed cells.

For each emitted interior Voronoi vertex, compare distances to defining sites
and scan all sites for strict interior points. Do not apply the empty-circle
property to arbitrary bounding-box corners created only by clipping.

Check polygon area, coverage, containment and shared boundaries in addition to
vertices. Exercise repeated runs, input permutations and coordinate scaling.
Define tie handling explicitly for equidistant queries and duplicate sites.

## Benchmark protocol to finalize

Measure n = 100, 1,000, 10,000 seeded sites on the same environment and settings.
Keep plotting and file export outside construction timing, and state exactly
whether clipping and cell assembly are included. Record wall time and measured
peak memory with the measurement method disclosed. Separate instrumented memory
runs from timing runs if instrumentation materially affects time.

Keep raw per-run results rather than only a final mean. Record repetition count,
hardware, OS, Python/dependency versions, seed and bounding box. Compare time
against n log n and memory against n; report discrepancies instead of forcing a fit.
