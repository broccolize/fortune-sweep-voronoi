# Report format and editable source

The supplied specification's Section 6 requires English searchable PDF, A4,
25 mm margins, Times New Roman 12 pt and 1.5 line spacing. Code may use
Courier New/Consolas at 9-10 pt. Sections, figures and tables must be numbered,
captions must be present, and citations must use one consistent numbered or APA
style. The nine prescribed main sections and at least ten body pages are mandatory.
The supplied cover has identity, subject and date fields.

The owner's requested LaTeX conversion uses those settings. The cover records
Mineth Lohiru Ariyarathna, student ID 2024380145, course Computer Geometry.
The source is report/report.tex and report/sections/, not the legacy Markdown.

Presentation additions are editorial choices, not additional specification
requirements: contents and figure/table lists, PDF bookmarks, running headers,
horizontal-rule tables, numbered mathematical displays, and syntax-highlighted
code with line numbers. Shared formatting is centralized in report/preamble.tex.
References are in report/references.bib and use the numbered IEEE BibTeX style.

Use report/README.md for editing and the tested build command. Do not substitute
pdfLaTeX for LuaLaTeX/XeLaTeX: the specified Windows TrueType fonts require
fontspec. On this computer the existing Debian compiler uses locally prepared
Lua font support; the global TeX installation and system packages were unchanged.

The report remains a review draft while the narrated demonstration and final
owner review are pending. Owner observations are incorporated into Section 8;
seven genuine ChatGPT/Pi originals are reproduced in Appendix B, using landscape
pages for the wide terminal captures. Appendix C records the included Canvas
viewer and the scope of its rendering measurements. Current page counts and
checksums are in evidence/report-latex-audit.json; retained build, provenance
and visual-review audits document the actual checks.
