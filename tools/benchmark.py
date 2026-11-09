"""Reproducible timing plus isolated Python-allocation/Windows RSS measurements."""

import argparse
import csv
import ctypes
import gc
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from fortune import construct, Box
from fortune.io import random_sites


def windows_memory():
    if sys.platform != "win32":
        return {}
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t)
            for name in (
                "PeakWorkingSetSize",
                "WorkingSetSize",
                "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage",
                "QuotaPeakNonPagedPoolUsage",
                "QuotaNonPagedPoolUsage",
                "PagefileUsage",
                "PeakPagefileUsage",
            )
        ]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(Counters),
        wintypes.DWORD,
    ]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(
        kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    return dict(
        process_peak_rss_bytes=counters.PeakWorkingSetSize,
        process_working_set_bytes=counters.WorkingSetSize,
    )


def memory_sample(n, seed):
    points = random_sites(n, seed)
    gc.collect()
    tracemalloc.start()
    d = construct(points, Box(0, 0, 1, 1))
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return dict(
        n=n,
        python_peak_bytes=peak,
        python_retained_bytes=current,
        cells=len(d.cells),
        **windows_memory(),
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", type=int, nargs="+", default=[100, 1000, 10000])
    p.add_argument("--repeat", type=int, default=3)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--memory-child", type=int)
    p.add_argument("--out", default=str(ROOT / "results"))
    args = p.parse_args()
    if args.memory_child:
        print(json.dumps(memory_sample(args.memory_child, args.seed)))
        return
    if args.repeat < 1 or min(args.sizes) < 1:
        p.error("Sizes and repetition count must be positive")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows, raw = [], []
    construct(random_sites(40, args.seed), Box(0, 0, 1, 1))
    for n in args.sizes:
        points = random_sites(n, args.seed)
        elapsed = []
        for repetition in range(args.repeat):
            gc.collect()
            started = time.perf_counter()
            d = construct(points, Box(0, 0, 1, 1))
            seconds = time.perf_counter() - started
            elapsed.append(seconds)
            raw.append(
                dict(
                    n=n,
                    repetition=repetition,
                    seconds=seconds,
                    sweep_seconds=d.statistics["sweep_seconds"],
                    vertices=len(d.vertices),
                    edges=len(d.edges),
                )
            )
            del d
        memory = json.loads(
            subprocess.check_output(
                [
                    sys.executable,
                    __file__,
                    "--memory-child",
                    str(n),
                    "--seed",
                    str(args.seed),
                ],
                text=True,
            )
        )
        row = dict(
            median_seconds=statistics.median(elapsed),
            min_seconds=min(elapsed),
            max_seconds=max(elapsed),
            **memory,
        )
        rows.append(row)
        print(json.dumps(row), flush=True)
    meta = dict(
        actual_timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        python=sys.version,
        platform=platform.platform(),
        machine=platform.machine(),
        processor=platform.processor(),
        seed=args.seed,
        repetitions=args.repeat,
        timing_scope="deduplication, normalization, Fortune sweep, clipping, cell/edge assembly; excludes input generation, plotting, validation and export",
        memory_method="fresh subprocess per size; tracemalloc starts after input generation; process RSS includes interpreter and tracing overhead",
        results=rows,
        raw_timings=raw,
    )
    (out / "benchmark.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    with (out / "benchmark.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
