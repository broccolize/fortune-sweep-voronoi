"""Assemble the assignment ZIP without environments, editing files or credentials."""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--exclude-recording",
        action="store_true",
        help="Build source/report materials without reading recording or editing files",
    )
    args = parser.parse_args()
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
            if (
                source == ROOT / "demo"
                and str(relative).replace("\\", "/") == "02_SourceCode/demo"
                and path.suffix.lower() in {".mp4", ".mov", ".mkv", ".avi", ".webm"}
            ):
                continue  # The single delivered video belongs in 04_Demo.
            if args.exclude_recording and path.suffix.lower() in {
                ".mp4",
                ".gif",
                ".mov",
                ".mkv",
                ".avi",
                ".webm",
            }:
                continue
            if source == ROOT / "demo" and (
                path.relative_to(source).parts[0] == "recording"
                or path.name == "command.txt"
            ):
                continue
            # A ZIP cannot contain its own final hash; final audits stay beside it.
            if path in {
                ROOT / "evidence/package-audit.json",
                ROOT / "evidence/package-final-content.json",
            }:
                continue
            if source == ROOT / "report" and (
                path.suffix
                in {
                    ".aux",
                    ".bbl",
                    ".blg",
                    ".log",
                    ".toc",
                    ".lof",
                    ".lot",
                    ".out",
                    ".fls",
                }
                or path.name.endswith((".synctex.gz", ".fdb_latexmk"))
            ):
                continue
            if path.is_file() and not any(
                p in ("__pycache__", ".pytest_cache", ".venv", "tmp")
                or p.endswith(".egg-info")
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
        if directory == "demo" and args.exclude_recording:
            checklist = ROOT / "demo/recording-checklist.md"
            if checklist.is_file():
                copy(checklist, "02_SourceCode/demo/recording-checklist.md")
            continue
        tree(ROOT / directory, Path("02_SourceCode") / directory)
    for name in (
        "owner-metadata.json",
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-reference.txt",
        "install.bat",
        "run.bat",
        "test.bat",
        "run.sh",
        ".gitignore",
        ".gitattributes",
    ):
        copy(ROOT / name, Path("02_SourceCode") / name)
    # Documentation is supplied manually. Include existing README files without
    # recreating deleted versions or synthesizing replacement instructions.
    for path in sorted(ROOT.iterdir()):
        if path.is_file() and path.stem.lower() == "readme":
            copy(path, Path("02_SourceCode") / path.name)
    for name in ("README.txt", "README.md"):
        path = ROOT / name
        if path.is_file():
            copy(path, "README.txt")
            break
    tree(ROOT / "report", "01_Report")
    tree(ROOT / "figures", "01_Report/figures")
    copy(ROOT / "evidence/gui-native.png", "01_Report/figures/gui-native.png")
    for name in (
        "ai-interaction-1.png",
        "pi-environment.png",
        "pi-interaction-invariants.png",
        "ai-interaction-2.png",
        "pi-tiny-cell-code-continuation.png",
        "pi-interaction-tests.png",
        "pi-tests-summary.png",
        "canvas-preview.jpg",
        "canvas-export.png",
    ):
        copy(ROOT / "evidence" / name, Path("01_Report/figures") / name)
    tree(ROOT / "tests", "tests")
    tree(ROOT / "examples", "04_Demo/examples")
    if args.exclude_recording:
        checklist = ROOT / "demo/recording-checklist.md"
        if checklist.is_file():
            copy(checklist, "04_Demo/recording-checklist.md")
    else:
        tree(ROOT / "demo", "04_Demo")
    copy(ROOT / "requirements.txt", "03_Executable/requirements.txt")
    write(
        "03_Executable/run.bat",
        '@echo off\nsetlocal\npushd "%~dp0..\\02_SourceCode"\ncall run.bat %*\nset "task_exit=%errorlevel%"\npopd\nexit /b %task_exit%\n',
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
        source_worktree_dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=ROOT, text=True, encoding="utf-8"
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        revision = "unavailable"
        source_worktree_dirty = None
        gitlog = "Git history unavailable in this source folder.\n"
    write("02_SourceCode/git_log.txt", gitlog)
    write(
        "02_SourceCode/SOURCE_REVISION.json",
        json.dumps(
            {
                "base_git_commit": revision,
                "source_worktree_dirty": source_worktree_dirty,
                "note": "The archive includes the current working files; the base commit alone does not identify uncommitted changes.",
            },
            indent=2,
        ),
    )
    metadata = json.loads((ROOT / "owner-metadata.json").read_text(encoding="utf-8"))
    required = [
        "01_Report/report.pdf",
        "01_Report/source_appendix.pdf",
        "01_Report/source_appendix.tex",
        "01_Report/report.tex",
        "01_Report/preamble.tex",
        "01_Report/references.bib",
        "01_Report/sections/01-introduction.tex",
        "01_Report/sections/appendix-c.tex",
        "01_Report/figures/canvas-preview.jpg",
        "02_SourceCode/src/fortune/sweep.py",
        "02_SourceCode/src/fortune/replay_canvas.py",
        "02_SourceCode/src/fortune/replay_canvas.html",
        "02_SourceCode/src/fortune/replay_canvas.js",
        "02_SourceCode/tools/verify_package.py",
        "03_Executable/run.bat",
        "04_Demo/examples/sweep-pointer-replay.html",
        "tests/test_diagram.py",
        "README.txt",
    ]
    if not args.exclude_recording:
        required.append("04_Demo/walkthrough.mp4")
    staged_names = {p.relative_to(stage).as_posix() for p in files}
    missing = [p for p in required if p not in staged_names]
    owner = dict(
        subscription_plan=bool(metadata.get("subscription_plan")),
        ai_screenshot_1=(ROOT / "evidence" / "ai-interaction-1.png").is_file(),
        ai_screenshot_2=(ROOT / "evidence" / "ai-interaction-2.png").is_file(),
        narrated_recording=False
        if args.exclude_recording
        else (ROOT / "demo" / "walkthrough.mp4").is_file(),
    )
    verified = ROOT / "evidence/final-package-verification.json"
    if not verified.is_file():
        verified = ROOT / "evidence/final-clean-install-summary.json"
    if not verified.is_file():
        verified = ROOT / "evidence/package-verification.json"
    runtime_check = dict(matches_tested_payload=False, compared_files=0)
    if verified.is_file():
        record = json.loads(verified.read_text(encoding="utf-8"))
        expected = record.get("source_and_test_sha256", {})
        changed = [
            name
            for name, expected_hash in expected.items()
            if not (stage / "02_SourceCode" / name).is_file()
            or hashlib.sha256((stage / "02_SourceCode" / name).read_bytes()).hexdigest()
            != expected_hash
        ]
        runtime_check = dict(
            matches_tested_payload=bool(expected) and not changed,
            compared_files=len(expected),
            changed_files=changed,
            installed_tests_passed=record.get("tests_passed"),
            installed_module_assertions=record.get(
                "all_tested_fortune_modules_installed", False
            ),
            verification_record="02_SourceCode/"
            + verified.relative_to(ROOT).as_posix(),
        )
    audit_path = ROOT / "evidence/report-revision-audit.json"
    if not audit_path.is_file():
        audit_path = ROOT / "evidence/report-audit.json"
    report_audit = json.loads(audit_path.read_text(encoding="utf-8"))
    report_hash = hashlib.sha256(
        (stage / "01_Report/report.pdf").read_bytes()
    ).hexdigest()
    report_check = dict(
        matches_audited_pdf=report_hash == report_audit.get("pdf_sha256"),
        sha256=report_hash,
        pages=report_audit.get("pages"),
        body_pages=report_audit.get("main_body_pages"),
        verification_record="02_SourceCode/" + audit_path.relative_to(ROOT).as_posix(),
    )
    supplement_hash = hashlib.sha256(
        (stage / "01_Report/source_appendix.pdf").read_bytes()
    ).hexdigest()
    report_check.update(
        source_supplement_sha256=supplement_hash,
        source_supplement_pages=report_audit.get("source_supplement_pages"),
        matches_audited_source_supplement=supplement_hash
        == report_audit.get("source_supplement_sha256"),
    )
    snapshot = stage / "01_Report/implementation-snapshot.zip"
    if snapshot.is_file():
        with ZipFile(snapshot) as source_snapshot:
            expected_sources = {
                name: source_snapshot.read(name).replace(b"\r\n", b"\n")
                for name in source_snapshot.namelist()
                if name.startswith("src/") and not name.endswith("/")
            }
        delivered_source = stage / "02_SourceCode"
        current_sources = {
            path.relative_to(delivered_source).as_posix(): path.read_bytes().replace(
                b"\r\n", b"\n"
            )
            for path in (delivered_source / "src").rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and not any(part.endswith(".egg-info") for part in path.parts)
        }
        differing_sources = sorted(
            name
            for name in expected_sources.keys() | current_sources.keys()
            if expected_sources.get(name) != current_sources.get(name)
        )
        report_check.update(
            report_scope_end=report_audit.get("report_scope_end"),
            matches_packaged_implementation=not differing_sources,
            differing_application_files=differing_sources,
        )
    manifest = dict(
        generated_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        source_revision=revision,
        source_worktree_dirty=source_worktree_dirty,
        recording_status="excluded_at_user_request"
        if args.exclude_recording
        else "included_if_available",
        missing_required_files=missing,
        ai_artifacts_present=owner["ai_screenshot_1"] and owner["ai_screenshot_2"],
        owner_evidence_present=owner,
        owner_review_required=not metadata.get("owner_review_complete", False),
        runtime_verification=runtime_check,
        report_verification=report_check,
        video_verification=json.loads(
            (ROOT / "evidence/final-video-validation.json").read_text(encoding="utf-8")
        ) if (ROOT / "evidence/final-video-validation.json").is_file() else None,
        complete_against_reference=not missing
        and all(owner.values())
        and runtime_check["matches_tested_payload"]
        and runtime_check.get("installed_module_assertions", False)
        and report_check["matches_audited_pdf"]
        and report_check["matches_audited_source_supplement"]
        and report_check.get("matches_packaged_implementation", True)
        and metadata.get("owner_review_complete", False),
        note="File presence and automated checks are distinct from the author's final review.",
    )
    if manifest["video_verification"] and not manifest["video_verification"].get(
        "meets_duration_limit", False
    ):
        manifest["complete_against_reference"] = False
    write("completeness.json", json.dumps(manifest, indent=2) + "\n")
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    identifier = re.sub(
        r"[^A-Za-z0-9_-]+", "_", str(metadata.get("student_id") or "PERSONAL")
    )
    author = re.sub(
        r"[^A-Za-z0-9_-]+", "_", metadata.get("author", "broccolize")
    ).strip("_")
    archive = dist / f"CG_Assignment_{identifier}_{author}.zip"
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
        source_worktree_dirty=source_worktree_dirty,
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
