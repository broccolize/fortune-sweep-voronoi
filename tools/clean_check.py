"""Install and verify a clean Windows source copy without sharing its environment."""

from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]


def main():
    target = (ROOT / "tmp" / "clean-check-final").resolve()
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
    run(str(python), "-m", "pip", "install", "-r", "requirements.txt")
    run(str(python), "-m", "pip", "install", "--no-deps", "--force-reinstall", ".")
    run(
        str(python),
        "-I",
        "-c",
        'import fortune;print("Installed package:",fortune.__file__)',
    )
    run(
        str(python),
        "-m",
        "pytest",
        "-q",
        "--basetemp",
        "pytest-temp",
        "--junitxml",
        str(ROOT / "evidence" / "clean-install-tests.xml"),
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
    )
    for name in ("clean.png", "clean.csv", "clean.json"):
        assert (target / name).stat().st_size > 0
    result = dict(
        status="passed",
        actual_timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        separate_environment=True,
        wheel_install=True,
        installed_import_isolated=True,
        batch_outputs=["clean.png", "clean.csv", "clean.json"],
    )
    (ROOT / "evidence" / "clean-install-summary.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
