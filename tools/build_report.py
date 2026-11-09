"""Build the editable Markdown report as a searchable A4 Times New Roman PDF.

Supports the small, explicit Markdown subset used by report/report.md. Emits
page budgets for layout review; does not silently shrink body text to fit.
"""

from pathlib import Path
import os
import re
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
    Preformatted,
    Table,
    TableStyle,
)
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "report" / "report.md"
OUT = ROOT / "report" / "report.pdf"
WIDTH = A4[0] - 5 * cm - 12
HEIGHT = A4[1] - 5 * cm - 12


def register_fonts():
    directory = Path(os.environ.get("FORTUNE_TNR_DIR", r"C:\Windows\Fonts"))
    for name, filename in [
        ("TNR", "times.ttf"),
        ("TNR-Bold", "timesbd.ttf"),
        ("TNR-Italic", "timesi.ttf"),
    ]:
        pdfmetrics.registerFont(TTFont(name, str(directory / filename)))
    pdfmetrics.registerFontFamily(
        "TNR", normal="TNR", bold="TNR-Bold", italic="TNR-Italic", boldItalic="TNR-Bold"
    )


def markup(text):
    return re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', escape(text))


def page_flowables(text, cover=False):
    normal = ParagraphStyle(
        "Body",
        fontName="TNR",
        fontSize=12,
        leading=18,
        spaceAfter=7,
        splitLongWords=True,
    )
    heading = ParagraphStyle(
        "Heading",
        parent=normal,
        fontName="TNR-Bold",
        fontSize=16,
        leading=21,
        spaceAfter=12,
        keepWithNext=True,
    )
    sub = ParagraphStyle(
        "Sub", parent=heading, fontSize=13, leading=18, spaceBefore=3, spaceAfter=8
    )
    caption = ParagraphStyle("Caption", parent=normal, spaceBefore=3, spaceAfter=10)
    centre = ParagraphStyle("Cover", parent=normal, alignment=TA_CENTER, spaceAfter=22)
    title = ParagraphStyle(
        "Title",
        parent=centre,
        fontName="TNR-Bold",
        fontSize=23,
        leading=29,
        spaceAfter=36,
    )
    code = ParagraphStyle(
        "Code", fontName="Courier", fontSize=9, leading=12, spaceBefore=4, spaceAfter=10
    )
    elements = []
    lines = text.strip().splitlines()
    i = 0
    if cover:
        elements.append(Spacer(1, 110))
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i])
                i += 1
            elements.append(Preformatted("\n".join(block), code))
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                parts = [p.strip() for p in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", p) for p in parts):
                    rows.append([Paragraph(markup(p), normal) for p in parts])
                i += 1
            count = len(rows[0])
            widths = (
                [WIDTH * 0.38, WIDTH * 0.62]
                if count == 2
                else [WIDTH * 0.62, WIDTH * 0.15, WIDTH * 0.23]
                if count == 3
                else [WIDTH / count] * count
            )
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9D9D9")),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E7EBF0")),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            elements.extend([table, Spacer(1, 5)])
            continue
        image = re.fullmatch(r"!\[([^]]+)\]\(([^)]+)\)", line)
        if image:
            path = (SOURCE.parent / image.group(2)).resolve()
            w, h = ImageReader(str(path)).getSize()
            target = min(WIDTH, 420)
            elements.append(Image(str(path), width=target, height=target * h / w))
            elements.append(Paragraph(markup(image.group(1)), caption))
            i += 1
            continue
        if line.startswith("# "):
            elements.append(Paragraph(markup(line[2:]), title if cover else heading))
            i += 1
            continue
        if line.startswith("## "):
            elements.append(Paragraph(markup(line[3:]), sub))
            i += 1
            continue
        paragraph = [line]
        i += 1
        while (
            i < len(lines)
            and lines[i].strip()
            and not lines[i].startswith(("#", "|", "```", "!["))
        ):
            paragraph.append(lines[i].strip())
            i += 1
        elements.append(
            Paragraph(markup(" ".join(paragraph)), centre if cover else normal)
        )
    return elements


def footer(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("TNR", 10)
    canvas.drawCentredString(A4[0] / 2, 1.3 * cm, str(doc.page - 1))
    canvas.restoreState()


def main():
    register_fonts()
    pages = SOURCE.read_text(encoding="utf-8").split("<!-- PAGE -->")
    story = []
    budgets = []
    for number, text in enumerate(pages):
        items = page_flowables(text, cover=number == 0)
        height = sum(
            f.wrap(WIDTH, 100000)[1]
            + getattr(f, "getSpaceBefore", lambda: 0)()
            + getattr(f, "getSpaceAfter", lambda: 0)()
            for f in items
        )
        # Modest figure resizing is allowed; body text always stays 12/18.
        images = [f for f in items if isinstance(f, Image)]
        if height > HEIGHT and images:
            reduction = min(
                height - HEIGHT + 8, sum(im.drawHeight for im in images) * 0.25
            )
            for im in images:
                factor = 1 - reduction / sum(item.drawHeight for item in images)
                im.drawWidth *= factor
                im.drawHeight *= factor
            height = sum(
                f.wrap(WIDTH, 100000)[1]
                + getattr(f, "getSpaceBefore", lambda: 0)()
                + getattr(f, "getSpaceAfter", lambda: 0)()
                for f in items
            )
        budgets.append(
            dict(
                source_page=number + 1,
                height_points=round(height, 1),
                available=round(HEIGHT, 1),
            )
        )
        if height > HEIGHT + 1:
            raise RuntimeError(
                f"Page {number + 1} exceeds budget: {height:.1f} > {HEIGHT:.1f}; edit prose/layout"
            )
        if number:
            story.append(PageBreak())
        story.extend(items)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        title="Fortune Sweep Line Voronoi Diagrams",
        author="broccolize",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    import json

    (ROOT / "evidence" / "report-layout.json").write_text(
        json.dumps(budgets, indent=2), encoding="utf-8"
    )
    listing = []
    sources = []
    for name in ("src", "tests", "tools"):
        sources.extend((ROOT / name).rglob("*.py"))
    sources.extend(ROOT.glob("*.bat"))
    sources.extend(ROOT.glob("*.sh"))
    sources.extend(
        [
            ROOT / "pyproject.toml",
            ROOT / "requirements.txt",
            ROOT / ".github" / "workflows" / "tests.yml",
        ]
    )
    for path in sorted(sources):
        listing.extend(
            [
                "=" * 78,
                str(path.relative_to(ROOT)),
                "=" * 78,
                path.read_text(encoding="utf-8"),
                "",
            ]
        )
    (ROOT / "report" / "source_listing.txt").write_text(
        "\n".join(listing), encoding="utf-8"
    )
    print(f"Wrote {OUT}; {len(pages)} pages including cover and appendix")


if __name__ == "__main__":
    main()
