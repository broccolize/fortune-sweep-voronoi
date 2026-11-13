"""Check the compiled report and optionally render numbered pages for visual QA."""

import argparse
import hashlib
import importlib.metadata
import io
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--dpi", type=int, default=105)
    args = parser.parse_args()
    pdf = ROOT / "report/report.pdf"
    reader = PdfReader(pdf)
    aux = (ROOT / "tmp/latex-build/report.aux").read_text(encoding="utf-8")
    labels = {
        name: (number, int(page))
        for name, number, page in re.findall(
            r"\\newlabel\{([^}]+)\}\{\{([^}]+)\}\{(\d+)\}", aux
        )
    }
    body = labels["last-main-page"][1]
    text = [page.extract_text() for page in reader.pages]
    fonts = {}
    for page in reader.pages:
        resources = page["/Resources"]
        font_refs = resources.get("/Font")
        if font_refs is None:
            continue
        for ref in font_refs.get_object().values():
            font = ref.get_object()
            children = font.get("/DescendantFonts", [font])
            for child in children:
                obj = child.get_object()
                descriptor = obj.get("/FontDescriptor", {})
                if hasattr(descriptor, "get_object"):
                    descriptor = descriptor.get_object()
                embedded = any(
                    k in descriptor for k in ("/FontFile", "/FontFile2", "/FontFile3")
                )
                fonts[str(obj.get("/BaseFont", font.get("/BaseFont")))] = embedded
    all_a4 = all(
        all(
            abs(a - b) < 1
            for a, b in zip(
                sorted(map(float, (p.mediabox.width, p.mediabox.height))),
                [595.276, 841.890],
            )
        )
        for p in reader.pages
    )
    unresolved = bool(re.search(r"\?\?|\b(?:TODO|TBD|PLACEHOLDER)\b", "\n".join(text)))
    build = json.loads((ROOT / "evidence/report-build.json").read_text())
    from PIL import Image

    embedded_images = set()
    for page in reader.pages:
        for item in page.images:
            stream = item.indirect_reference.get_object()
            # The high-level extractor can re-encode JPEGs. Decode the original
            # DCT stream to compare original pixels without another lossy save.
            if str(stream.get("/Filter")) == "/DCTDecode":
                picture = Image.open(io.BytesIO(stream.get_data())).convert("RGB")
            else:
                picture = item.image.convert("RGB")
            embedded_images.add(
                (picture.size, hashlib.sha256(picture.tobytes()).hexdigest())
            )
    screenshot_names = (
        "gui-native.png",
        "ai-interaction-1.png",
        "pi-environment.png",
        "pi-interaction-invariants.png",
        "ai-interaction-2.png",
        "pi-tiny-cell-code-continuation.png",
        "pi-interaction-tests.png",
        "pi-tests-summary.png",
        "canvas-preview.jpg",
    )
    screenshot_matches = {}
    for name in screenshot_names:
        with Image.open(ROOT / "evidence" / name) as original:
            picture = original.convert("RGB")
            key = (picture.size, hashlib.sha256(picture.tobytes()).hexdigest())
            screenshot_matches[name] = key in embedded_images
    summary = dict(
        actual_timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        report_engine="LuaLaTeX",
        pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
        pages=len(reader.pages),
        main_body_pages=body,
        section_pages={k: v[1] for k, v in labels.items() if k.startswith("sec:")},
        counts={
            prefix: sum(k.startswith(prefix + ":") for k in labels)
            for prefix in ("fig", "tab", "eq", "lst")
        },
        a4_all_pages=all_a4,
        body_font="Times New Roman 12 pt",
        body_spacing="1.5 (setspace onehalfspacing)",
        code_font="Courier New 9.5 pt; line numbers 9 pt",
        fonts_embedded=fonts,
        searchable_text=all(len(t.strip()) > 10 for t in text),
        unresolved_placeholders=unresolved,
        overflow_warnings=build["overfull_box_warnings"],
        owner_review_complete=json.loads((ROOT / "owner-metadata.json").read_text())[
            "owner_review_complete"
        ],
        source="report/report.tex",
        editable_sections=len(list((ROOT / "report/sections").glob("*.tex"))),
        bibliography_style="IEEE numbered (ieeetr)",
        bibliography_entries=len(re.findall(r"\\bibcite\{", aux)),
        embedded_screenshots_match_original_pixels=screenshot_matches,
        visual_review="Pending inspection of the newly rendered pages",
    )
    if args.render:
        import pypdfium2 as pdfium
        from PIL import Image, ImageDraw

        stamp = datetime.now(timezone(timedelta(hours=8)))
        out = ROOT / "tmp" / stamp.strftime("report-pages-%Y%m%d-%H%M%S")
        out.mkdir(parents=True, exist_ok=False)
        document = pdfium.PdfDocument(str(pdf))
        thumbs = []
        for index in range(len(document)):
            page = document[index]
            bitmap = page.render(scale=args.dpi / 72)
            im = bitmap.to_pil().convert("RGB")
            im.save(out / f"page-{index + 1:02d}.png")
            im.thumbnail((420, 595), Image.Resampling.LANCZOS)
            thumb = Image.new("RGB", (440, 630), "#e4e7eb")
            ImageDraw.Draw(thumb).text((10, 6), f"PDF page {index + 1}", fill="black")
            thumb.paste(im, ((440 - im.width) // 2, 27))
            thumbs.append(thumb)
            bitmap.close()
            page.close()
        document.close()
        for first in range(0, len(thumbs), 6):
            sheet = Image.new("RGB", (880, 1890), "#d4d9df")
            for offset, thumb in enumerate(thumbs[first : first + 6]):
                sheet.paste(thumb, ((offset % 2) * 440, (offset // 2) * 630))
            sheet.save(out / f"contact-{first // 6 + 1:02d}.png")
        summary["render_dpi"] = args.dpi
        summary["render_directory"] = str(out.relative_to(ROOT)).replace("\\", "/")
        summary["renderer"] = "pypdfium2 " + importlib.metadata.version("pypdfium2")
    assert body >= 10 and all_a4 and all(fonts.values())
    assert summary["searchable_text"] and not unresolved
    assert summary["overflow_warnings"] == 0
    assert all(screenshot_matches.values()), screenshot_matches
    for name in ("report-audit.json", "report-latex-audit.json", "report-layout.json"):
        (ROOT / "evidence" / name).write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {k: v for k, v in summary.items() if k != "fonts_embedded"}, indent=2
        )
    )


if __name__ == "__main__":
    main()
