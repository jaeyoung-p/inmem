#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Plot Step 16 GAPBS IPC overhead from a parsed CSV."""

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

VARIANT_ORDER = ["aes", "aes_mac", "inmem", "inmem_low"]
VARIANT_LABELS = {
    "baseline": "Baseline",
    "aes": "C",
    "aes_mac": "C+I",
    "inmem": "InMem",
    "inmem_low": "InMem(Resize)",
}


def kernel_label(kernel: str) -> str:
    return kernel.replace("_", "-").upper()


def read_rows(csv_path: Path):
    rows = []
    with csv_path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            variant = row.get("variant", "")
            if variant not in VARIANT_LABELS:
                continue
            try:
                ipc = float(row["ipc"])
            except (KeyError, ValueError):
                continue
            if ipc <= 0:
                continue
            rows.append({**row, "ipc_value": ipc})
    return rows


def select_rows(rows):
    by_kernel_variant = defaultdict(dict)
    for row in rows:
        kernel = row["gapbs_kernel"]
        variant = row["variant"]
        previous = by_kernel_variant[kernel].get(variant)
        if previous is None or row["ipc_value"] > previous["ipc_value"]:
            by_kernel_variant[kernel][variant] = row

    selected = {}
    for kernel, variants in by_kernel_variant.items():
        baseline = variants.get("baseline")
        if baseline is None:
            continue
        baseline_ipc = baseline["ipc_value"]
        if baseline_ipc <= 0:
            continue
        selected[kernel] = {
            variant: baseline_ipc / variants[variant]["ipc_value"]
            for variant in VARIANT_ORDER
            if variant in variants
        }
    return selected


def write_plot(selected, outpath: Path):
    kernels = sorted(selected)
    geomean = {}
    for variant in VARIANT_ORDER:
        slowdowns = [
            selected[kernel][variant]
            for kernel in kernels
            if variant in selected[kernel] and selected[kernel][variant] > 0
        ]
        if len(slowdowns) == len(kernels):
            geomean[variant] = math.prod(slowdowns) ** (1.0 / len(slowdowns))
    if geomean:
        kernels = kernels + ["__geomean__"]
        selected = {**selected, "__geomean__": geomean}

    bar_width = 0.18
    group_gap = 0.35
    group_width = len(VARIANT_ORDER) * bar_width + group_gap
    x_centers = [i * group_width for i in range(len(kernels))]

    fig, ax = plt.subplots(figsize=(5, 3), constrained_layout=True)
    colors = ["#4C78A8", "#F58518", "#54A24B", "#B279A2"]

    for idx, variant in enumerate(VARIANT_ORDER):
        xs = [
            center + (idx - (len(VARIANT_ORDER) - 1) / 2) * bar_width
            for center in x_centers
        ]
        ys = [(selected[kernel].get(variant, 1.0) - 1.0) * 100.0 for kernel in kernels]
        ax.bar(
            xs,
            ys,
            width=bar_width,
            label=VARIANT_LABELS[variant],
            color=colors[idx],
        )

    ax.axhline(0.0, color="#222222", linewidth=0.8, alpha=0.45)
    ax.set_ylabel("Overhead (%)")
    ax.set_xticks(x_centers)
    ax.set_xticklabels(
        ["GeoMean" if kernel == "__geomean__" else kernel_label(kernel) for kernel in kernels]
    )
    ax.set_ylim(bottom=0, top=35)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, ncols=len(VARIANT_ORDER), loc="upper center")

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "csv_path",
        type=Path,
        default=Path(
            "artifacts/figures/gapbs_interleave_ipc/all_runs/gapbs_ipc_results.csv"
        ),
        nargs="?",
        help="Parsed Step 16 CSV. Default: all_runs/gapbs_ipc_results.csv.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "artifacts/figures/gapbs_interleave_ipc/all_runs/ipc_overhead.png"
        ),
        help="Output PNG path.",
    )
    args = parser.parse_args()

    selected = select_rows(read_rows(args.csv_path))
    if not selected:
        raise SystemExit("no complete baseline-normalizable kernel groups found")

    write_plot(selected, args.output)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
