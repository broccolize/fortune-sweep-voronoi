# Editing and building the LaTeX report

The authoritative source is **report.tex**. Text is divided among **sections/**;
shared formatting is in **preamble.tex**; cover details are in **cover.tex**;
numbered references are in **references.bib**.

## Build on this Windows computer

From the project root:

    .venv\Scripts\python tools\build_report.py --wsl Debian

Or run:

    report\build.bat --wsl Debian

This uses the already installed Debian LuaLaTeX and BibTeX, reads the Windows
Times New Roman/Courier New fonts, and writes report/report.pdf. Build files
stay under tmp/latex-build/. Actual logs are retained in evidence/report-build.log
and evidence/report-build.json.

This Debian installation originally lacked the LuaLaTeX font-support package.
It was prepared locally under tmp/tex-deps/, without sudo or system changes.
If that temporary dependency directory is removed, recreate it from the root:

    wsl -d Debian -- bash tools/bootstrap_tex_debian.sh

Alternatively, use a complete TeX Live installation including texlive-luatex.

With a configured native MiKTeX or TeX Live installation:

    python tools/build_report.py

The script tries native LuaLaTeX/XeLaTeX and falls back to Debian WSL on Windows.
It runs LaTeX, BibTeX, then LaTeX twice more for citations and navigation.

With a complete TeX installation, the self-contained 01_Report folder in the
review package can also be compiled directly:

    lualatex report.tex
    bibtex report
    lualatex report.tex
    lualatex report.tex

## What to edit

- Main text: the matching file under sections/.
- Font, margins, spacing, heading/caption/table/code styles: preamble.tex.
- Author and cover fields: cover.tex.
- Reference entries: references.bib; cite them using \cite{fortune1987}.
- Equations: \( ... \) inline, or equation/align environments for displays.
- Code: lstlisting environments; Python highlighting and numbering are configured.
- Figure captions and sizes: the matching figure environment. Original images
  are in ../figures/; genuine GUI and AI captures are in ../evidence/.
- AI evidence: sections/appendix-b.tex. Landscape pages preserve the original
  terminal captures; the originals and their checksums must be kept unchanged.
  In the self-contained 01_Report package, these assets are also in figures/.

Compile after editing. TeX numbers sections, equations, figures, tables and
listings and updates contents, figure/table lists and references automatically.
The body remains Times New Roman 12 pt with 1.5 line spacing. The source is
editable in VS Code, TeXstudio or any text editor.

The checked PDF has 26 pages: one cover, two navigation pages, 16 body pages and
seven appendix pages. Five evidence pages use A4 landscape orientation for
legible terminal captures; the main report remains portrait. Automatic numbering will update when the source is edited.

The older Markdown file is retained as a legacy draft. It is no longer used to
build the PDF; editing it does not change the LaTeX report.
