#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Plot Step 12 achieved DMA bandwidth versus latency."""

import argparse
import csv
import json
import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "artifacts/figures/dma_bwlat"

LAT_RE = re.compile(
    r"LAT_RESULT node=(?P<node>\d+) "
    r"latency_ns=(?P<latency_ns>[-+0-9.eE]+) "
    r"latency_cycles=(?P<latency_cycles>[-+0-9.eE]+)"
)
STAT_RE = re.compile(
    r"\S+step12_dma_injector\d+\.(?P<stat>readBW|bytesRead)\s+"
    r"(?P<value>[-+0-9.eE]+)"
)
SIM_SECONDS_RE = re.compile(r"^simSeconds\s+([-+0-9.eE]+)")


def point_dirs(root: Path):
    if (root / "step12_point.json").is_file():
        yield root
        return

    for point_json in sorted(root.rglob("step12_point.json")):
        yield point_json.parent


def parse_rate_Bps(rate_text: str) -> float:
    text = rate_text.strip()
    if text.lower() in {
        "0",
        "0b/s",
        "0kb/s",
        "0mb/s",
        "0gb/s",
        "0kib/s",
        "0mib/s",
        "0gib/s",
    }:
        return 0.0

    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*([KMG]?i?)?B/s", text, re.I)
    if not match:
        raise RuntimeError(f"unsupported DMA rate format: {rate_text}")

    value = float(match.group(1))
    unit = (match.group(2) or "").lower()
    scale = {
        "": 1.0,
        "k": 1e3,
        "m": 1e6,
        "g": 1e9,
        "ki": 1024.0,
        "mi": 1024.0**2,
        "gi": 1024.0**3,
    }[unit]
    return value * scale


def format_rate_Bps(rate_Bps: float) -> str:
    if rate_Bps == 0:
        return "0"
    if float(rate_Bps).is_integer():
        return f"{int(rate_Bps)}B/s"
    return f"{rate_Bps:.6f}".rstrip("0").rstrip(".") + "B/s"


def offered_rate(metadata: dict):
    dma_injectors = int(metadata.get("dma_injectors", 0))
    per_injector_rate = metadata.get(
        "dma_per_injector_rate", metadata.get("dma_rate", "0")
    )
    per_injector_rate_Bps = float(
        metadata.get(
            "dma_per_injector_rate_Bps",
            parse_rate_Bps(per_injector_rate),
        )
    )

    if "dma_total_rate_Bps" in metadata:
        offered_rate_Bps = float(metadata["dma_total_rate_Bps"])
        offered_rate_text = metadata.get(
            "dma_total_rate", format_rate_Bps(offered_rate_Bps)
        )
    else:
        offered_rate_Bps = per_injector_rate_Bps * dma_injectors
        offered_rate_text = (
            metadata.get("dma_rate", format_rate_Bps(offered_rate_Bps))
            if dma_injectors <= 1
            else format_rate_Bps(offered_rate_Bps)
        )

    return {
        "dma_injectors": dma_injectors,
        "dma_per_injector_rate": per_injector_rate,
        "dma_per_injector_rate_Bps": per_injector_rate_Bps,
        "offered_rate": offered_rate_text,
        "offered_rate_Bps": offered_rate_Bps,
        "offered_rate_gib_s": offered_rate_Bps / (1024.0**3),
    }


def read_latency(point_dir: Path):
    serial_path = point_dir / "board.pc.com_1.device"
    if not serial_path.is_file():
        return None

    for line in serial_path.read_text(errors="ignore").splitlines():
        match = LAT_RE.search(line)
        if match:
            return {
                "latency_node": int(match.group("node")),
                "latency_ns": float(match.group("latency_ns")),
                "latency_cycles": float(match.group("latency_cycles")),
            }

    return None


def read_dma_stats(point_dir: Path):
    stats_path = point_dir / "stats.txt"
    if not stats_path.is_file():
        return None

    total_read_bw = 0.0
    total_bytes_read = 0.0
    sim_seconds = None
    saw_dma_stat = False

    for raw_line in stats_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("-"):
            continue
        match = STAT_RE.match(line)
        if match:
            saw_dma_stat = True
            value = float(match.group("value"))
            if match.group("stat") == "readBW":
                total_read_bw += value
            elif match.group("stat") == "bytesRead":
                total_bytes_read += value
            continue
        sim_match = SIM_SECONDS_RE.match(line)
        if sim_match:
            sim_seconds = float(sim_match.group(1))

    if total_read_bw == 0.0 and total_bytes_read > 0.0 and sim_seconds:
        total_read_bw = total_bytes_read / sim_seconds

    return {
        "achieved_bandwidth_Bps": total_read_bw,
        "achieved_bandwidth_gib_s": total_read_bw / (1024.0**3),
        "bytes_read": total_bytes_read,
        "has_dma_stats": saw_dma_stat,
    }


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


def output_dir_for(input_dir: Path, output_root: Path) -> Path:
    resolved = input_dir.resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT)
        parts = relative.parts
    except ValueError:
        safe_name = resolved.as_posix().strip("/").replace("/", "__")
        return output_root / safe_name

    if "artifacts" in parts:
        artifact_index = parts.index("artifacts")
        parts = parts[:artifact_index] + parts[artifact_index + 1 :]

    return output_root.joinpath(*parts)


def write_csv(rows, outpath: Path):
    columns = [
        "node",
        "offered_rate",
        "offered_rate_Bps",
        "offered_rate_gib_s",
        "achieved_bandwidth_Bps",
        "achieved_bandwidth_gib_s",
        "bytes_read",
        "dma_per_injector_rate",
        "dma_per_injector_rate_Bps",
        "dma_injectors",
        "latency_ns",
        "latency_cycles",
        "point_dir",
    ]
    with outpath.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_plot(rows, outpath: Path):
    fig, ax = plt.subplots(figsize=(8.6, 5.4), constrained_layout=True)

    for node in sorted({row["node"] for row in rows}):
        node_rows = [row for row in rows if row["node"] == node]
        node_rows.sort(key=lambda row: (row["offered_rate_Bps"], row["point_dir"]))
        ax.plot(
            [
                equal_power_of_two_position(row["achieved_bandwidth_gib_s"])
                for row in node_rows
            ],
            [row["latency_ns"] for row in node_rows],
            marker="o",
            linewidth=2,
            label=f"node{node}",
        )

    max_x = max((row["achieved_bandwidth_gib_s"] for row in rows), default=1.0)
    x_ticks = power_of_two_ticks(max_x)
    ax.set_xlim(0.75, len(x_ticks) - 0.75)
    ax.set_ylim(top=800)
    ax.set_xticks(range(len(x_ticks)))
    ax.set_xticklabels([format_gib_s(value) for value in x_ticks])
    ax.set_xlabel("Achieved injected DMA read bandwidth (GiB/s)")
    ax.set_ylabel("Latency (ns)")
    ax.set_title("Achieved DMA Bandwidth vs Latency")
    ax.grid(True, which="major", alpha=0.35)
    if rows:
        ax.legend()
    fig.savefig(outpath, dpi=160)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=(
            "Directory root for generated CSV/PNG outputs. Default: "
            f"{DEFAULT_OUTPUT_ROOT}"
        ),
    )
    args = parser.parse_args()

    rows = []
    for point_dir in point_dirs(args.outdir):
        latency = read_latency(point_dir)
        if latency is None:
            continue

        metadata = json.loads((point_dir / "step12_point.json").read_text())
        rate = offered_rate(metadata)
        dma_stats = read_dma_stats(point_dir)
        if dma_stats is None:
            if rate["offered_rate_Bps"] == 0.0:
                dma_stats = {
                    "achieved_bandwidth_Bps": 0.0,
                    "achieved_bandwidth_gib_s": 0.0,
                    "bytes_read": 0.0,
                    "has_dma_stats": False,
                }
            else:
                continue
        if rate["offered_rate_Bps"] > 0.0 and not dma_stats["has_dma_stats"]:
            continue
        rows.append(
            {
                "point_dir": str(point_dir),
                "node": int(metadata["node"]),
                **rate,
                **dma_stats,
                "latency_ns": latency["latency_ns"],
                "latency_cycles": latency["latency_cycles"],
            }
        )

    rows.sort(key=lambda row: (row["node"], row["offered_rate_Bps"], row["point_dir"]))

    output_dir = output_dir_for(args.outdir, args.output_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "dma_bwlat_results.csv"
    png_path = output_dir / "dma_bwlat_results.png"
    write_csv(rows, csv_path)
    write_plot(rows, png_path)
    print(f"Parsed {len(rows)} point(s)")
    print(f"Wrote {csv_path}")
    print(f"Wrote {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
