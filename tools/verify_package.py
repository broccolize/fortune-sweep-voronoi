"""Verify a delivered ZIP in a fresh Windows environment, retaining real logs."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]

# Load Fortune before pytest and verify every loaded submodule's actual location.
INSTALLED_TEST_RUNNER = """
from pathlib import Path
import sys
import fortune
import pytest
folder = Path(fortune.__file__).resolve().parent
assert "site-packages" in str(folder), folder
print("Tested installed package:", folder)
result = pytest.main(sys.argv[1:])
modules = {name: Path(module.__file__).resolve()
           for name, module in sys.modules.items()
           if name == "fortune" or name.startswith("fortune.")}
assert modules and all(path.is_relative_to(folder) for path in modules.values()), modules
print("All loaded Fortune modules came from the installed package:", len(modules))
raise SystemExit(result)
"""


def installed_test_command(python, junit):
    return [
        str(python),
        "-I",
        "-c",
        INSTALLED_TEST_RUNNER,
        "-c",
        "pytest-package.ini",
        "tests",
        "-q",
        "--basetemp",
        "pytest-temp",
        "--junitxml",
        str(junit),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    archive = args.archive.resolve()
    if os.name != "nt":
        parser.error("This check exercises the delivered Windows launcher.")
    if not shutil.which("node"):
        parser.error("Install Node.js 24.22.1 to run the complete JavaScript checks")
    stamp = datetime.now(timezone(timedelta(hours=8)))
    target = (ROOT / "tmp" / stamp.strftime("package-check-%Y%m%d-%H%M%S")).resolve()
    assert target.is_relative_to((ROOT / "tmp").resolve())
    target.mkdir(parents=True, exist_ok=False)
    log = ROOT / "evidence/final-package-verification.log"
    log.write_text("", encoding="utf-8")
    with ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise RuntimeError("Archive CRC verification failed")
        for name in bundle.namelist():
            if not (target / name).resolve().is_relative_to(target):
                raise RuntimeError(f"Unsafe archive member: {name}")
        bundle.extractall(target)
    source = target / "02_SourceCode"
    temporary = target / "temporary"
    temporary.mkdir()
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["TEMP"] = env["TMP"] = str(temporary)
    env["MPLBACKEND"] = "Agg"
    env["MPLCONFIGDIR"] = str(target / "mplconfig")
    env["PYTHONIOENCODING"] = "utf-8"

    def run(name, command, *, cwd=source):
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=600,
            check=False,
        )
        with log.open("a", encoding="utf-8") as stream:
            stream.write(f"=== {name} ===\n{result.stdout}\n")
        print(f"{name}: exit {result.returncode}", flush=True)
        if result.returncode:
            raise RuntimeError(f"{name} failed; inspect {log}")
        return result.stdout

    python = source / ".venv/Scripts/python.exe"
    run(
        "new isolated environment",
        [sys.executable, "-m", "venv", str(source / ".venv")],
    )
    run(
        "pinned dependencies",
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-q",
            "-r",
            "requirements-reference.txt",
        ],
    )
    run(
        "install delivered package",
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-q",
            "--no-deps",
            ".",
        ],
    )
    installed = run(
        "isolated import and Canvas assets",
        [
            str(python),
            "-I",
            "-c",
            (
                "from pathlib import Path; import fortune; "
                "from fortune.replay_canvas import write_replay; "
                "folder=Path(fortune.__file__).parent; "
                "assert 'site-packages' in str(folder); "
                "assert (folder/'replay_canvas.html').is_file(); "
                "assert (folder/'replay_canvas.js').is_file(); "
                "r=write_replay([(0,0),(1,0),(0.5,1)], output='clean-replay.html'); "
                "text=r.path.read_text(encoding='utf-8'); "
                "assert '<canvas' in text and '__FORTUNE_DATA__' not in text; "
                "print(fortune.__file__)"
            ),
        ],
    ).strip()
    # Block ancestor configuration discovery, including the primary checkout's
    # pythonpath option when an archive is extracted beneath that checkout.
    (target / "pytest-package.ini").write_text(
        "[pytest]\naddopts = -ra\n", encoding="utf-8"
    )
    run(
        "delivered independent test suite",
        installed_test_command(python, ROOT / "evidence/final-package-tests.xml"),
        cwd=target,
    )
    run(
        "03_Executable batch launcher",
        [
            "cmd.exe",
            "/d",
            "/c",
            "03_Executable\\run.bat",
            "--input",
            "examples\\sites.txt",
            "--bbox",
            "0",
            "0",
            "1",
            "1",
            "--output",
            "output\\package.png",
            "--csv",
            "output\\package.csv",
            "--json",
            "output\\package.json",
            "--delaunay",
        ],
        cwd=target,
    )
    for name in ("package.png", "package.csv", "package.json"):
        if (source / "output" / name).stat().st_size <= 0:
            raise RuntimeError(f"Empty batch output: {name}")
    tree = ET.parse(ROOT / "evidence/final-package-tests.xml")
    cases = list(tree.iter("testcase"))
    failures = sum(len(list(tree.iter(tag))) for tag in ("failure", "error"))
    skipped = len(list(tree.iter("skipped")))
    if failures or skipped:
        raise RuntimeError("Delivered tests must pass without failures or skips")
    hashes = {
        str(p.relative_to(source)).replace("\\", "/"): hashlib.sha256(
            p.read_bytes()
        ).hexdigest()
        for folder in ("src/fortune", "tests")
        for p in sorted((source / folder).rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
    }
    for name in (
        "pyproject.toml",
        "requirements.txt",
        "requirements-reference.txt",
        "run.bat",
        "test.bat",
        "install.bat",
        "run.sh",
    ):
        hashes[name] = hashlib.sha256((source / name).read_bytes()).hexdigest()
    summary = dict(
        status="passed",
        actual_timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        archive=archive.name,
        archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        extracted_to=str(target),
        separate_environment=True,
        installed_import=installed,
        installed_import_isolated=True,
        pytest_configuration_isolated=True,
        all_tested_fortune_modules_installed=True,
        canvas_assets_and_offline_export="passed",
        delivered_windows_launcher="passed",
        tests_passed=len(cases) - skipped,
        tests_skipped=skipped,
        test_failures=failures,
        source_and_test_sha256=hashes,
        source_hash_scope="Delivered src/fortune, tests, package configuration and launchers; excludes generated egg-info and caches",
        node=subprocess.check_output(["node", "--version"], text=True).strip(),
        log="evidence/final-package-verification.log",
        junit="evidence/final-package-tests.xml",
    )
    (ROOT / "evidence/final-package-verification.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {k: v for k, v in summary.items() if k != "source_and_test_sha256"},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
