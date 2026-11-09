# Architecture Notes

Status: implemented and independently tested. See evidence/tests-current.xml.

## Implemented module responsibilities

| Module | Responsibility |
| --- | --- |
| `geometry` | Points, orientation, circumcentres and parabola intersections |
| `events` | Event records, deterministic heap priorities and invalidation |
| `beachline` | Balanced ordered arc structure plus adjacent-arc links |
| `sweep` | Sweep orchestration and site/circle event handlers |
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

## Verified design choices and practical limits

1. The AVL tree gives a worst-case logarithmic height bound.
2. Events use stable arc identity and generation counters; stale heap entries
   are discarded lazily. Tests exercise invalidation through random diagrams.
3. Equal heights insert limiting arcs, exact collinearity uses sorted neighbours,
   and exact input-circle identities group genuine cocircular vertices. Rounded
   coordinate buckets must not merge distinct nearby vertices.
4. Angle-sorted half-plane intersection uses only sweep neighbours and box
   constraints, with O(k log k) work for degree k and O(n log n) total target.
5. Uncertain plane order/membership and zero-edge concurrence use rational signs.
   Difficult intersection coordinates use 80-digit Decimal arithmetic.
6. The sweep's event positions and exported coordinates are still doubles;
   selected near-machine-precision inputs pass, not a universal exactness proof.
