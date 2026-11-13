# Final Review and Recording

The approved Canvas viewer is included in main. The software and technical draft
are ready for review. This checklist distinguishes completed checks from your
final reading and narrated recording. It is not a claim of a grade.

## 1 Run and understand the program

- [ ] Open README.md and follow the Windows quick start.
- [x] Run `test.bat -q`; confirm the current passing count from the actual output.
  Owner reported `82 passed in 5.14s` on 16 November 2026. On 17 November,
  the owner supplied genuine Pi execution captures: `86 passed in 7.09s`.
- [x] Run the nine-site batch example and inspect PNG, CSV and JSON.
  Owner supplied its statistics and confirmed seeing all three outputs.
- [x] Start `run.bat --interactive`, insert points, Compute and Export.
  Confirmed 16 November 2026: owner supplied the five-site diagram and Export
  success message; output/review.png, review.csv and review.json were checked.
- [ ] Read docs/walkthrough.md and trace the triangle example yourself.
- [ ] Explain the AVL beach-line invariant and circle-event generation checks.
- [ ] Explain why final cells use only sweep-generated neighbour constraints.
- [ ] Read docs/problems.md, including the late tiny-cell regression and fix.
- [x] Approve and include the pointer-controlled Canvas viewer in main.
  Owner authorized integration on 18 November 2026. Use `run.bat --animate`
  or Animate in the point-entry window; the feature-worktree path is no longer needed.
- [x] Integrated main test suite: 139 passed in 14.48s on 18 November 2026.

## 2 Review the report

- [ ] Read report/report.pdf and its editable LaTeX source report/report.tex
  and report/sections/. Shared formatting is in report/preamble.tex.
- [ ] Check that explanations match your understanding of the actual code.
- [ ] Review all five main problem analyses, the real retained failures and fixes.
- [ ] Review the measurement scope and raw results/benchmark.json.
  The updated construction medians are 0.08210 / 0.66062 / 6.66119 seconds.
  Section 4 and Appendix C explain the replay and its separate rendering measurements.
- [x] Add your personal observations to the critical reflection; do not claim
  experiences or checks you have not had or performed.
  Owner supplied and clarified their learning, Pi debugging workflow and
  verification takeaway on 17 November 2026. Incorporated into Section 8 with
  the learning article cited. Reading and approving the final wording remains
  part of the report-review item above.
- [x] Confirm your selected model is GPT-6.1 and fill subscription_plan in
  owner-metadata.json with the actual plan. Update Section 2 of the report.
  Owner confirmed ChatGPT Plus on 17 November 2026. Section 2 also records Pi's
  actual GPT-6.1 review and four generated regression tests from that date.

## 3 Supply genuine AI interaction evidence

- [x] Capture a real substantive prompt and response about the architecture or invariant.
  Owner supplied ai-interaction-1.png on 17 November 2026: current ChatGPT
  review of AVL ordering and generation-based circle-event invalidation.
- [x] Capture a second real interaction about a failing test and its correction.
  Owner supplied Pi's review of the retained tiny-cell failure and exact-topology
  correction, including the code continuation, on 17 November 2026.
- [x] Save originals as evidence/ai-interaction-1.png and evidence/ai-interaction-2.png.
  All six additional Pi originals are preserved unchanged with SHA-256 records.
- [x] Keep prompt and response legible, with real context; do not draw mock conversations.
- [x] Add captions/context to docs/evidence.md and insert them into the editable report.
  Appendix B contains the ChatGPT capture and all six Pi images. Wide terminal
  captures use landscape pages. The final report is rebuilt and visually checked.

Screenshots must come from the actual app. This assistant did not automate the
ChatGPT interface to collect them. The code, failure records and this chat can
help you choose which real interactions to capture.

## 4 Record your demonstration

- [ ] Rehearse demo/script.md and use demo/recording-checklist.md.
- [ ] Record your own audible narration, below five minutes.
- [ ] Show batch and interactive modes, architecture, both invariants and three
  actual problems or design decisions.
- [ ] Show the pointer-controlled replay and explain that it presents recorded
  Python event states, with a 200-site cap separate from normal construction.
- [ ] Play the recording all the way through and check readable text and audio.
- [ ] Save it as demo/walkthrough.mp4; it is excluded from Git and added to the ZIP.

## 5 Rebuild and review the package

- [x] Rebuild and visually check the technical report: 28 pages, 16 body pages,
  with the included viewer and real evidence. Rebuild again if you edit its text.
- [x] Prepare the review ZIP using tools/package_project.py; rebuild after adding video.
- [x] Check required folders, CRC and the completeness manifest. It deliberately
  reports the missing personal video and pending owner review.
- [x] Verify the 03_Executable launcher, installed Canvas assets and 139 tests in
  the extracted package's separate environment.
- [ ] Check GitHub's latest Actions run and compare the latest source revision.
- [ ] After all checks and personal evidence are complete, set owner_review_complete
  to true in owner-metadata.json and rebuild. The manifest will still report missing
  evidence rather than treating this flag alone as completion.

The cover and archive naming use the owner's provided identity:
Mineth Lohiru Ariyarathna, 2024380145, Computer Geometry. The archive remains a
review copy until the personal report/package review and narrated video are
complete. Existing AI screenshots and subscription disclosure are already supplied.
