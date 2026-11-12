# Evidence Register

On the optional animation branch, current validation is 139 tests; Canvas
measurements and screenshots are additional feature evidence. The copied report,
AI captures, construction benchmarks and earlier CI records remain baseline
artifacts. The primary working folder and review ZIP are unchanged.

Initial implementation date 10 November 2026; owner review and Pi contribution
continued on 16-17 November 2026, GMT+8. Project scope is personal, with the
supplied assignment as a quality benchmark.

## Tool disclosure

- ChatGPT desktop app, Windows package OpenAI.Codex 26.1029.7803.0, verified via
  Windows package metadata. Owner-reported model: GPT-6.1.
- Subscription plan: ChatGPT Plus, confirmed by the owner on 17 November 2026
  and recorded in owner-metadata.json.
- The first owner-provided interaction capture visibly labels the selected
  desktop model GPT-6.1 Sol Max. This is retained as the observed UI label;
  GPT-6.1 remains the owner-reported model family.
- Pi `@earendil-works/pi-coding-agent` 0.86.0 on Debian 13.7 / WSL 2 used
  provider openai-codex and model gpt-6.1-sol on 17 November 2026. It reviewed
  event/arc invariants and generated four pytest regressions. The desktop
  assistant checked the proposals, applied formatting and executed them. Pi's
  invocation had no tools and made no test-execution claim.
- The owner's additional Pi captures show tool-enabled reviews of the actual
  source and retained tiny-cell failure, plus `cmd.exe /c test.bat -q` reporting
  `86 passed in 7.09s`. The footer visibly selects `openai-codex/gpt-6.1-sol`
  with `xhigh` thinking. This is a separate run from the desktop 5.43s JUnit
  result, not a construction benchmark. A follow-up search failed with exit
  code 2, after pytest passed; Pi then read tests/validation.py. Both are visible.
- Pi used its existing OAuth sign-in. No separate Pi subscription plan is
  inferred. Only the desktop assistant and Pi contributed AI work.
- The owner separately reports inspecting outputs, editing code and rerunning
  tests using Pi. These personal debugging activities are described in the
  reflection. The new captures substantiate the separate review/test run;
  they do not establish that a particular production fix was made by the owner.

| ID | Evidence | Location and status |
| --- | --- | --- |
| E01 | Specification checklist | docs/requirements.md |
| E02 | Actual development record | devlog.md and Git log |
| E03 | Substantive AI interaction 1 | Present and embedded: evidence/ai-interaction-1.png; ChatGPT invariant review, Figure 9; provenance in ai-interaction-1.json |
| E04 | Substantive AI interaction 2 | Present and embedded: evidence/ai-interaction-2.png plus pi-tiny-cell-code-continuation.png; Pi tiny-cell review, Figure 12; provenance in ai-interaction-2.json |
| E05 | General program output | figures/general.png, examples/batch.png |
| E06 | Annotated degenerate outputs | figures/degenerate-1.png and degenerate-2.png |
| E07 | Automated validation | evidence/tests-current.xml: 139 passing on this feature branch; original 82-test result preserved in evidence/tests-before-pi-2026-11-17.xml |
| E08 | Timing, memory and scaling | results/benchmark.json and figures/scaling.png |
| E09 | Architecture and beach-line illustrations | figures/architecture.png, beachline.png |
| E10 | Genuine problems and retained failures | docs/problems.md and initial failure files |
| E11 | Personal narrated walkthrough | Owner recording pending: demo/walkthrough.mp4 |
| E12 | Native Windows GUI Export | evidence/gui-native.png and examples/interactive.* |
| E13 | Clean install and package execution | evidence/clean-install-summary.json and clean-install-tests.xml |
| E14 | Full stress including largest vertices | evidence/stress-final.json |
| E15 | Searchable PDF and layout | report/report.pdf and evidence/report-layout.json |
| E16 | Genuine Pi review and generated tests | evidence/pi-review-2026-11-17/: prompt, response, raw session and targeted results; tests/test_pi_regressions.py |
| E17 | Actual LaTeX build and visual review | report/report.tex, report/sections/, report/references.bib; evidence/report-build.log and report-latex-audit.json; 26 pages including 16 body pages |
| E18 | Owner-supplied personal reflection | docs/personal-reflection-notes.md; Section 8; Heunis learning article cited in the bibliography |

## Owner-provided screenshots, received 17 November 2026

All seven original PNGs are preserved byte-for-byte. SHA-256, dimensions, roles
and the original filenames are in ai-interaction-1.json and
pi-screenshots-2026-11-17.json. Appendix B presents the complete captures;
landscape layout changes the page orientation, not the source pixels.

| Report figure | Original in evidence/ | Context |
| --- | --- | --- |
| 9 | ai-interaction-1.png | ChatGPT prompt and explanation of the AVL sequence and generation guard; selected model label visible |
| 10 | pi-environment.png | Pi 0.86.0 startup in the project directory; environment context, not a substantive exchange by itself |
| 11 | pi-interaction-invariants.png | Pi prompt, reads of the actual modules and invariant explanation |
| 12 | ai-interaction-2.png; pi-tiny-cell-code-continuation.png | Pi prompt, retained failure review, exact-topology correction and regression excerpt; the small image is the response continuation |
| 13 | pi-interaction-tests.png | Test prompt, real command and 86/7.09s output, later inspection-search error and recovery; model footer visible |
| 14 | pi-tests-summary.png | Response continuation describing the result, nearest-site/empty-circle checks and sampling limit |

These are current review/verification exchanges. They do not purport to show
the original development dates or an earlier debugging interaction. The test
PNG is retained as the observed result; it is not converted into a supposed
JUnit file. The preceding desktop JUnit result and measured benchmarks retain
their actual values and provenance.

A comparison of all 21 Python files under src/ and tests/ found the bytes
unchanged from the preceding review ZIP. That corroborates the current source
state; it does not reconstruct every activity performed in the owner's Pi
session. The red inspection error remains visible and is not labelled as a
pytest failure. The startup update banner is not evidence of an installed update.

The screenshot requirements are complete. The owner still needs to review the
report, demonstrate understanding and record the personal narration. The plan
is confirmed as ChatGPT Plus. See REVIEW_CHECKLIST.md and demo/script.md.

## Optional animation evidence

- `docs/animation.md`: controls, architecture, complexity trade-off and measured scope.
- `results/animation-preview/render-browser.json`: real browser diagnostics,
  position/pointer checks, console results and downloaded-file path.
- `evidence/canvas-preview.jpg`: actual browser capture, not an AI-conversation image.
- `evidence/canvas-export.png`: actual PNG obtained using the browser Save PNG control.
- `evidence/animation-canvas-tests.xml`: initial Canvas check, including a Node
  test-harness syntax failure. Corrected checks and pointer-event verification
  are retained in the subsequent Canvas XML files.
- `evidence/animation-fast-text-tests.xml`: seven real failures caused by the
  installed Matplotlib default line-spacing value `auto`; fixed and retested.
- `evidence/animation-checkpoint-tests.xml`: real counter-copy failures; serial
  reconstruction from the queue push count fixed the clone, with independence
  and future-order regressions added.

The owner said the newly created pointer-controlled viewer looked good. This
feedback approves the preview's presentation; no merge or completed personal
recording/review is inferred from it.
