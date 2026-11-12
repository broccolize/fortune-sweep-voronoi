# Optional pointer-following sweep replay

This feature is isolated on `codex/sweep-animation`. The primary project folder,
reviewed PDF and submission ZIP are unchanged. The report files copied into this
branch describe the baseline; incorporate the optional viewer into the report
and rebuild the submission only if the feature is selected for inclusion.

## Try the default viewer

In this session's primary project folder, run:

```powershell
.\tmp\worktrees\sweep-animation\run.bat --animate --input examples\sites.txt --bbox 0 0 1 1
```

In a checkout of the feature branch itself:

```powershell
.\run.bat --animate --input examples\sites.txt --bbox 0 0 1 1
.\run.bat --animate --random 50 --seed 2026
```

The viewer opens in the default browser. Move the pointer over the diagram:
the white sweep line follows without holding a button. Click to freeze/resume,
or use Position, Play, Next event, Reset and Finish. H displays help. Space
plays/pauses, Right steps one actual heap entry, R resets and E finishes.

The main point-entry window also opens this viewer through Animate. Add or
change sites there and reopen the replay to construct a new input. Pointer
movement in the browser selects a sweep state for the fixed input; it does not
insert sites or recompute the diagram. Save PNG downloads a canvas image through
the browser. CSV/JSON and normal PNG/SVG exports remain in batch/Compute mode.

Use `--output output\my-replay.html` to retain the self-contained HTML. It has
no external scripts, fonts, libraries or network requests and runs offline.
The earlier Matplotlib inspector is available for comparison:

```powershell
.\run.bat --animate --animation-backend matplotlib --input examples\sites.txt --bbox 0 0 1 1
```

## Why the first version was slow

The first implementation cleared both Matplotlib axes and rebuilt artists,
labels, queue text and widgets for every frame. The 50-site Agg measurement was
234.36 ms per redraw while advancing the event model took about 0.007 ms.
Painting, rather than Fortune construction, was the bottleneck. Its fixed
per-frame event subdivisions also made playback slow down with rendering.

The retained Matplotlib version now uses persistent artists, cached background
layers, bounded text bitmap caching, dirty-region blits, time-based playback and
a bounded checkpoint index. Its native Tk test reached about 44.5 timer updates
per second. The owner still found its interaction less fluid than pointer-following
web examples, so Canvas became the default optional renderer.

## How the Canvas version stays fast and faithful

Python runs the actual `FortuneSweep.step()` handlers once and records immutable
arc orders, heap previews, stale flags, vertices and edge-attachment times.
The browser chooses the appropriate event state by binary search. It evaluates
only presentation geometry and draws parabolas as exact quadratic Bezier curves.
There is no Python call or algorithm run for each pointer movement. No existing
Voronoi or Delaunay implementation is used.

The core batch constructor retains its O(n log n) time / O(n) space target. The
optional educational export deliberately trades memory for immediate seeking:
recording arc orders across events can use O(n^2) data in the worst case. It is
limited to 200 distinct sites and is excluded from construction benchmarks. The
200-site example HTML was about 669 kB. Exactly collinear inputs show the genuine
sorted-neighbour/direct-bisector special case rather than a fabricated sweep.

## Verification

- Full local suite: **139 passed**. Raw result: `evidence/tests-current.xml`.
- A wheel build included both HTML/JS assets; an isolated unpacked-wheel import
  generated a standalone replay. See `evidence/animation-wheel-audit.json`.
- Snapshot tests compare every recorded state with an independent replay of
  the Python event engine, including stale entries and required degeneracies.
- Node cross-checks JavaScript drawing geometry against Python for 100 cases.
- A source-level DOM event test moves the pointer without a pressed-button
  property and checks the expected sweep coordinates and event progression.
- Browser checks exercised positioning, continuous playback, pointer movement,
  the 200-site input and Save PNG. No page-console errors were reported.
- The downloaded 752 x 469 PNG and an actual browser screenshot are retained
  as `evidence/canvas-export.png` and `evidence/canvas-preview.jpg`.

| Browser case | Rolling RAF rate | Median canvas draw |
| --- | ---: | ---: |
| 50 sites | 120.0 Hz | 1.4 ms |
| 200 sites | 120.0 Hz | 2.4 ms |

These are observations from the visible in-app browser at 602 x 375 CSS pixels
(752 x 469 backing pixels). They are not display-scanout measurements or a promise
for every machine. Raw diagnostics are in
`results/animation-preview/render-browser.json`. Earlier Matplotlib profiles
and the native timer measurement are retained separately in that folder.

Reproduce the Matplotlib CPU/native comparisons with `tools/profile_replay.py`
and `tools/profile_replay_tk.py`. The browser displays its live FPS on the canvas
and its measured drawing time in the desktop header. The ordinary batch
benchmarks and stress records remain separate from rendering measurements.
