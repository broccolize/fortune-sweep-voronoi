"""Reproduce the report scaling figure from its retained benchmark dataset."""
# ruff: noqa: E402
# Set the noninteractive backend before importing pyplot.

import argparse
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "tmp" / "matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "report/data/construction-benchmark-current.json",
    )
    parser.add_argument("--stem", default="scaling-current")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))["results"]
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman"],
            "mathtext.fontset": "stix",
            "font.size": 11,
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 8,
        }
    )
    ns = [row["n"] for row in data]
    ts = [row["median_seconds"] for row in data]
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 3.1))
    axes[0].loglog(ns, ts, "o-", label="Measured median, 3 runs")
    axes[0].loglog(
        ns,
        [ts[0] * n * math.log2(n) / (ns[0] * math.log2(ns[0])) for n in ns],
        "--",
        label=r"$n\log_2 n$, scaled at $n=100$",
    )
    axes[0].set(
        xlabel=r"Sites $n$", ylabel="Construction time (seconds)", title="Time scaling"
    )
    axes[0].legend()
    axes[1].loglog(
        ns,
        [r["python_peak_bytes"] / 2**20 for r in data],
        "o-",
        label="Traced Python peak",
    )
    axes[1].loglog(
        ns,
        [r["process_peak_rss_bytes"] / 2**20 for r in data],
        "s-",
        label="Process peak with tracer",
    )
    axes[1].set(
        xlabel=r"Sites $n$",
        ylabel="Peak memory (MiB)",
        title="Memory in isolated processes",
    )
    axes[1].legend()
    for axis in axes:
        axis.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    target = ROOT / "report/figures"
    target.mkdir(parents=True, exist_ok=True)
    fig.savefig(target / f"{args.stem}.png", dpi=220, bbox_inches="tight")
    fig.savefig(target / f"{args.stem}.svg", bbox_inches="tight")
    plt.close(fig)
    print("Wrote report scaling figure from the retained core benchmark dataset")


if __name__ == "__main__":
    main()
