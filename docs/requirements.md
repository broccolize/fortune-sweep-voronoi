# Requirements and Acceptance Evidence

Source: official assignment specification supplied by the student. All boxes
start unchecked until the corresponding implementation or deliverable is
examined and verified. Earlier work may satisfy items after inspection.

## Algorithm — Sections 3 and 4.1

- [ ] From-scratch Fortune sweep with downward site and circle events.
- [ ] Ordered beach line with logarithmic locate, insert and delete.
- [ ] Event priority queue with deterministic ordering and stale-event handling.
- [ ] Parabola intersections and explicit numerical tolerance policy.
- [ ] Circle detection, invalidation, Voronoi vertices and incremental edges.
- [ ] Infinite-edge treatment and rectangular clipping.
- [ ] Equivalent per-cell boundary representation or DCEL; ordered boundaries.
- [ ] Justified O(n log n) construction time and O(n) space analysis.
- [ ] No existing Voronoi/Delaunay core or brute-force replacement.

## Input, output and visualization — Sections 4.2 and 4.3

- [ ] Plain text sites, one `x y` or `x,y` pair per line; sample included.
- [ ] Seeded uniform random sites in the unit square.
- [ ] Batch CLI, documented including `--input`, `--output`, `--csv` equivalents.
- [ ] Coloured closed polygons, site markers and indices, clipping boundary.
- [ ] PNG or SVG export to a specified location.
- [ ] Text/CSV cell export with ordered vertices and explicit clipped ray data.
- [ ] Console site/cell/vertex/edge counts and total construction time.
- [ ] Interactive click insertion and compute trigger; recommended in 4.2,
  but also expected in the demo and final self-check, so include it.

## Tests and measurements — Section 4.4

- [ ] Seeded random general-position tests.
- [ ] Many-query brute-force nearest-neighbour validation of constructed cells.
- [ ] Empty-circle and equidistance checks for emitted defining triples.
- [ ] Horizontal, vertical and slanted collinear cases.
- [ ] Four or more cocircular sites.
- [ ] Duplicate and near-coincident sites.
- [ ] Single and two-site cases.
- [ ] Numerical stability and deterministic repeatability checks.
- [ ] Annotated report figures for every required degenerate family.
- [ ] Measured n = 100, 1,000, 10,000 construction times.
- [ ] Measured memory use and analysis of space growth.
- [ ] Raw results, hardware/OS, interpreter, dependency versions, seeds and commands.
- [ ] Runtime table and scaling plot; investigate unexpected growth.
- [ ] Optional reference comparisons isolated under `tests/reference_compare/`
  and explicitly disclosed if used.

## Windows delivery — Sections 4.5 and 7

- [ ] Native Windows 10/11 x64 run path, verified on the available Windows host.
- [ ] Standalone executable or documented one-command run script.
- [ ] Exact dependency versions and installation instructions without licence keys.
- [ ] Complete source/build scripts and clean-checkout verification.
- [ ] Git history or Git log export if version control is used.
- [ ] Required folders plus root `README.txt`; reproducible figure commands.
- [ ] Archive `CG_Assignment_<StudentID>_<Name>.zip`; split/link if over 50 MB.
- [ ] Personal submission by email before 11 November 2026, 23:59 GMT+8.

## AI evidence — Section 5

- [ ] At least one mainstream/approved tool, no more than two tools.
- [ ] Actual product/version/model/access mode and subscription or plan disclosed.
- [ ] Credible record of prompts, generated work, checks, corrections and decisions.
- [ ] At least two authentic, legible substantive prompt-and-response screenshots.
- [ ] Five genuine substantive problems, each with symptom, investigation,
  root cause, solution with excerpt/patch, verification and prevention/lesson.
- [ ] Personal critical reflection grounded in actual experience.

## Report — Section 6

- [ ] Supplied cover adapted with real student details.
- [ ] English searchable PDF and editable `.md`, `.tex` or `.docx` source.
- [ ] A4, 2.5 cm margins, Times New Roman 12 pt, 1.5 line spacing.
- [ ] Numbered sections, figures/tables and captions; consistent cited references.
- [ ] At least ten body pages, excluding cover and appendices.
- [ ] At least six original figures/tables; include program screenshots,
  architecture, AI evidence, test results and performance visuals.
- [ ] 1 Introduction and theoretical background.
- [ ] 2 AI tools and development methodology.
- [ ] 3 Algorithm design and data structures.
- [ ] 4 Implementation and the AI-assisted coding process.
- [ ] 5 Testing and validation.
- [ ] 6 Problems and solutions, at least 1.5 pages.
- [ ] 7 Performance analysis and results.
- [ ] 8 Critical reflection on AI-assisted programming, at least one page.
- [ ] 9 Conclusion, followed by references and appropriate appendices.

## Personal recording — Section 4.5

- [ ] MP4 or GIF at most five minutes, with the student's audible narration.
- [ ] Batch and interactive demonstrations; pre-generated inputs and outputs.
- [ ] Architecture, beach-line invariant and event-queue invariant explained.
- [ ] Three actual problems or design decisions explained by the student.
- [ ] Playback and duration checked before packaging.
