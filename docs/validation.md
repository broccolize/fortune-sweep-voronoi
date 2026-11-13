# Validation and Benchmark Evidence

Current integration: 18 November 2026, GMT+8. The native main suite passed
139 tests in 14.48 seconds. Raw JUnit, separate installation evidence, stress
results and measured benchmarks retain their own execution scope and timestamps.

## Test run record

| Field | Recorded evidence |
| --- | --- |
| Actual timestamp and timezone | JUnit and benchmark records; review dated 18 November GMT+8 |
| Source snapshot | Integrated main; package verification records source/test hashes |
| OS and interpreter | Native Windows 11, Python 3.14.7; CI Windows/Ubuntu 3.12 and 3.14 |
| Dependency versions | requirements.txt; optional PDF audit dependencies in report/requirements.txt |
| Command and directory | Project root: test.bat -q --junitxml=evidence/tests-current.xml |
| Inputs | Explicit pytest inputs, seeded stress loops and benchmark seed 2026 |
| Main result | 139 passed, zero failures/errors/skips on the verified Node-enabled host |
| Raw evidence | evidence/tests-current.xml; evidence/stress-final.json; results/benchmark.json |
| Independent delivery | tools/verify_package.py installs an extracted ZIP in its own environment |
| Limits | Sampled ownership is not exhaustive coverage; finite-precision construction is not universally certified |

The two optional JavaScript checks explicitly skip if Node is unavailable.
Node is not required to use the offline viewer. The earlier Pi screenshot
records its actual 86-test run and is not relabelled as a 139-test execution.

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

## Applied benchmark protocol

Measure n = 100, 1,000, 10,000 seeded sites on the same environment and settings.
Keep plotting and file export outside construction timing, and state exactly
whether clipping and cell assembly are included. Record wall time and measured
peak memory with the measurement method disclosed. Separate instrumented memory
runs from timing runs if instrumentation materially affects time.

Keep raw per-run results rather than only a final mean. Record repetition count,
hardware, OS, Python/dependency versions, seed and bounding box. Compare time
against n log n and memory against n; report discrepancies instead of forcing a fit.

The current protocol uses three uninstrumented timing runs per size and a fresh
memory subprocess per size. Medians are 0.08210 / 0.66062 / 6.66119 seconds;
traced Python peaks are 0.70 / 7.38 / 65.08 MiB. Process working-set peaks include
the interpreter and allocation tracing. The 10,000-site timings ranged from
5.25015 to 6.92806 seconds on this shared desktop. Replay export and drawing are
excluded; the earlier faster benchmark is preserved separately rather than reused.
