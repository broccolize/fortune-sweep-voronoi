# Detailed Milestone Schedule

Feature schedule supplied by the owner. See devlog.md for verified results.

## Phase 1 — Planning and environment

### 24 October — Requirements and architecture

Analyse specifications and grading criteria; create requirements checklist;
design modules; choose beach-line, event-queue and edge representations;
define tolerances and validation methods.

### 25 October — Environment and geometry

Initialize Python project and Git; configure pytest and pinned dependencies;
create README and development log; implement geometric predicates and parabola
intersections; write geometry unit tests.

## Phase 2 — Fortune implementation

### 26 October — Beach line

Implement balanced beach line, insertion, deletion and search; test operations.

### 27 October — Site events

Implement priority queue, sweep processing, site events and breakpoints;
test site-event processing.

### 28 October — Circle detection

Implement circumcentres, valid-circle detection and orientation handling;
write detection tests.

### 29 October — Circle processing

Implement invalidation, arc removal and beach-line updates; emit vertices;
test circle processing.

### 30 October — Complete sweep

Integrate event types; verify queue/beach-line invariants; test ordinary inputs
and debug sweep errors.

## Phase 3 — Diagram construction

### 31 October — Edges

Implement edge representation, finite edges, infinite rays and incomplete-edge
handling; test construction.

### 1 November — Clipping

Implement box clipping and closed ordered cells; validate clipping geometry.

### 2 November — First complete diagram

Generate complete diagrams; test small/medium inputs; verify topology and
boundary order; fix construction errors.

## Phase 4 — Robustness and correctness

### 3 November — Degeneracies

Handle horizontal/vertical/slanted collinearity, cocircularity, duplicates,
near-coincidence and single/two-site cases; investigate simultaneous events
and numerical instability.

### 4 November — Validation

Implement nearest-neighbour and empty-circle checks; test stability and
repeatability; optionally compare against a reference library; document failures
and corrections. Whether reference comparison was actually used remains to
be confirmed from the earlier files.

## Phase 5 — Interfaces

### 5 November — Input, output and CLI

Parse whitespace/comma coordinate files; generate seeded random sites;
export ordered CSV/text boundaries; print statistics/timing; document commands.

### 6 November — Visualization

Render coloured closed cells, labelled sites and box; export PNG/SVG;
support click insertion and compute trigger; generate examples.

## Phase 6 — Measurements and report

### 7 November — Benchmarks

Benchmark 100/1,000/10,000 sites, construction time and peak memory;
generate tables/plots; evaluate complexity and document methodology.
No actual numeric results were included in the supplied timeline.

### 8 November — First report draft

Prepare cover and all nine sections, architecture explanations, five problems
with all six required fields, tests and benchmark findings.

### 9 November — Report finalization

Target 13–16 body pages; apply mandatory formatting; add captions/citations;
provide problems/reflection page allocations; verify accuracy and export PDF
plus editable source. Earlier report files have not yet been examined here.

## Phase 7 — Demonstration and submission

### 10 November — Demo and packaging

Prepare script, personal recording, architecture/invariant explanations and
three design discussions; organize AI records and two authentic screenshots;
prepare Windows launcher and submission archive. Completion has not been
verified; the timeline provides no recording or archive location.

### 11 November — Final checks and submission, planned

Verify folders, clean-copy installation, full tests, exports, results, PDF,
video playback, AI evidence and reproduction instructions. Create
`CG_Assignment_<StudentID>_<Name>.zip` and submit before 23:59 GMT+8.
These are future tasks at the time this account was recorded.

## Reported milestone summary

| Date | Student reported milestone | Verification in this workspace |
| --- | --- | --- |
| 25 Oct | Environment and geometry foundation complete | Not inspected |
| 30 Oct | Fortune engine implemented | Not inspected |
| 2 Nov | Complete Voronoi construction working | Not inspected |
| 4 Nov | Degeneracies and correctness checks completed | Not inspected |
| 6 Nov | CLI and visualization complete | Not inspected |
| 7 Nov | Benchmarks complete | Raw results not supplied |
| 9 Nov | Report finalized | Earlier report not supplied |
| 10 Nov | Demo and package prepared | Artifacts not supplied |
| 11 Nov | Final verification and submission | Future plan |
