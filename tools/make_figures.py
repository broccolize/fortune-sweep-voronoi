"""Reproduce all original program and explanatory figures from recorded data."""
# ruff: noqa: E402
# Standalone execution needs the source path and Agg backend before local imports.

import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "tmp" / "matplotlib"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from fortune import Box, construct
from fortune.geometry import Point, parabola_y
from fortune.io import random_sites, read_sites, write_csv, write_json
from fortune.visualize import draw, render

OUT = ROOT / "figures"


def report_diagram(diagram, path, *, labels=True):
    """Render at the report's physical width so embedded labels stay legible."""
    fig, ax = plt.subplots(figsize=(6.3, 5.8))
    draw(diagram, ax, labels=labels)
    for text in ax.texts:
        text.set_fontsize(10)
    if not labels:
        ax.collections[-1].set_sizes([5])
    ax.set_title(ax.get_title(), fontsize=11)
    fig.tight_layout(pad=0.7)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--benchmark", type=Path, default=ROOT / "results/benchmark.json"
    )
    args = parser.parse_args()
    plt.rcParams.update(
        {
            "font.family": "serif",
            "mathtext.fontset": "stix",
            "font.serif": ["Times New Roman"],
            "font.size": 11,
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
        }
    )
    OUT.mkdir(exist_ok=True)
    d = construct(read_sites(ROOT / "examples" / "sites.txt"), Box(0, 0, 1, 1))
    report_diagram(d, OUT / "general.png")
    render(d, ROOT / "examples" / "general.svg")
    write_csv(d, ROOT / "examples" / "cells.csv")
    write_json(d, ROOT / "examples" / "diagram.json")
    large = construct(random_sites(1000, 2026), Box(0, 0, 1, 1))
    report_diagram(large, OUT / "large.png", labels=False)
    cases = [
        ("Horizontal collinear", [(i, 0) for i in range(5)]),
        ("Vertical collinear", [(0, i) for i in range(5)]),
        ("Slanted collinear", [(i, 2 * i) for i in range(5)]),
        ("Cocircular square", [(0, 0), (1, 0), (1, 1), (0, 1)]),
        ("Duplicate index groups", [(0, 0), (1, 0), (0, 1), (0, 0)]),
        (
            r"Near sites $10^{-11}$ apart",
            [(0, 0), (1e-11, 1e-11), (1, 0), (0.3, 0.7), (0, 1)],
        ),
        ("Single site", [(0, 0)]),
        ("Two sites", [(0, 0), (1, 1)]),
    ]
    for half in range(2):
        fig, axes = plt.subplots(2, 2, figsize=(6.3, 5.9))
        for ax, (title, points) in zip(axes.flat, cases[half * 4 : half * 4 + 4]):
            draw(construct(points), ax)
            ax.set_title(title, fontsize=10)
            for text in ax.texts:
                text.set_fontsize(9)
            ax.xaxis.set_major_locator(MaxNLocator(3))
            ax.yaxis.set_major_locator(MaxNLocator(3))
            width = ax.get_xlim()[1] - ax.get_xlim()[0]
            height = ax.get_ylim()[1] - ax.get_ylim()[0]
            if width / height < 0.3:
                ax.set_xticks([points[0][0]])
            if height / width < 0.3:
                ax.set_yticks([points[0][1]])
        fig.tight_layout()
        fig.savefig(OUT / f"degenerate-{half + 1}.png", dpi=220, bbox_inches="tight")
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.3, 3.7))
    boxes = [
        (0.02, 0.72, "Input validation\nExact duplicate groups"),
        (0.56, 0.72, "Fortune sweep\nAVL arcs + event heap"),
        (0.56, 0.40, "Voronoi topology\nAdjacency + vertices"),
        (0.02, 0.40, "Clipped cell assembly\nOrdered half-plane intersection"),
        (0.02, 0.08, "CLI, GUI and exports\nPNG / SVG / CSV / JSON"),
        (0.56, 0.08, "Independent tests\nOwnership / empty circles"),
    ]
    for x, y, label in boxes:
        ax.add_patch(
            plt.Rectangle(
                (x, y),
                0.42,
                0.22,
                facecolor="#f3f5f7",
                edgecolor="#687481",
                linewidth=0.8,
            )
        )
        ax.text(x + 0.21, y + 0.11, label, ha="center", va="center", fontsize=10.5)
    for start, end in [
        ((0.44, 0.83), (0.56, 0.83)),
        ((0.77, 0.72), (0.77, 0.62)),
        ((0.56, 0.51), (0.44, 0.51)),
        ((0.23, 0.40), (0.23, 0.30)),
        ((0.44, 0.19), (0.56, 0.19)),
    ]:
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops=dict(arrowstyle="->", lw=1.0, color="#485563"),
        )
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "architecture.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "architecture.svg", bbox_inches="tight")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.3, 3.4))
    points = [Point(-0.6, 0.8), Point(0.2, 0.6), Point(0.75, 1.0)]
    ly = -0.2
    xs = [-1.2 + i * 2.4 / 700 for i in range(701)]
    curves = [[parabola_y(p, x, ly) for x in xs] for p in points]
    for i, (p, ys) in enumerate(zip(points, curves)):
        ax.plot(xs, ys, alpha=0.4)
        ax.scatter(p.x, p.y, c="black")
        ax.annotate(f"p{i}", (p.x, p.y), xytext=(5, 5), textcoords="offset points")
    ax.plot(
        xs,
        [min(values) for values in zip(*curves)],
        lw=2.5,
        c="#1f4e79",
        label="Beach line lower envelope",
    )
    ax.axhline(ly, c="#b42318", ls="--", label="Sweep directrix")
    ax.set(xlim=(-1.2, 1.2), ylim=(-0.4, 1.5), xlabel="x", ylabel="y")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "beachline.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    data = json.loads(args.benchmark.read_text(encoding="utf-8"))["results"]
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
    axes[0].legend(fontsize=8)
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
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "scaling.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "scaling.svg", bbox_inches="tight")
    plt.close(fig)
    for path in (
        ROOT / "examples/general.svg",
        OUT / "architecture.svg",
        OUT / "scaling.svg",
    ):
        normalize_svg_whitespace(path)
    print("Wrote original figures, SVG example, CSV and JSON exports")


def normalize_svg_whitespace(path):
    """Keep generated SVG paths unchanged while avoiding trailing-space noise."""
    text = path.read_text(encoding="utf-8")
    path.write_text(
        "\n".join(line.rstrip() for line in text.splitlines()) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
