"""Compile editable LaTeX with native TeX or an existing WSL installation.

LaTeX section files are authoritative; Markdown is never regenerated or read.
Shell escape is disabled and actual compiler logs are retained.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
BUILD = ROOT / "tmp" / "latex-build"


def checked(command, *, cwd=None, timeout=300):
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def select_engine(requested, distro):
    names = [requested] if requested != "auto" else ["lualatex", "xelatex"]
    if distro is None:
        for name in names:
            executable = shutil.which(name)
            if (
                executable
                and checked([executable, "--version"], timeout=20).returncode == 0
            ):
                return executable, None
        if os.name != "nt":
            raise RuntimeError("Install LuaLaTeX or XeLaTeX, or specify --engine.")
        distro = "Debian"
    for name in names:
        probe = checked(["wsl.exe", "-d", distro, "--", "which", name], timeout=30)
        if probe.returncode == 0:
            return name, distro
    raise RuntimeError(f"No working LuaLaTeX/XeLaTeX found in WSL {distro}.")


def wsl_path(path, distro):
    result = checked(
        ["wsl.exe", "-d", distro, "--", "wslpath", "-u", str(path)], timeout=30
    )
    if result.returncode:
        raise RuntimeError(result.stdout)
    return result.stdout.strip()


def source_listing():
    paths = []
    for directory in ("src", "tests", "tools"):
        paths.extend((ROOT / directory).rglob("*.py"))
    # The browser renderer is part of the editable implementation, too.
    paths.extend((ROOT / "src/fortune").glob("*.html"))
    paths.extend((ROOT / "src/fortune").glob("*.js"))
    paths.extend((ROOT / "tests").glob("*.js"))
    paths.extend(ROOT.glob("*.bat"))
    paths.extend(ROOT.glob("*.sh"))
    paths.extend((ROOT / "tools").rglob("*.sh"))
    paths.extend(REPORT.glob("*.bat"))
    paths.extend(
        [
            ROOT / "pyproject.toml",
            ROOT / "requirements.txt",
            ROOT / ".github/workflows/tests.yml",
        ]
    )
    listing = []
    for path in sorted(paths):
        listing.extend(
            [
                "=" * 78,
                str(path.relative_to(ROOT)),
                "=" * 78,
                path.read_text(encoding="utf-8"),
                "",
            ]
        )
    (REPORT / "source_listing.txt").write_text("\n".join(listing), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--engine", choices=["auto", "lualatex", "xelatex"], default="auto"
    )
    parser.add_argument(
        "--wsl", metavar="DISTRO", help="Compile in this WSL distribution"
    )
    args = parser.parse_args(argv)
    BUILD.mkdir(parents=True, exist_ok=True)
    engine, distro = select_engine(args.engine, args.wsl)
    if distro:
        report_path, build_path = wsl_path(REPORT, distro), wsl_path(BUILD, distro)
        command = ["wsl.exe", "-d", distro, "--cd", report_path, "--"]
        local_tex = ROOT / "tmp/tex-deps/tree/usr/share/texlive/texmf-dist"
        cached_paths = ROOT / "tmp/tex-deps/wsl-paths.json"
        if cached_paths.is_file():
            local_paths = json.loads(cached_paths.read_text(encoding="utf-8"))
            command.extend(
                [
                    "env",
                    f"TEXMFHOME={local_paths['texmf_home']}",
                    f"TEXMFVAR={local_paths['font_cache']}",
                    f"TEXMFCACHE={local_paths['font_cache']}",
                ]
            )
        elif local_tex.is_dir():
            font_cache = ROOT / "tmp/latex-font-cache"
            font_cache.mkdir(exist_ok=True)
            local_path = wsl_path(local_tex, distro)
            cache_path = wsl_path(font_cache, distro)
            command.extend(
                [
                    "env",
                    f"TEXMFHOME={local_path}",
                    f"TEXMFVAR={cache_path}",
                    f"TEXMFCACHE={cache_path}",
                ]
            )
        command.append(engine)
        bib_command = [
            "wsl.exe",
            "-d",
            distro,
            "--cd",
            build_path,
            "--",
            "bibtex",
            "report",
        ]
        build_option = build_path
    else:
        command = [engine]
        bibtex = shutil.which("bibtex")
        if not bibtex:
            raise RuntimeError("BibTeX is required for the numbered references.")
        bib_command = [bibtex, "report"]
        build_option = str(BUILD)
    command.extend(
        [
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            "-no-shell-escape",
            "-synctex=1",
            f"-output-directory={build_option}",
            "report.tex",
        ]
    )
    shutil.copy2(REPORT / "references.bib", BUILD / "references.bib")
    logs = []

    def run_stage(name, stage_command, cwd):
        result = checked(stage_command, cwd=cwd)
        (BUILD / f"{name}.log").write_text(result.stdout, encoding="utf-8")
        logs.append(f"=== {name} ===\n{result.stdout}")
        (ROOT / "evidence/report-build.log").write_text(
            "\n".join(logs), encoding="utf-8"
        )
        if result.returncode:
            raise RuntimeError(
                f"{name} failed:\n" + "\n".join(result.stdout.splitlines()[-45:])
            )
        return result.stdout

    run_stage("latex-pass-1", command, REPORT)
    run_stage("bibtex", bib_command, BUILD)
    run_stage("latex-pass-2", command, REPORT)
    final_output = run_stage("latex-pass-3", command, REPORT)
    if re.search(
        r"(?:Citation .* undefined|There were undefined references)", final_output
    ):
        raise RuntimeError(
            "Unresolved citations or references; see evidence/report-build.log"
        )
    pdf = BUILD / "report.pdf"
    if not pdf.is_file():
        raise RuntimeError("LaTeX did not produce report.pdf")
    shutil.copy2(pdf, REPORT / "report.pdf")
    source_listing()
    summary = {
        "source": "report/report.tex",
        "editable_sections": "report/sections/",
        "engine": Path(engine).name,
        "wsl_distribution": distro,
        "bibliography_style": "ieeetr",
        "latex_passes": 3,
        "shell_escape": False,
        "overfull_box_warnings": len(re.findall(r"Overfull \\[hv]box", final_output)),
        "pdf_bytes": pdf.stat().st_size,
        "output": "report/report.pdf",
    }
    (ROOT / "evidence/report-build.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error
