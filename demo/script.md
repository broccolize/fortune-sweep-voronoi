# Narrated Demonstration Script

Target length 4 minutes 45 seconds. Use your own words after tracing the code.
Do not claim personal verification until you have performed the review checks.

## 0:00 to 0:25 Purpose and attribution

Show the nine-site diagram and the source tree.

Suggested narration: This personal project implements Fortune's sweep-line
algorithm for planar Voronoi diagrams. GPT-6.1 assisted with implementation,
testing and writing. The geometric core is implemented here, without an existing
Voronoi or Delaunay library. I will demonstrate the program and explain its
invariants and numerical fixes.

## 0:25 to 1:05 Batch mode and outputs

Run from the project root:

```bat
run.bat --input examples\sites.txt --bbox 0 0 1 1 --output output\demo.png --csv output\demo.csv --json output\demo.json
```

Show the result image, console statistics and the first CSV rows. Explain that
the vertices are ordered, the next endpoint closes each polygon, and JSON also
records defining sites and explicit ray information. Counts distinguish input
sites from unique sites and visible clipped edges from traced adjacencies.

## 1:05 to 1:50 Interactive mode

Run `run.bat --interactive`. Add five or six sites by clicking. Compute, add one
more point and compute again. Show Export creating PNG/CSV/JSON. State that the
interface recomputes the complete diagram when requested; it is not a dynamic
incremental Voronoi data structure between clicks.

## 1:50 to 2:45 Architecture and the two invariants

Show figures/architecture.png, then beachline.py and sweep.py.

Suggested narration: The AVL tree stores arcs in their current left-to-right
order, with links to adjacent arcs. One site may own several arcs. Rotations
preserve the order, while current parabola breakpoints guide a logarithmic search.
That is the beach-line invariant. The heap processes the highest remaining
valid sweep event. A queued circle event is usable only while its arc is alive
and its generation still matches. Neighbour changes increment the generation,
so stale events are discarded instead of changing the wrong topology.

## 2:45 to 3:45 Three concrete decisions and fixes

1. Explain stable arc identity. AVL deletion transplants the actual successor
   node rather than copying site data into a node referenced by queued events.
2. Explain close-site precision. Nearly parallel bisectors amplified rounded
   coefficients. The fix retains defining focus pairs and rebuilds the difficult
   intersection using Decimal arithmetic.
3. Explain the epsilon failure. A permissive clipping epsilon retained a tiny
   reversed edge beyond the box. Reducing it fixed a genuine ownership hole;
   making the validator more forgiving alone did not solve that defect.

Use docs/problems.md and the retained failure files to point to the actual
symptoms and passing regressions. Do not try to read every line of code.

## 3:45 to 4:30 Tests and measured scaling

Run `test.bat -q`. Show the current result, then results/benchmark.csv and
figures/scaling.png. Explain polygon ownership versus brute-force nearest site,
the empty-circle check and separate timing/memory runs. The recorded medians
are approximately 0.033, 0.406 and 4.357 seconds at 100, 1,000 and 10,000 sites.
These are machine-specific observations. The traced allocation peak grows
approximately linearly; three data sizes do not prove the asymptotic bound.

## 4:30 to 4:45 Limits and finish

State that finite-precision geometry is tested rather than universally certified.
Windows 11 has been exercised directly; do not claim a Windows 10 test that has
not been run. Finish before five minutes and check that narration is audible.
