#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Plot one unified bandwidth/latency figure from generated result CSVs."""

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURE_ROOT = REPO_ROOT / "artifacts/figures"

NAME_MAPPING = {
    12: {
        0: "Local",
        1: "CXL",
    },
    13: {
        0: "Local+AES",
        1: "CXL+AES",
    },
    14: {
        1: "CXL+AES+ExtraSlot",
    },
}

CSV_PATHS = {
    12: REPO_ROOT
    / "artifacts/figures/dma_bwlat/step_12_bw_latency_curve/"
    / "m5out_dma_16x4_ddr5_4400_64k/dma_bwlat_results.csv",
    13: REPO_ROOT
    / "artifacts/figures/dma_bwlat/step_13_aes_bw_latency_curve/"
    / "m5out_dma_aes_16x4_ddr5_4400_64k/dma_bwlat_results.csv",
    14: REPO_ROOT
    / "artifacts/figures/dma_bwlat/step_14_extra_cxl_data_slot/"
    / "m5out_dma_aes_16x4_ddr5_4400_64k/dma_bwlat_results.csv",
}

OUTPUT_CSV = FIGURE_ROOT / "unified_dma_bwlat.csv"
OUTPUT_PNG = FIGURE_ROOT / "unified_dma_bwlat.png"


def format_gib_s(value: float) -> str:
    if abs(value) < 0.005:
        return "0"
    if abs(value - round(value)) < 0.005:
        return str(int(round(value)))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def power_of_two_ticks(max_value: float):
    if max_value <= 1.0:
        return [0, 1]

    limit = 2 ** math.ceil(math.log2(max_value))
    ticks = [0]
    value = 1
    while value <= limit:
        ticks.append(value)
        value *= 2
    return ticks


def equal_power_of_two_position(value: float) -> float:
    if value <= 0.0:
        return 0.0
    return 1.0 + math.log2(value)


def read_rows():
    rows = []
    for step, csv_path in CSV_PATHS.items():
        if not csv_path.is_file():
            raise SystemExit(f"missing generated CSV for step {step}: {csv_path}")

        with csv_path.open(newline="") as csv_file:
            for row in csv.DictReader(csv_file):
                node = int(row["node"])
                label = NAME_MAPPING.get(step, {}).get(node)
                if label is None:
                    continue
                rows.append(
                    {
                        **row,
                        "step": step,
                        "node": node,
                        "label": label,
                        "achieved_bandwidth_gib_s": float(
                            row["achieved_bandwidth_gib_s"]
                        ),
                        "latency_ns": float(row["latency_ns"]),
                        "offered_rate_Bps": float(row["offered_rate_Bps"]),
                    }
                )
    return rows


def write_unified_csv(rows):
    columns = [
        "label",
        "step",
        "node",
        "offered_rate",
        "offered_rate_Bps",
        "offered_rate_gib_s",
        "achieved_bandwidth_Bps",
        "achieved_bandwidth_gib_s",
        "latency_ns",
        "latency_cycles",
        "point_dir",
    ]
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_plot(rows):
    fig, ax = plt.subplots(figsize=(9.4, 5.8), constrained_layout=True)

    labels = [
        label
        for step in sorted(NAME_MAPPING)
        for label in NAME_MAPPING[step].values()
    ]
    for label in labels:
        series = [row for row in rows if row["label"] == label]
        if not series:
            continue
        series.sort(key=lambda row: row["achieved_bandwidth_gib_s"])
        ax.plot(
            [
                equal_power_of_two_position(row["achieved_bandwidth_gib_s"])
                for row in series
            ],
            [row["latency_ns"] for row in series],
            marker="o",
            linewidth=2,
            label=label,
        )

    max_x = max((row["achieved_bandwidth_gib_s"] for row in rows), default=1.0)
    x_ticks = power_of_two_ticks(max_x)
    ax.set_xlim(0.75, len(x_ticks) - 0.75)
    ax.set_xticks(range(len(x_ticks)))
    ax.set_xticklabels([format_gib_s(value) for value in x_ticks])
    ax.set_xlabel("Achieved injected DMA read bandwidth (GiB/s)")
    ax.set_ylabel("Latency (ns)")
    ax.set_title("Unified DMA Bandwidth vs Latency")
    ax.grid(True, which="major", alpha=0.35)
    ax.legend()

    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=180)
    plt.close(fig)


def main() -> int:
    rows = read_rows()
    rows.sort(key=lambda row: (row["label"], row["offered_rate_Bps"]))
    write_unified_csv(rows)
    write_plot(rows)
    print(f"Wrote {OUTPUT_CSV}")
    print(f"Wrote {OUTPUT_PNG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
