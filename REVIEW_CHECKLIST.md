# Start Here When You Return

The software is implemented and tested; this checklist covers your review and
the evidence that requires your participation. It is not a claim of a grade.

## 1 Run and understand the program

- [ ] Open README.md and follow the Windows quick start.
- [ ] Run `test.bat -q`; confirm the current passing count from the actual output.
- [ ] Run the nine-site batch example and inspect PNG, CSV and JSON.
- [ ] Start `run.bat --interactive`, insert points, Compute and Export.
- [ ] Read docs/walkthrough.md and trace the triangle example yourself.
- [ ] Explain the AVL beach-line invariant and circle-event generation checks.
- [ ] Explain why final cells use only sweep-generated neighbour constraints.
- [ ] Read docs/problems.md, including the late tiny-cell regression and fix.

## 2 Review the report

- [ ] Read report/report.pdf and its editable report/report.md source.
- [ ] Check that explanations match your understanding of the actual code.
- [ ] Review all five main problem analyses, the real retained failures and fixes.
- [ ] Review the measurement scope and raw results/benchmark.json.
- [ ] Add your personal observations to the critical reflection; do not claim
  experiences or checks you have not had or performed.
- [ ] Confirm your selected model is GPT-6.1 and fill subscription_plan in
  owner-metadata.json with the actual plan. Update Section 2 of the report.

## 3 Supply genuine AI interaction evidence

- [ ] Capture a real substantive prompt and response about the architecture or invariant.
- [ ] Capture a second real interaction about a failing test and its correction.
- [ ] Save originals as evidence/ai-interaction-1.png and evidence/ai-interaction-2.png.
- [ ] Keep prompt and response legible, with real context; do not draw mock conversations.
- [ ] Add captions/context to docs/evidence.md and insert them into the editable report.

Screenshots must come from the actual app. This assistant did not automate the
ChatGPT interface to collect them. The code, failure records and this chat can
help you choose which real interactions to capture.

## 4 Record your demonstration

- [ ] Rehearse demo/script.md and use demo/recording-checklist.md.
- [ ] Record your own audible narration, below five minutes.
- [ ] Show batch and interactive modes, architecture, both invariants and three
  actual problems or design decisions.
- [ ] Play the recording all the way through and check readable text and audio.
- [ ] Save it as demo/walkthrough.mp4; it is excluded from Git and added to the ZIP.

## 5 Rebuild and review the package

- [ ] Rebuild the report after your text/screenshots/metadata changes.
- [ ] Run `.venv\Scripts\python tools\package_project.py`.
- [ ] Check submission/completeness.json and inspect the ZIP contents.
- [ ] Verify the launcher in 03_Executable and root README.txt.
- [ ] Check GitHub's latest Actions run and compare the latest source revision.
- [ ] After all checks and personal evidence are complete, set owner_review_complete
  to true in owner-metadata.json and rebuild. The manifest will still report missing
  evidence rather than treating this flag alone as completion.

Because this is a personal project, the archive uses PERSONAL in the identifier
field. If you later use the package in an actual course, replace that field and
the cover details with your real required identity; follow that course's rules.
