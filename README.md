# Fortune sweep Voronoi diagrams

A from-scratch implementation of Fortune's sweep-line algorithm for planar point sites. An AVL beach line and a heap event queue generate Voronoi adjacency; neighbour half-planes form ordered cells inside a clipping rectangle. The construction core uses the Python standard library. SciPy is confined to independent validation.

Computational Geometry major assignment by **Mineth Lohiru Ariyarathna**, student ID **2024380145**.

## Features

- Coordinate-file and seeded-random batch input, plus click-to-add interactive input.
- Ordered clipped polygons, original input-index groups, and explicit segment/ray/line exports in CSV and JSON.
- Duplicate, collinear, equal-height, cocircular and nearly coincident input handling.
- Static plots and an interactive Delaunay checkbox; exactly cocircular faces use a deterministic fan triangulation.
- Offline Canvas sweep replay with pointer following, playback and event stepping; an alternative Matplotlib event inspector is also available.
- Independent area, ownership and empty-circle checks, a precision campaign, stress tests, and comparison with SciPy/Qhull and a separate exact clipping validator.

## Windows setup

Use Windows 10/11 x64 with **Python 3.12 or 3.14** available as `python`. The current local benchmark uses Python **3.14.7**; the earlier complete suite also ran with **3.12.14**. Install Python from the [official Windows downloads](https://www.python.org/downloads/windows/) if needed.

Open PowerShell in the repository folder:

If using the assignment ZIP, first enter `02_SourceCode`. Its `01_Report` sibling contains the PDF; `03_Executable\run.bat` is a wrapper for the same program, and `04_Demo` contains the demonstration assets supplied with that package.

```powershell
python --version
.\install.bat
.\run.bat --random 30 --seed 2026 --output output\random.png
```

`install.bat` creates `.venv` and installs the exact pins in `requirements.txt`. `run.bat` uses that environment and creates it automatically on first use if absent. Generated output folders are created when required.

| Dependency | Version | Purpose |
| --- | --- | --- |
| Matplotlib | 3.11.2 | Static plots and the desktop interface |
| NumPy | 2.5.4 | Plotting dependency and validation utilities |
| pytest | 9.2.0 | Automated tests |
| SciPy | 1.18.1 | Optional installation for the independent reference checks |
| Node.js | 24.22.1 | Additional JavaScript presentation tests; not needed to run the Python constructor or browser replay |
| Ruff | 0.17.4 | Optional code-style checks |

All Python transitive pins are in `requirements.txt`; `requirements-reference.txt` adds SciPy and `requirements-dev.txt` adds Ruff. No licence keys are required.

For Linux or WSL, `bash run.sh --random 30 --output output/random.png` creates `.venv-wsl` and runs the same source. Install the reference pins with `.venv-wsl/bin/python -m pip install -r requirements-reference.txt` and run `.venv-wsl/bin/python -m pytest -q` for validation. Interactive plotting requires a working graphical display; static output uses a noninteractive backend.

## Batch input and exports

```powershell
.\run.bat --input examples\sites.txt --bbox 0 0 1 1 --output output\sites.png --csv output\cells.csv --json output\diagram.json
.\run.bat --random 100 --seed 2026 --delaunay --no-labels --output output\dual.png
```

Add `--show` to display a batch plot. Without `--bbox`, file input uses a padded rectangle containing its sites; random input defaults to the unit square. `--seed` makes generated sites reproducible.

Files are UTF-8, with one `x y` or `x,y` pair per line. Blank lines and `#` comments are accepted:

```text
# Three distinct sites and one duplicate
0.1 0.2
0.8,0.2
0.5 0.9
0.1 0.2
```

Exact duplicates share one cell while retaining all original input indices. Distinct nearby sites are not deliberately merged. Non-finite coordinates, malformed input and unsupported precision ranges produce an error.

CSV rows preserve each cell's boundary order, next endpoint, neighbouring site and edge kind. JSON adds complete statistics, circle-vertex defining sites, ray origin/direction data, Delaunay edges and the degeneracy policy. A clipped-away site can have an empty output polygon. An unbounded full-plane cell can still have a closed clipped polygon.

## Interactive input

```powershell
.\run.bat --interactive --output output\interactive.png
.\run.bat --interactive --input examples\sites.txt --delaunay --output output\loaded.png
```

Click to add sites. **Compute**, or a double-click, builds the cells. **Delaunay** toggles the dual overlay. **Clear** removes the sites. **Export** saves PNG, CSV and JSON beside the chosen output path. **Animate** opens a replay of the same points.

An empty click canvas starts with the unit square. Supplied file coordinates infer their own view unless an explicit `--bbox` is given.

## Sweep replay

```powershell
.\run.bat --input examples\sites.txt --bbox 0 0 1 1 --animate --output output\sweep.html
.\run.bat --random 8 --seed 2026 --animate --animation-backend matplotlib --output output\inspector.png
```

The default viewer is a standalone HTML file opened in the browser. Move the pointer vertically to position the sweep; click to freeze or resume following. **Play**, **Next event**, **Reset** and **Finish** inspect the recorded Python event states. The beach line comes from the actual sweep engine.

Replay supports at most **200 distinct sites**. Its browser state history can use quadratic storage. Ordinary batch construction does not retain that history. Delaunay overlays are available in batch and point-entry views; CSV/JSON exports use batch mode rather than `--animate`.

## Tests and independent validation

For the complete suite, install the reference dependencies and [Node.js 24.22.1](https://nodejs.org/download/release/v24.22.1/). Reopen PowerShell after installing Node so it is on `PATH`.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-reference.txt
node --version
.\test.bat -q
```

The complete suite contains **171 passing tests** when SciPy and Node are available. Pytest reports skips when either validation dependency is absent; quote the count actually shown for that run.

```powershell
# Independent library comparison and exact all-pairs clipping oracle
.\.venv\Scripts\python.exe tests\reference_compare\compare.py --output evidence\reference-comparison.json

# 800 deterministic precision configurations
.\.venv\Scripts\python.exe tools\check_precision.py --output evidence\precision-validation.json

# 300 random, 40 clustered, and large cases through 10,000 sites
.\.venv\Scripts\python.exe tools\stress.py --output evidence\final-stress.json

# Fresh environment, wheel installation, installed-package suite and exports
.\.venv\Scripts\python.exe tools\clean_check.py
```

The default reference suite checks **45 datasets**. **39** are fully resolved by SciPy; five minimal/collinear cases and one precision-limited near-cluster case are covered by the independent exact validator and recorded separately. The result includes seeds, inputs, tolerances and discrepancies. It does not count unsupported reference inputs as SciPy matches.

Optional style checks:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m ruff check src tests tools
```

## Benchmarks and figure reproduction

```powershell
.\.venv\Scripts\python.exe tools\benchmark.py --sizes 100 1000 10000 --repeat 3 --seed 2026 --out results\final-2026-11-18
.\.venv\Scripts\python.exe tools\make_figures.py --benchmark results\final-2026-11-18\benchmark.json
.\.venv\Scripts\python.exe tools\make_report_scaling.py
```

The retained current run uses Windows 11 x64, Python 3.14.7, seed 2026 and three timing repetitions per size:

| Sites | Median construction seconds | Python allocation peak MiB | Process peak MiB |
| ---: | ---: | ---: | ---: |
| 100 | 0.06103 | 0.70 | 25.02 |
| 1,000 | 0.61293 | 7.42 | 42.86 |
| 10,000 | 7.69296 | 65.31 | 218.48 |

Raw samples and environment metadata are in [`results/final-2026-11-18/benchmark.json`](results/final-2026-11-18/benchmark.json); the table is also supplied as CSV. The earlier measurement records are retained separately.
Use a different `--out` directory to retain an additional run without replacing these records.

Timing covers the full `construct()` call, including normalization, sweep, clipped cells and the dual graph. Input generation, plotting, export and validation are excluded. Memory is measured in fresh processes; Python allocations start after input generation, while process peaks include the interpreter and tracing overhead. These are measurements on this machine, not performance guarantees or a proof of asymptotic complexity.

## Report and source layout

The [main PDF report](report/report.pdf) includes the algorithm, seven problem investigations, current validation, AI-interaction evidence, Git dates/descriptions and the other appendices. The [complete source listing](report/source_appendix.pdf) is a separate Appendix A supplement. The [archived implementation](report/implementation-snapshot.zip) preserves the editable source associated with both documents.

| Path | Contents |
| --- | --- |
| `src/fortune/` | Geometry, frame, AVL beach line, event sweep, clipping, exports and viewers |
| `tests/` | Structural, geometric, precision, interface, replay and reference tests |
| `tools/` | Measurements, figure generation and installation/package checks |
| `examples/` | Inputs and retained output examples |
| `results/` and `evidence/` | Raw measurements and verification records |
| `report/` | Editable LaTeX, Word cover, figures, data and source archive |

To rebuild the editable report, install LuaLaTeX or XeLaTeX with BibTeX and the packages used in `report/preamble.tex`, plus Times New Roman and Courier New. With the configured Debian WSL TeX installation:

```powershell
report\build.bat --wsl Debian
```

`report/build_snapshot.py` builds both PDFs and rebuilds the listing from the archived implementation so a later checkout cannot silently replace the printed source. The main volume has its own contents and continuous page numbering; the source supplement uses A-prefixed pages. The separate Python PDF-audit dependencies are pinned in `report/requirements.txt`.

## Packaging

The completed narrated demonstration is in `demo/walkthrough.mp4`. Build and verify the assignment package with:

```powershell
.\.venv\Scripts\python.exe tools\package_project.py
.\.venv\Scripts\python.exe tools\verify_package.py dist\CG_Assignment_2024380145_Mineth_Lohiru_Ariyarathna.zip
```

The video is included under `04_Demo` in the ZIP. Add `--exclude-recording` for a smaller source/report review copy. Recording workspaces, local editing notes, environments and credentials are excluded.

## Limits

The core targets O(n log n) arithmetic operations and O(n) construction records; exact fallback costs also depend on operand size. It uses filtered predicates, rational decisions in uncertain cases, fixed 80-digit construction fallbacks and rounded output coordinates. It is not a certified exact-geometry kernel. Unsupported coordinate ranges are rejected explicitly. Exactly cocircular triangulations can differ from other valid implementations because of the deterministic fan policy. Replay has its own 200-site and storage limits.

AI assistance for the program covered specification extraction, architecture, implementation, tests and measurements; the report records the tools and concrete interactions.
