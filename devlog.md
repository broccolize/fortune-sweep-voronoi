# Development Log

Records use the actual working date, GMT+8. Git milestone dates follow the
owner's schedule in docs/history.md. Only executed checks count as results.
AI assistance: this desktop assistant; Pi has only been inspected so far.

## 10 November 2026 Requirements and setup

- Request: build a personal geometry project to the full technical and
  documentation standard of the supplied specification.
- AI output: complete DOCX text extraction, requirements checklist, architecture
  design, role allocation, Markdown records and project configuration.
- Verification: read the full extracted document including appendices; read
  twelve nonempty UTF-8 documentation/configuration files.
- Environment: Windows Python 3.14.7, Git 2.55.0; Debian 13.7 on WSL 2;
  Pi 0.86.0, Node v22.23.2, npm 10.9.8. No Pi model run tested.
- Corrections: UTF-8 fixed extraction output; WSL and Git index access required
  approved execution. First commit failed due to missing author identity.
- Owner then supplied repository-local Git name and email and clarified that
  the project is personal, using the course specification as a quality target.
- Decisions: native Windows primary environment; AVL beach line; independent
  brute-force validation confined to tests.
- Initial status: implementation and correctness testing are beginning.

## Entry format

Record purpose, prompt summary, AI output, files changed, commands and inputs,
actual passing/failing results, root cause, correction, decisions and remaining
limitations. Preserve raw outputs where they matter.

## 10 November 2026 Core implementation and verification

- Implemented geometry, AVL beach line, event queue, circle detection and
  invalidation, traced vertices/edges and ordered half-plane cell construction.
- Tests progressed from 10 to 17 to 21. The first cell suite had 59 passes and
  three failures. Tight-cluster checks exposed additional conditioning and
  clipping-tolerance issues. Five genuine analyses are in docs/problems.md.
- After fixes, all 74 geometry, structural, diagram, adversarial and interface
  tests passed. Raw initial failures and current JUnit output are retained.
- Extended validation passed 300 random configurations and 40 cluster cases.
  For n=100/1000/10000 it checked 100 queries each and all circle vertices,
  including 19,978 at n=10000. No reference Voronoi library was used.
- Implemented text/comma input, random generation, CLI, ordered CSV/JSON,
  PNG/SVG and click-to-add interface. Native Tk output was observed; Export
  produced the actual files and a real screenshot was retained.
- Timing medians: 0.0151621, 0.1654038, 1.8706645 seconds for 100/1000/10000.
  Traced Python peaks: 540872, 5670864, 55839040 bytes. Memory runs were isolated
  from uninstrumented timing. Full conditions and raw values are in results/.
- Clean-copy verification installed pinned dependencies into a new environment
  and built a wheel successfully. The first clean test command used a missing
  parent for --basetemp (70 pass, four fixture setup errors). Creating that
  workspace directory fixed the harness; the clean suite passed all 74 tests.
- Corrected declared minimum Python from 3.11 to 3.12 after inspecting NumPy's
  package metadata. Pinned the build backend and verified wheel construction.
- GitHub repository connected and initial tested history pushed successfully.
- Report draft: all nine sections, actual plots/results and five problems;
  generated searchable PDF and inspected every initial rendered page. Layout
  revisions and final report/package verification are still being completed.

## 10 November 2026 Stricter tiny-cell review and final measurements

- Review added a requirement that every distinct in-box site retain a positive
  cell containing that site. Two additional cluster cases failed despite earlier
  sampled checks. The failing tiny-cell-initial.xml is retained.
- Root causes: a distance cutoff deleted genuine short edges and rounded-centre
  hashing merged distinct circle vertices. Replaced cleanup with exact rational
  concurrence and vertex grouping with exact input-circle identities. Uncertain
  half-plane order/membership also uses rational signs.
- Added a fail-fast postcondition: construction cannot silently return a zero-area
  cell for an in-box distinct site. Outside sites may legitimately clip away.
- Current suite: 82 passing tests. Repeated 340-configuration stress and all
  19,978 vertices at n=10000 passed. A fresh isolated package import, installed
  wheel, 82-test suite and batch exports passed in the clean environment.
- A transient isolated-build dependency resolution failure was retried successfully;
  no claim is made that the failed attempt passed. Earlier fixture/path failures
  are separately retained. Current clean summary is evidence/clean-install-summary.json.
- Remeasured final code after the stronger checks; results/benchmark.json is the
  current result, and benchmark-initial.json preserves the earlier version.
- Desktop package metadata read from Windows: OpenAI.Codex 26.1029.7803.0;
  the displayed app is ChatGPT and the owner reports model GPT-6.1. Plan is pending.
- GitHub's first two CI runs completed successfully on Windows and Linux with
  Python 3.12 and 3.14. The final revision will be pushed and checked as well.

## 10 November 2026 Final topology and presentation checks

- An exact twelve-site integer circle revealed 17 output edges instead of 12;
  the manual count evidence is retained. Hull adjacency now identifies true
  unbounded rays and removes redundant cocircular diagonals before clipping.
  Exact circle keys also provide world-coordinate vertex centres directly.
- The square regression additionally checks the exact twelve-site ring: one
  vertex and twelve rays. The suite remains 82 parametrized tests and passes.
- Reran full stress and performance after the final numerical/topology changes;
  only the current benchmark.json values are used by the report and plots.
- Formatted 27 Python files with Ruff 0.17.4 and checked format-only AST
  equivalence. A separate safe import cleanup passed the configured lint rules
  and the full 82-test suite. Runtime dependencies were not changed by formatting.
- Prepared a personal narration script, recording checklist and code walkthrough.
  Model metadata is recorded as owner-reported GPT-6.1, plan pending.

## 10 November 2026 Final artifact audit

- Report: 19 searchable A4 pages, comprising cover, 16 body pages and two
  appendix pages. Inspected every rendered page. Two crowded plot axes were
  corrected; the other seventeen page images remained byte-identical and the
  two revised pages were reinspected. PDF structure/font setup and page budgets
  were checked. The raw audits are retained in evidence/.
- Review ZIP: 134 files, 4,108,359 bytes, required folders present and CRC check
  passed. SHA-256 and source revision are in evidence/package-audit.json.
- Extracted that ZIP to a separate folder. Its 03_Executable launcher performed
  first-run environment creation and pinned installation and generated PNG,
  CSV and JSON. The extracted suite then passed all 82 tests in 3.95 seconds.
- GitHub revision 7333694 passed all four Windows/Ubuntu Python 3.12/3.14 jobs.
  See evidence/ci-final.json for the run and job conclusions.
- AI production work is complete for owner review. Remaining personal items:
  actual subscription-plan disclosure, two genuine prompt/response screenshots,
  personal review and understanding, and an audible narrated recording under
  five minutes. No placeholder screenshot or recording is presented as real.
