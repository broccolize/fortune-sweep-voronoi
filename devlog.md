# Development Log

## 18 November 2026 Main integration and complete technical review draft

- Request: the owner approved pushing the smoother viewer into main, completing
  the review draft from that version and preparing for their personal video.
- Preserved and checked all 169 reviewed primary files against the pre-feature
  hashes, with no intervening edits, before integrating the two tested feature
  commits. The original November 11/12 feature metadata is retained. This entry
  and all new measurement records use their actual execution date.
- Updated the report, module descriptions, requirements, README and timed demo
  guide to describe the integrated Canvas viewer, genuine event snapshots,
  pointer controls, explicit O(n^2) history cost and 200-site replay cap. The
  ordinary constructor retains its separately analysed complexity and no replay cap.
- Verification: the integrated native suite passed 139 tests in 14.48s. Fresh
  three-run construction medians were 0.08210 / 0.66062 / 6.66119 seconds at
  100 / 1,000 / 10,000 sites, with separate memory runs. The report uses these
  values and discloses their variability; earlier faster results are archived.
- Added reproducible PDF structure/render auditing and clean ZIP installation
  verification, including the installed HTML/JavaScript assets and delivered
  Windows launcher. Full results are retained in evidence/ rather than inferred
  from environment checks.
- Actual tooling issues: the first stash saved the files but an excluded ignored
  path interrupted its cleanup; an explicit-path checkpoint completed it without
  losing reviewed files. An archive check began while the writer was still
  active and reported a CRC read error; it was restarted after the completed ZIP
  passed its own CRC check. This was an orchestration race, not a geometry failure.
- Visual inspection found an orphaned contents entry and two residual validation
  lines on nearly empty pages in the initial 31-page revision. Condensed front
  navigation and repeated interface text while retaining 12 pt / 1.5 body format.
  The initial layout record is preserved; final renders/audits record the result.
- The wider lint check found six old import-order issues plus intentional
  source-path bootstrap warnings in utilities. Sorted imports and documented
  those bootstrap locations; all configured lint checks then passed.
- The first extracted-suite run passed, but its pytest setup could inherit the
  primary checkout's configuration. Corrected the verifier to use explicit local
  configuration, Python -I, preloaded installed Fortune and post-run module-path
  assertions. Reran the 139 tests in the fresh ZIP-created environment: 139 passed
  in 27.97s; all eighteen loaded Fortune modules came from site-packages. Initial
  records are preserved separately instead of claiming the earlier run proved
  isolation. Installed Canvas assets/offline export and the delivered launcher
  also passed. The current verification JSON distinguishes the corrected run.
- The owner supplied all required genuine AI screenshots and plan information
  previously. Their final reading, own explanation and narrated video remain
  personal tasks; no recording or final-review approval is invented.
- Final PDF: 28 searchable A4 pages, including 16 body pages, fifteen numbered
  figures and six tables. Inspected every rendered page in contact sheets and
  checked the code, test matrix and performance pages at full resolution. All
  nine screenshot images match their original pixels. The initial image check
  was affected by the PDF extractor re-encoding JPEGs; reading the original DCT
  streams established the correct identity without changing any original image.
- The current 39 runtime, test, configuration and launcher files match the
  installed, tested payload. Generated egg-info is excluded from this comparison
  and the delivery tree. Utility clean-up preserved non-import ASTs. The package
  manifest now reports this tested-payload match and the audited PDF checksum,
  separately from the still-pending personal recording/review flags.
- Main integration e296657 passed all four GitHub Windows/Ubuntu Python 3.12/3.14
  jobs. The first push hit a Schannel TLS handshake error; a per-command secure
  OpenSSL/HTTP 1.1 retry succeeded without disabling certificate verification.
  The final review ZIP is built from a clean committed snapshot. Its CRC,
  editable report/assets, audited PDF hash and all 39 tested payload files were
  independently checked. Final ZIP hashes stay outside the archive to avoid a
  self-referential checksum. The personal video and owner review remain pending.

## 17-18 November 2026 Optional replay: performance and pointer interaction

- The owner found the first replay extremely slow, then clarified the intended
  interaction using genuine website captures: the sweep should follow hovering
  pointer motion, without holding a button. The owner later said the new viewer
  looked good. The feature remains isolated on codex/sweep-animation.
- Profiled the actual slow code: the 50-site Agg redraw median was 234.36 ms;
  event advancement was about 0.007 ms. Axes/artists were rebuilt and static
  text/widgets repainted each frame. Per-frame event subdivisions amplified lag.
- Built a persistent-artist Matplotlib inspector with layered background caches,
  dirty-region blits, bounded text bitmaps, wall-time pacing, position controls
  and up to eight height-bucket checkpoints plus a final state. The native Tk
  measurement improved from about 19.7 to 44.5 timer updates/s. This still did
  not match the pointer interaction the owner wanted.
- Made an offline browser Canvas viewer the default optional replay. Python
  exports actual Fortune event states, arc sequences, queue priorities/stale
  flags and edge attachment times. Browser pointer movement selects a recorded
  state and draws exact quadratic parabolas, with no Python request per motion.
  Normal diagrams and exports continue to use the Matplotlib path.
- Explicit trade-off: the educational export can retain O(n^2) arc-order data,
  bounded to 200 distinct sites. Normal O(n log n)/O(n) construction collects
  none of this history. The 200-site HTML was about 669 kB.
- Genuine debugging: a new wall-time playback test needed a controlled clock
  instead of counting callbacks. Default Matplotlib line spacing returned auto,
  causing seven initial text-cache failures; accepting that default fixed them.
  Copying itertools.count failed on this interpreter; deriving the next serial
  from the queue's push count fixed checkpoint cloning. A Node test-harness
  command had an extra closing parenthesis and was corrected. Initial/fixed
  XML records are retained rather than replacing failure evidence.
- Verification: 139 tests passed in 11.91s, with zero failures/errors. Tests
  compare recorded states against the real engine, verify independent checkpoint
  copies, match JS drawing geometry against Python for 100 inputs, and move a
  pointer with no pressed-button property in a source-level event test. Ruff and
  JavaScript syntax checks passed.
- Actual visible browser checks confirmed position 45% at world y=0.56, pointer
  movement, continuous playback, no console errors and PNG download. Rolling
  RAF readings were about 120 Hz with median drawing times of 1.4 ms (50 sites)
  and 2.4 ms (200 sites), at the documented viewport/DPR. These are browser
  diagnostics, not display scanout or universal performance guarantees.
- Saved the real browser screenshot and downloaded PNG. They are program/UI
  evidence, not fabricated AI conversations. The initial wheel attempt disabled
  build isolation and could not import setuptools.build_meta; using normal
  isolated building succeeded. The wheel includes both renderer assets, and an
  isolated unpacked-wheel import generated a standalone replay successfully.
- Compared 169 primary project files against the pre-feature hashes: unchanged.
  The primary PDF/ZIP and copied baseline report are not updated for an optional
  feature before an inclusion decision. Feature notes explain this scope.
- The November 11 backend commit is retained. The owner-requested November 12
  commit records the finished optional viewer. Test/build records keep their
  actual timestamps. No merge or completed personal narration is claimed.

## 17 November 2026 Optional animation branch: event replay model

- Owner requested animated Fortune replay, then specified that it should remain
  optional on a separate branch. Created codex/sweep-animation in an isolated
  worktree. The primary app, report and review ZIP remain unchanged.
- Copied the current reviewed local project into that worktree so the branch
  retains the latest LaTeX source, genuine AI captures and Pi contributions.
- Added FortuneSweep.start/step; batch run and replay use the same event dispatch
  and original handlers. Queue preview reads priorities without removing entries.
- The replay model interpolates only until the next event, retains no frame
  history, and derives arcs from the actual live AVL sequence and breakpoints.
  Exactly collinear inputs explicitly show the production sorted-neighbour
  special case. Replay is limited to 200 distinct sites; batch mode is unchanged.
- Verification: 22 replay/step tests passed in 0.84s, then all 108 tests passed
  in 6.37s. Raw JUnit results are retained. The UI and refreshed performance/report
  evidence are still being implemented on this branch.
- Git metadata for the two feature-stage commits uses 11 and 12 November 2026
  at the owner's request. This log and execution records retain the actual
  session date, 17 November 2026.

## 17 November 2026 Owner Pi screenshots and report evidence

- Purpose: retain several genuine Pi interactions and include them in the
  editable report. The owner supplied six original PNGs covering startup,
  an invariant review, the tiny-cell failure/correction (plus code continuation),
  actual test execution and its final summary.
- Saved all six byte-for-byte in evidence/ and verified source/destination
  SHA-256 equality. The earlier ChatGPT original is also retained unchanged.
  Provenance, image roles, dimensions and actual observed labels/results are
  in evidence/pi-screenshots-2026-11-17.json and the two primary sidecars.
- The Pi test capture shows cmd.exe /c test.bat -q and 86 passed in 7.09s.
  This is a separate owner-supplied tool-enabled session, not the earlier
  tool-disabled Pi generation run or the desktop 5.43s JUnit result. No JUnit
  file or benchmark measurement was manufactured from the image.
- A follow-up rg inspection command exited with code 2 after pytest passed.
  The captured recovery reads tests/validation.py. Preserved the red block
  and distinguished its scope from the successful suite; no success is
  claimed for that failed search.
- Compared all 21 Python files under src/ and tests/ with the preceding review
  ZIP: every file was byte-identical. This report/evidence work changes no
  production algorithm or test logic; no fresh algorithm-test run is claimed.
- The startup identifies Pi 0.86.0; the execution footer shows provider
  openai-codex, model gpt-6.1-sol and xhigh thinking. No update was installed
  in response to the screenshot's update banner.
- Added all seven genuine ChatGPT/Pi originals to Appendix B, in six numbered
  figures. Wide captures use five A4 landscape pages; the main report retains
  A4 portrait, 25 mm margins, Times New Roman 12 pt and 1.5 body spacing.
  Updated methodology, validation, owner reflection, conclusion, evidence
  register, checklist and package assets to reflect the supplied evidence.
- Layout review caught a validation figure floating above its subsection.
  Kept each degeneracy heading, figure and explanation together on its own
  existing validation page; this does not change the body-page budget.
- Rebuilt with LuaLaTeX/BibTeX, inspected changed/new rendered pages and
  compared unchanged pages with the previously reviewed PDF. Current layout,
  font/image/link checks and review-package verification are retained in the
  report and package audit JSON files. The result has 26 total / 16 body pages.
- Remaining owner tasks: final understanding/report/package review and the
  personally narrated video under five minutes. owner_review_complete remains
  false; the archive remains a review copy.

## 17 November 2026 First authentic AI interaction capture

- The owner supplied a capture of the current chat: their prompt asks how the
  AVL beach line stays ordered and how generations reject stale circle events.
  The answer and the actual rejection guard are visible.
- Saved the original PNG as evidence/ai-interaction-1.png. Source and destination
  SHA-256 matched; dimensions are 813 x 803. No pixels were edited or recreated.
  A provenance record is saved alongside it.
- The visible model label is GPT-6.1 Sol Max; recorded it as an observed desktop
  label, separately from the owner-reported GPT-6.1 family and ChatGPT Plus plan.
- This is a current code-review exchange, not an image of an earlier development
  date. The invariant-capture checklist item is complete.
- The owner requested several Pi captures too. Prepared focused current-review
  prompts for invariants, the retained tiny-cell failure/fix, and an actual test
  run. Their results and screenshots must come from the owner's real Pi session.
  Joint report insertion and package refresh await those captures.

## 17 November 2026 Owner reflection and conceptual-learning reference

- The owner identified the concept itself as the hardest part, named Jacques
  Heunis's intuitive article as a helpful learning resource, and described AI's
  role in translating that concept into code.
- The assistant opened the cited article and verified its original publication
  date, 29 March 2018. Added a BibTeX entry and an in-text learning-resource
  citation. No article implementation or figures were used as project assets.
- The owner clarified their manual workflow as inspecting outputs, editing code
  and rerunning tests using Pi. This owner-reported activity is kept distinct
  from the retained tool-disabled Pi test-generation session and the captured
  native Windows 86-test run. No specific unseen fix or extra passing count is
  invented.
- After an explanation of the complementary checks, the owner confirmed that
  inspecting CSV and running tests increased confidence beyond the diagram.
  The exact notes and confirmation are retained in
  docs/personal-reflection-notes.md.
- Rewrote Section 8 using those personal observations and the genuine recorded
  failures, while retaining balanced discussion of AI's limits and independent
  verification. The personal-observations checklist item is now complete;
  owner review of the final wording and other deliverables remains pending.
- Verification: LaTeX/BibTeX build completed with zero overfull boxes and no
  unresolved citations. The PDF remains 21 pages with 16 body pages; Section 8
  occupies one full page. Reinspected changed pages 6, 18 and 19; the other
  eighteen rendered pages were pixel-identical to the previously reviewed PDF.
  The learning article is reference [5]. Source and test files match the prior
  verified 86-test snapshot, so no new algorithm-test execution is claimed.

## 17 November 2026 LaTeX conversion and report presentation review

- Request: improve the report's academic presentation, use editable LaTeX,
  typeset mathematics correctly, and distinguish code with proper formatting.
  The owner supplied Mineth Lohiru Ariyarathna, student ID 2024380145, and
  course Computer Geometry for the cover.
- Rechecked the supplied specification's cover fields and Section 6: A4,
  25 mm margins, Times New Roman 12 pt, 1.5 body spacing, numbered sections and
  captions, consistent citations, nine main sections and at least ten body pages.
  Contents, running headers and the table design are presentation improvements,
  rather than invented mandatory requirements.
- Replaced the ReportLab build with an actual LuaLaTeX/BibTeX workflow. The
  editable source is report/report.tex, report/preamble.tex, report/cover.tex,
  eleven files under report/sections/ and report/references.bib. The previous
  Markdown is explicitly labelled as legacy and is no longer a build input.
- Typeset six mathematical displays, including the cell definition, parabola,
  circle-event height, neighbour half-plane, circumcentre precision condition
  and validation bound. Python excerpts use Courier New 9.5 pt, restrained
  syntax highlighting, numbered lines and listing captions. File paths use
  separate inline code styling.
- Regenerated original report figures with consistent serif typography and
  physical sizes suitable for the page. Benchmark values were read from the
  existing measured JSON; no benchmark results were invented or remeasured.
  The real native GUI capture was retained unchanged.
- Actual toolchain failures: Windows MiKTeX was installed but its user setup
  was incomplete. Debian had the LuaLaTeX binary but lacked luaotfload font
  support; the initial compiler error is preserved. Downloaded the matching
  Debian texlive-luatex package and unpacked it locally, without sudo or system
  installation. A first font-cache build on the Windows share timed out;
  moving only the temporary dependency/font cache into the Debian user cache
  resolved it. tools/bootstrap_tex_debian.sh makes that preparation repeatable.
- Verification: tools/build_report.py --wsl Debian completed LaTeX, BibTeX and
  two subsequent LaTeX passes. The final log has zero overfull boxes and no
  unresolved citations. A harmless epstopdf warning states that shell escape is
  disabled; this report uses PNG assets and needs no EPS conversion.
- Visual review caught a cover footer spilling onto a second page, awkward
  filename wrapping, and overly long inline conditions. Corrected these and
  inspected all 21 final rendered pages: one cover, two navigation pages,
  sixteen body pages and two appendices. All eight figures, five tables, six
  equations and two code listings were checked. A4 dimensions, searchable text,
  embedded font families, PDF author and cover identity were verified.
- Updated the editing guide, source listing, checklist and package builder.
  LaTeX sections, bibliography and figure assets are included in 01_Report.
  Archive naming uses the owner's supplied identity, and source metadata
  explicitly reports uncommitted working files instead of implying a base
  commit contains them. Current review-package verification is recorded
  separately in evidence/package-audit.json.
- Scope: production algorithm and its 86-test suite were unchanged by this
  presentation work. The recorded 86-pass result remains the prior actual run;
  the LaTeX compiler and figure-generation commands above were executed here.
  Owner reflection/review, genuine AI captures and narrated video remain pending.

## 17 November 2026 Owner review, plan disclosure and actual Pi contribution

- Purpose: continue the owner walkthrough, complete the AI plan disclosure,
  and involve Pi at the owner's explicit request. The owner confirmed ChatGPT
  Plus and requested GPT-6.1 as Pi's default model.
- Owner review: the triangle example, beach-line ordering, event generations,
  sweep-neighbour clipping and all seven genuine problem records were explained
  in chat. The owner confirmed understanding during the guided review. This
  does not claim an independently narrated demonstration or completed PDF review.
- Environment: non-login Debian shells did not locate Pi; the interactive
  shell initialized its existing fnm environment and located Pi 0.86.0.
  Model discovery listed openai-codex/gpt-6.1-sol, and the credential-readiness
  check returned ready with OAuth. No credential value was displayed or copied.
- Configuration: changed only defaultProvider/defaultModel in Pi's existing
  ~/.pi/agent/settings.json, preserving other settings. The previous settings
  were saved as settings.before-fortune-gpt61-2026-11-17.json in that directory.
  Readback confirmed openai-codex/gpt-6.1-sol.
- Actual Pi prompt: review circle-event invalidation and stable arc identity,
  identify genuine coverage gaps, and generate four executable pytest tests.
  Pi received the relevant source and existing tests with tools disabled. The
  prompt, raw JSON stream, persistent session, exact response and original test
  proposal are retained under evidence/pi-review-2026-11-17/.
- Pi output: no confirmed production defect; four coverage gaps involving
  superseded live predictions with the same defining site IDs, delayed events
  for removed arcs, deep AVL-successor identity, and exact heap-priority ties.
  The desktop assistant reviewed the proposed code, adopted it in
  tests/test_pi_regressions.py and applied Ruff formatting. Production source
  and algorithm dependencies were unchanged.
- Verification: all four proposed tests passed on their first run in 0.33 s.
  After formatting, the full native Windows suite passed 86 tests in 5.43 s.
  Ruff checks of src/tests and the new test's format check passed. The previous
  82-test JUnit result is preserved; evidence/tests-current.xml is the new run.
  These are desktop-executed checks; Pi did not execute tests in its invocation.
- Disclosure: owner-metadata.json, README, evidence register and report source
  now distinguish the initial desktop implementation from Pi's actual
  17 November review/test generation. ChatGPT Plus is owner-confirmed. The
  authentic screenshots, personal reflection/review and narration remain owner
  tasks; no generated transcript is presented as a captured interaction image.
- Report verification: rebuilt the searchable A4 PDF with 19 pages, including
  16 body pages. Inspected all seven changed rendered pages; the other twelve
  were pixel-identical to the previously reviewed PDF. Page budgets, required
  section headings, updated plan/model disclosure and the 86-test count passed.
- The existing ZIP remains the earlier review snapshot. Regenerate it during
  the final packaging step after incorporating the owner's remaining evidence.

## 16 November 2026 Owner interactive review

- Subsequent owner confirmation: found the five CSV rows for cell 0 and verified
  that its last next endpoint matches its first vertex.
- Owner then ran the automated suite in their terminal and reported
  `82 passed in 5.14s`. This is owner-reported review evidence, not a new assistant
  test run. The test-execution checklist item is now complete.

- The owner opened the interactive program, inserted five sites and computed
  the diagram. Their supplied screenshot shows five labelled cells and seven
  visible clipped edges.
- The owner then clicked Export and reported the success message. The assistant
  checked that output/review.png, review.csv and review.json exist and are nonempty.
- JSON confirms five input sites, five cells and seven clipped edges. The first
  cell has five ordered vertices, with the CSV's final next endpoint closing it.
- Only the confirmed interactive-run/export checklist item is marked complete.
  Owner test execution, further understanding, report review and personal evidence
  remain pending.

Records use the actual working date, GMT+8. Git milestone dates follow the
owner's schedule in docs/history.md. Only executed checks count as results.
AI assistance: this desktop assistant and Pi. Pi was initially inspected only;
its actual 17 November review and test-generation contribution is recorded above.

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
