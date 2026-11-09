# Requirements and Acceptance Evidence

Source: official assignment specification supplied by the student. Checked items have implementation or artifact evidence. Unchecked items are
optional, personal, or await final packaging/owner review. This is a personal
project; student identity and actual email submission are not applicable.

## Algorithm — Sections 3 and 4.1

- [x] From-scratch Fortune sweep with downward site and circle events.
- [x] Ordered beach line with logarithmic locate, insert and delete.
- [x] Event priority queue with deterministic ordering and stale-event handling.
- [x] Parabola intersections and explicit numerical tolerance policy.
- [x] Circle detection, invalidation, Voronoi vertices and incremental edges.
- [x] Infinite-edge treatment and rectangular clipping.
- [x] Equivalent per-cell boundary representation or DCEL; ordered boundaries.
- [x] Justified O(n log n) construction time and O(n) space analysis.
- [x] No existing Voronoi/Delaunay core or brute-force replacement.

## Input, output and visualization — Sections 4.2 and 4.3

- [x] Plain text sites, one `x y` or `x,y` pair per line; sample included.
- [x] Seeded uniform random sites in the unit square.
- [x] Batch CLI, documented including `--input`, `--output`, `--csv` equivalents.
- [x] Coloured closed polygons, site markers and indices, clipping boundary.
- [x] PNG or SVG export to a specified location.
- [x] Text/CSV cell export with ordered vertices and explicit clipped ray data.
- [x] Console site/cell/vertex/edge counts and total construction time.
- [x] Interactive click insertion and compute trigger; recommended in 4.2,
  but also expected in the demo and final self-check, so include it.

## Tests and measurements — Section 4.4

- [x] Seeded random general-position tests.
- [x] Many-query brute-force nearest-neighbour validation of constructed cells.
- [x] Empty-circle and equidistance checks for emitted defining triples.
- [x] Horizontal, vertical and slanted collinear cases.
- [x] Four or more cocircular sites.
- [x] Duplicate and near-coincident sites.
- [x] Single and two-site cases.
- [x] Numerical stability and deterministic repeatability checks.
- [x] Annotated report figures for every required degenerate family.
- [x] Measured n = 100, 1,000, 10,000 construction times.
- [x] Measured memory use and analysis of space growth.
- [x] Raw results, hardware/OS, interpreter, dependency versions, seeds and commands.
- [x] Runtime table and scaling plot; investigate unexpected growth.
- [ ] Optional reference comparisons isolated under `tests/reference_compare/`
  and explicitly disclosed if used.

## Windows delivery — Sections 4.5 and 7

- [x] Native Windows 10/11 x64 run path, verified on the available Windows host.
- [x] Standalone executable or documented one-command run script.
- [x] Exact dependency versions and installation instructions without licence keys.
- [x] Complete source/build scripts and clean-checkout verification.
- [x] Git history or Git log export if version control is used.
- [x] Required folders plus root `README.txt`; reproducible figure commands.
- [ ] Archive `CG_Assignment_<StudentID>_<Name>.zip`; split/link if over 50 MB.
- [ ] Personal submission by email before 11 November 2026, 23:59 GMT+8.

## AI evidence — Section 5

- [x] At least one mainstream/approved tool, no more than two tools.
- [ ] Actual product/version/model/access mode and subscription or plan disclosed.
- [x] Credible record of prompts, generated work, checks, corrections and decisions.
- [ ] At least two authentic, legible substantive prompt-and-response screenshots.
- [x] Five genuine substantive problems, each with symptom, investigation,
  root cause, solution with excerpt/patch, verification and prevention/lesson.
- [ ] Personal critical reflection grounded in actual experience.

## Report — Section 6

- [ ] Supplied cover adapted with real student details.
- [x] English searchable PDF and editable `.md`, `.tex` or `.docx` source.
- [x] A4, 2.5 cm margins, Times New Roman 12 pt, 1.5 line spacing.
- [x] Numbered sections, figures/tables and captions; consistent cited references.
- [x] At least ten body pages, excluding cover and appendices.
- [x] At least six original figures/tables; include program screenshots,
  architecture, AI evidence, test results and performance visuals.
- [x] 1 Introduction and theoretical background.
- [x] 2 AI tools and development methodology.
- [x] 3 Algorithm design and data structures.
- [x] 4 Implementation and the AI-assisted coding process.
- [x] 5 Testing and validation.
- [x] 6 Problems and solutions, at least 1.5 pages.
- [x] 7 Performance analysis and results.
- [x] 8 Critical reflection on AI-assisted programming, at least one page.
- [x] 9 Conclusion, followed by references and appropriate appendices.

## Personal recording — Section 4.5

- [ ] MP4 or GIF at most five minutes, with the student's audible narration.
- [ ] Batch and interactive demonstrations; pre-generated inputs and outputs.
- [ ] Architecture, beach-line invariant and event-queue invariant explained.
- [ ] Three actual problems or design decisions explained by the student.
- [ ] Playback and duration checked before packaging.
