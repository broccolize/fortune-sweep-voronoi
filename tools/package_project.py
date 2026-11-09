"""Assemble the requested review ZIP without including environments or credentials."""

from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]

ROOT_README = r"""FORTUNE SWEEP VORONOI
Personal project, evaluated against the supplied course specification.

WINDOWS QUICK START
Install Python 3.12+ x64 (3.14.7 was tested) with Python on PATH.
Open 02_SourceCode and run install.bat once, then:
  run.bat --input examples\sites.txt --bbox 0 0 1 1 --output output\demo.png --csv output\cells.csv --json output\diagram.json
  run.bat --interactive
  test.bat -q
The launcher 03_Executable\run.bat calls the same source implementation.
Internet is required for the first pinned dependency installation.

REPRODUCE RESULTS FROM 02_SourceCode
  .venv\Scripts\python tools\stress.py
  .venv\Scripts\python tools\benchmark.py --sizes 100 1000 10000 --repeat 3 --seed 2026
  .venv\Scripts\python tools\make_figures.py
To rebuild the report, install report\requirements.txt and run tools\build_report.py.
The report builder uses the Windows Times New Roman fonts.
See 02_SourceCode\README.md for Linux/WSL instructions, output schema and limits.

PACKAGE CONTENTS
01_Report: searchable PDF, editable Markdown, source listing, report dependencies.
02_SourceCode: complete source, build/run files, docs, tests and measured evidence.
03_Executable: Windows run-script entry point and pinned dependency list.
04_Demo: input/output examples, narrated script and recording checklist.
tests: independent test suite (also included inside the self-contained source tree).
devlog.md: actual verification process and corrections.
completeness.json: required files, owner evidence and source revision.

REVIEW STATUS
The AI-produced software and report have executable evidence. Owner review,
subscription-plan confirmation, two authentic AI interaction screenshots and the
personally narrated video remain required unless completeness.json says present.
No video or AI conversation screenshot has been fabricated. Read REVIEW_CHECKLIST.md.
PERSONAL in the ZIP name is a personal-project identifier, not a student number.
For a real course submission replace it with the actual required identity and
follow that course's submission rules. No email is sent by these scripts.
"""


def main():
    stage = ROOT / "submission"
    stage.mkdir(exist_ok=True)
    files = set()

    def copy(source, relative):
        destination = stage / relative
        assert destination.resolve().is_relative_to(stage.resolve())
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        files.add(destination)

    def write(relative, text):
        destination = stage / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        files.add(destination)

    def tree(source, relative):
        for path in sorted(source.rglob("*")):
            if path.is_file() and not any(
                p in ("__pycache__", ".pytest_cache", ".venv", "tmp")
                for p in path.parts
            ):
                copy(path, Path(relative) / path.relative_to(source))

    for directory in (
        "src",
        "tests",
        "tools",
        "docs",
        "report",
        "figures",
        "results",
        "evidence",
        "examples",
        "demo",
        ".github",
    ):
        tree(ROOT / directory, Path("02_SourceCode") / directory)
    for name in (
        "README.md",
        "REVIEW_CHECKLIST.md",
        "devlog.md",
        "owner-metadata.json",
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        "install.bat",
        "run.bat",
        "test.bat",
        "run.sh",
        ".gitignore",
        ".gitattributes",
    ):
        copy(ROOT / name, Path("02_SourceCode") / name)
    for name in ("report.pdf", "report.md", "source_listing.txt", "requirements.txt"):
        copy(ROOT / "report" / name, Path("01_Report") / name)
    tree(ROOT / "tests", "tests")
    tree(ROOT / "examples", "04_Demo/examples")
    tree(ROOT / "demo", "04_Demo")
    copy(ROOT / "devlog.md", "devlog.md")
    copy(ROOT / "REVIEW_CHECKLIST.md", "REVIEW_CHECKLIST.md")
    copy(ROOT / "requirements.txt", "03_Executable/requirements.txt")
    write("README.txt", ROOT_README)
    write(
        "03_Executable/run.bat",
        '@echo off\nsetlocal\npushd "%~dp0..\\02_SourceCode"\ncall run.bat %*\nset "task_exit=%errorlevel%"\npopd\nexit /b %task_exit%\n',
    )
    write(
        "03_Executable/README.txt",
        "Windows entry point: run.bat --interactive or run.bat --input examples\\sites.txt --output output\\demo.png --csv output\\cells.csv. Dependencies install into 02_SourceCode/.venv on first use. Read the root README.txt.\n",
    )
    try:
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        gitlog = subprocess.check_output(
            ["git", "log", "--date=iso-strict", "--pretty=fuller", "--stat"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError):
        revision = "unavailable"
        gitlog = "Git unavailable; see included development log.\n"
    write("02_SourceCode/git_log.txt", gitlog)
    write(
        "02_SourceCode/SOURCE_REVISION.json",
        json.dumps({"git_commit": revision}, indent=2),
    )
    metadata = json.loads((ROOT / "owner-metadata.json").read_text(encoding="utf-8"))
    required = [
        "01_Report/report.pdf",
        "01_Report/report.md",
        "02_SourceCode/src/fortune/sweep.py",
        "03_Executable/run.bat",
        "04_Demo/script.md",
        "tests/test_diagram.py",
        "README.txt",
        "devlog.md",
    ]
    missing = [p for p in required if not (stage / p).is_file()]
    owner = dict(
        subscription_plan=bool(metadata.get("subscription_plan")),
        ai_screenshot_1=(ROOT / "evidence" / "ai-interaction-1.png").is_file(),
        ai_screenshot_2=(ROOT / "evidence" / "ai-interaction-2.png").is_file(),
        narrated_recording=(ROOT / "demo" / "walkthrough.mp4").is_file(),
    )
    manifest = dict(
        generated_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        source_revision=revision,
        missing_required_files=missing,
        ai_artifacts_present=not missing,
        owner_evidence_present=owner,
        owner_review_required=not metadata.get("owner_review_complete", False),
        complete_against_reference=not missing
        and all(owner.values())
        and metadata.get("owner_review_complete", False),
        note="Review copy; file presence alone does not verify video duration, narration or screenshot authenticity.",
    )
    write("completeness.json", json.dumps(manifest, indent=2) + "\n")
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    archive = dist / "CG_Assignment_PERSONAL_broccolize.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as out:
        for path in sorted(files):
            out.write(path, path.relative_to(stage).as_posix())
    with ZipFile(archive) as check:
        assert check.testzip() is None
        assert all(
            not p.startswith("/") and ".." not in Path(p).parts
            for p in check.namelist()
        )
    audit = dict(
        archive=archive.name,
        bytes=archive.stat().st_size,
        files=len(files),
        sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        source_revision=revision,
        required_files_present=not missing,
        zip_crc_check="passed",
        owner_evidence_present=owner,
    )
    (ROOT / "evidence" / "package-audit.json").write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
