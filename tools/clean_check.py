"""Install and verify a clean Windows source copy without sharing its environment."""

import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from verify_package import installed_test_command  # noqa: E402


def main():
    if not shutil.which("node"):
        raise RuntimeError("Install Node.js 24.22.1 for the complete JavaScript checks")
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")
    target = (ROOT / "tmp" / f"clean-check-{stamp}").resolve()
    assert target.is_relative_to(ROOT / "tmp")
    target.mkdir(parents=True, exist_ok=True)
    for name in ("src", "tests", "examples"):
        shutil.copytree(
            ROOT / name,
            target / name,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    for name in (
        "pyproject.toml",
        "requirements.txt",
        "requirements-reference.txt",
        "install.bat",
        "run.bat",
        "test.bat",
    ):
        shutil.copy2(ROOT / name, target / name)
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    temporary = target / "temporary"
    temporary.mkdir(exist_ok=True)
    env["TEMP"] = env["TMP"] = str(temporary)
    env["MPLBACKEND"] = "Agg"
    env["MPLCONFIGDIR"] = str(target / "mplconfig")
    python = target / ".venv" / "Scripts" / "python.exe"

    def run(*args):
        subprocess.run(args, cwd=target, env=env, check=True)

    if not python.exists():
        run(sys.executable, "-m", "venv", str(target / ".venv"))
    run(str(python), "-m", "pip", "install", "-r", "requirements-reference.txt")
    run(str(python), "-m", "pip", "install", "--no-deps", "--force-reinstall", ".")
    run(
        str(python),
        "-I",
        "-c",
        'import fortune;print("Installed package:",fortune.__file__)',
    )
    (target / "pytest-package.ini").write_text(
        "[pytest]\naddopts = -ra\n", encoding="utf-8"
    )
    junit = ROOT / "evidence/final-clean-install-tests.xml"
    run(*installed_test_command(python, junit))
    tree = ET.parse(junit)
    if any(list(tree.iter(tag)) for tag in ("failure", "error", "skipped")):
        raise RuntimeError(
            "The complete clean-install suite must have no failures or skips"
        )
    run(
        str(python),
        "-I",
        "-m",
        "fortune",
        "--input",
        "examples/sites.txt",
        "--bbox",
        "0",
        "0",
        "1",
        "1",
        "--output",
        "clean.png",
        "--csv",
        "clean.csv",
        "--json",
        "clean.json",
        "--delaunay",
    )
    for name in ("clean.png", "clean.csv", "clean.json"):
        assert (target / name).stat().st_size > 0
    result = dict(
        status="passed",
        actual_timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        separate_environment=True,
        wheel_install=True,
        installed_import_isolated=True,
        all_tested_fortune_modules_installed=True,
        tests_passed=len(list(tree.iter("testcase"))),
        tests_skipped=0,
        node=subprocess.check_output(["node", "--version"], text=True).strip(),
        batch_outputs=["clean.png", "clean.csv", "clean.json"],
    )
    (ROOT / "evidence" / "final-clean-install-summary.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
