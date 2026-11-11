# Actual Pi contribution, 17 November 2026

The owner requested actual Pi participation and GPT-6.1 as its saved default.
Pi 0.86.0 in Debian WSL used provider `openai-codex`, model `gpt-6.1-sol`, and
its existing OAuth sign-in. No credentials were included in these records.

## Contribution and scope

The prompt attached the event queue, circle detection, sweep, geometry and AVL
modules, plus existing event/AVL tests. Pi ran with tools, extensions, skills and
context-file discovery disabled. It reviewed only the supplied context and
generated four tests; it did not execute commands or edit production files.
It reported coverage gaps, not a confirmed production defect.

The desktop assistant reviewed the proposal, added it as
`tests/test_pi_regressions.py`, applied Ruff formatting and executed verification.
AST comparison confirms that the adopted module differs from the original
proposal only in formatting.

## Retained evidence

- `prompt.md`: actual review request.
- `session-output.jsonl` and `sessions/`: actual Pi event stream and session.
- `response.md`: exact final response extracted from that stream.
- `proposed_test_pi_regressions.py`: original generated Python block.
- `session-summary.json`: actual provider/model and generated test names.
- `configuration.json`: saved-default change and backup location, without secrets.
- `tests-targeted.xml`: four tests passed on their first execution in 0.33 s.
- `verification.json`: full 86-test result, AST comparison and report checks.
- `../tests-current.xml`: full native Windows run, 86 passed in 5.43 s.
- `../tests-before-pi-2026-11-17.xml`: preserved original 82-test JUnit output.

The four regressions cover superseded live predictions despite unchanged site
IDs, delayed delivery after arc removal, deep-successor object identity during
AVL deletion, and stable exact heap-priority ties across interleaved insertion.
The production Fortune implementation and benchmarked algorithm were unchanged.

This transcript is genuine machine-readable collaboration evidence. It is not
an app screenshot; the owner's two real interaction captures remain pending.
