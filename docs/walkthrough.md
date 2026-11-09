# Understanding and Defending the Program

## Start with the output

Run the nine-site example. Every point inside the dashed rectangle belongs to
the cell of its nearest site. Adjacent polygons meet on perpendicular bisectors.
A clipping corner is a drawing boundary, not necessarily a Voronoi vertex.
Cells of hull sites extend beyond the box even though the displayed polygons
are finite. Their mathematical unboundedness is exported explicitly.

## Why the beach line stores arcs rather than just sites

After a site splits an arc, the old site can appear twice in the beach sequence.
The AVL tree therefore stores stable Arc objects, not one entry per input site.
At the current directrix, a node owns the interval between its two breakpoints.
Search moves left or right using those bounds. AVL rotations change the shape
of the tree but not its in-order sequence or its predecessor/successor links.

Find insert_after, remove and validate in beachline.py. Explain why physically
transplanting the successor is important when queued events refer to arc objects.

## Trace a triangle by hand

Use sites (0,0), (2,0), (1,2), in that input order. The top site has index 2 and
arrives first. The left bottom site creates arcs 2,0,2. The other bottom site
creates 2,0,2,1,2. The middle arc 2 between 0 and 1 disappears at the circle
event. Its centre is (1,0.75), its radius is 1.25, and its lowest point is y=-0.5.
The circle-event sweep height is therefore -0.5, not 0.75.

The final graph contains all three site pairs. The event closes two traced
boundaries and starts the third at the emitted centre. The ordered final cells
are formed from those neighbour bisectors and the box constraints.

## Why stale events stay in the heap

Removing an arbitrary heap entry would need extra indexing machinery. Instead,
each arc has a generation counter. A pending circle event records its value.
When neighbours change, schedule increments that counter. The old event can
remain physically queued, but its generation mismatch makes it unusable.
Read the first guard in circle_event and explain why it runs before topology
changes. A site identifier is not enough to validate a particular arc.

## Why final half planes are still Fortune construction

The sweep decides which site pairs can share a boundary. Final clipping uses
only that O(n)-size planar graph, not every pair of sites. A redundant diagonal
can appear when cocircular events select a triangulation; its constraint adds
no positive-length Voronoi edge. Angle sorting plus a deque intersects each
cell's neighbour constraints efficiently. This is output assembly from the
sweep, not a brute-force replacement for it.

## Read and explain the numerical fixes

Start with the five real analyses in docs/problems.md. In particular:

- A reliable determinant sign does not guarantee accurate circumcentre coordinates.
- A normalized plane coefficient can already have lost essential information.
- A large epsilon can retain invalid topology rather than make it robust.
- Exporting near 1e9 introduces a world-coordinate ULP even after local normalization.

The Decimal fallback is 80 digits, not arbitrary certified exact arithmetic for
all possible inputs. Explain the limits instead of promising that floating point
can never fail. Near-site tests pass selected tolerances and configurations.

## Explain what the tests establish

Random queries are located using polygon edges, then checked against a separate
linear distance scan. Every checked circle vertex must be equidistant to its
defining sites and empty of all other sites. Area, structure and ownership tests
cover different failure modes. A pretty image or equal total area alone is not
a complete correctness argument. NumPy accelerates large brute-force validation;
the production constructor does not import it.

## Practice questions

1. Why can one site have several live beach arcs?
2. Why are circle events processed at the bottom of the circle?
3. What makes a queued event invalid, and how is that detected?
4. Why does an AVL rotation preserve beach order?
5. How do exact duplicates differ from near-coincident inputs?
6. What information is lost when infinite cells are drawn in a box?
7. Why does a half-plane intersection use only sweep-generated neighbours?
8. Which measurement includes clipping, and which includes tracing overhead?
9. What failed before each numerical fix, and what regression checks it now?
10. What would be needed for a certified exact geometric implementation?
