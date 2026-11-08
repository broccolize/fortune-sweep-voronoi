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
