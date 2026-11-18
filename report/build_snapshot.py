"""Build this report with its archived source listing, including test data.

Run through build.bat, or: python build_snapshot.py --wsl Debian
The construction application and project tools are never edited by this helper.
"""

import json
import sys
import types
from pathlib import Path
from zipfile import ZipFile

REPORT = Path(__file__).resolve().parent


def source_listing():
    paths = json.loads(
        (REPORT / "data/printed-source-files.json").read_text(encoding="utf-8")
    )
    blocks = []
    with ZipFile(REPORT / "implementation-snapshot.zip") as archive:
        for name in paths:
            text = archive.read(name).decode("utf-8").replace("\r\n", "\n")
            blocks.extend(["=" * 78, name, "=" * 78, text, ""])
    (REPORT / "source_listing.txt").write_text("\n".join(blocks), encoding="utf-8")


def main():
    source_listing()
    if sys.argv[1:] == ["--listing-only"]:
        return
    root = (
        REPORT.parent if (REPORT.parent / "tools/build_report.py").is_file() else REPORT
    )
    # The frozen builder is standard-library code and is supplied in the same
    # source archive, so an isolated editable report does not need a checkout.
    with ZipFile(REPORT / "implementation-snapshot.zip") as archive:
        code = archive.read("tools/build_report.py").decode("utf-8")
    builder = types.ModuleType("snapshot_report_builder")
    builder.__file__ = str(root / "tools/build_report.py")
    exec(compile(code, builder.__file__, "exec"), builder.__dict__)
    builder.source_listing = source_listing
    builder.main(["--report-dir", str(REPORT), *sys.argv[1:]])
    builder.main(
        [
            "--report-dir",
            str(REPORT),
            "--entry",
            "source_appendix.tex",
            "--skip-bibliography",
            *sys.argv[1:],
        ]
    )


if __name__ == "__main__":
    main()
