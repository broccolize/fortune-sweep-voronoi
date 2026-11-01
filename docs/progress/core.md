# Core Implementation Evidence

Actual verification date: 10 November 2026, GMT+8.

## Geometry

Implemented filtered orientation, translated circumcentres, a stable quadratic
breakpoint formula, equal-height/directrix limits, stable circle-bottom evaluation
and bounding-box validation. Initial geometry run: 10 passed in 0.11 seconds.

## Beach line

Implemented a stable-identity AVL arc tree with neighbour links and explicit
validation of parent pointers, height balance and in-order adjacency. Five
seeded runs each inserted 600 arcs at random positions and deleted them in random
order, validating after each operation. Geometry plus beach-line tests: 17 passed
in 1.10 seconds.

## Sweep

Implemented deterministic heap events, clockwise-triple circle detection,
generation-based invalidation, site splits, arc removals, emitted vertices and
traced edges. Triangle and simultaneous square events pass. Suite: 21 passed
in 1.31 seconds before cell construction was added.

## Cell construction and first corrections

Constructed ordered cells using angle-sorted half-plane intersection over only
sweep-generated neighbours plus four clipping boundaries. Initial suite:
59 passed, 3 failed. Two failures came from rounded zero-length polygon edges;
one came from a world-coordinate precision bound in the validator.

After removing redundant zero-length supports and including world-coordinate
ULP error in the validator: 62 passed in 1.93 seconds. Raw records:
`evidence/initial-cell-failures.xml` and `evidence/tests-current.xml`.

## Extended stress

300 independently seeded configurations (10–89 sites) passed area coverage,
sampled polygon ownership and empty-circle validation. Each used 25 queries.
Additional seeded construction completed at n=100, 1,000 and 10,000; empty-circle
validation was also performed for the first two sizes. These preliminary timings
are not a replacement for the repeated, separately measured benchmark protocol.
See `evidence/stress-summary.json`.
