# Architecture Notes

Status: implementation design. Modules are complete only after verification.

## Candidate module responsibilities

| Module | Responsibility |
| --- | --- |
| `geometry` | Points, orientation, circumcentres and parabola intersections |
| `events` | Event records, deterministic heap priorities and invalidation |
| `beachline` | Balanced ordered arc structure plus adjacent-arc links |
| `fortune` | Sweep orchestration and site/circle event handlers |
| `diagram` | Sites, vertices, edges and per-cell boundary representation |
| `clipping` | Finite segments, rays, box intersections and boundary closure |
| `io` | Coordinate loading and ordered text/CSV exports |
| `visualize` | Matplotlib rendering and click-based input |
| `cli` | Batch/interactive arguments, statistics and reproducible invocation |
| `validation` / tests | Independent brute-force checks, never core construction |

## Invariants to explain and test

Beach line: in-order traversal gives the current left-to-right arc sequence;
each adjacent pair has the correct breakpoint at the current sweep position.
Locate, insertion and deletion must maintain both tree order and neighbour links.

Event queue: the next valid event has the highest remaining sweep coordinate;
site/circle ties have a documented deterministic policy. A circle event may be
processed only while its defining arc neighbourhood is still valid.

Output: incident cells share consistent geometric edges; finalized cells are
ordered, closed and clipped to the selected rectangle. Circle vertices retain
their defining sites for independent empty-circle validation.

## Design questions to verify

1. Which balanced structure is used, and is its complexity worst-case or expected?
2. Does circle-event invalidation use identity, a version counter or another scheme?
3. How are equal-height sites, cocircular events and collinearity handled?
4. How are output boundaries assembled without an all-pairs core fallback?
5. Does clipping preserve the desired total complexity? Measure and analyse
   output assembly separately if its worst-case bound differs from the sweep.
6. What tolerance policy is justified across coordinate scales?
