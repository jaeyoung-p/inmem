#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Parse Step 16 gem5 stats into an IPC CSV."""

import argparse
import csv
import json
import math
import re
from pathlib import Path


STAT_RE = re.compile(
    r"^([A-Za-z0-9_:\.\-]+)\s+([-+0-9.eE]+|nan|inf|-inf)\b.*$",
    re.IGNORECASE,
)


def read_stats(path: Path):
    stats = {}
    for line in path.read_text(errors="replace").splitlines():
        match = STAT_RE.match(line.strip())
        if match is None:
            continue
        name, value = match.groups()
        try:
            stats[name] = float(value)
        except ValueError:
            continue
    return stats


def read_cache_line_size(point_dir: Path):
    config_ini = point_dir / "config.ini"
    if not config_ini.is_file():
        return 64
    match = re.search(r"(?m)^cache_line_size=(\d+)$", config_ini.read_text())
    return int(match.group(1)) if match else 64


def find_first(stats, patterns):
    for pattern in patterns:
        regex = re.compile(pattern)
        matches = [
            (name, value)
            for name, value in stats.items()
            if regex.search(name) and math.isfinite(value)
        ]
        if matches:
            matches.sort(key=lambda item: item[0])
            return matches[0][1], matches[0][0]
    return None, ""


def sum_exact(stats, names):
    return sum(stats.get(name, 0.0) for name in names)


def sum_matching(stats, suffix):
    total = 0.0
    found = False
    for name, value in stats.items():
        if name.endswith(suffix):
            total += value
            found = True
    return total if found else 0.0


def point_completed(point_dir: Path):
    status_path = point_dir / "status.txt"
    if not status_path.is_file():
        return False
    return status_path.read_text().strip() == "0"


def parse_point(point_dir: Path, include_incomplete: bool):
    metadata_path = point_dir / "step16_point.json"
    stats_path = point_dir / "stats.txt"
    if not metadata_path.is_file() or not stats_path.is_file():
        return None
    if not include_incomplete and not point_completed(point_dir):
        return None

    metadata = json.loads(metadata_path.read_text())
    stats = read_stats(stats_path)

    sim_insts = stats.get("simInsts", 0.0)
    sim_ticks = stats.get("simTicks", 0.0)
    direct_ipc, ipc_stat = find_first(
        stats,
        [
            r"^board\.processor\.switch\.core\.ipc$",
            r"^board\.processor\.switch\.core\.commitStats[0-9]+\.ipc$",
            r"\.ipc$",
            r"\.committedInstsPerCycle$",
        ],
    )
    num_cycles, cycles_stat = find_first(
        stats,
        [
            r"^board\.processor\.switch\.core\.numCycles$",
            r"\.core\.numCycles$",
            r"\.numCycles$",
        ],
    )

    ipc = direct_ipc
    if ipc is None and num_cycles and num_cycles > 0:
        ipc = sim_insts / num_cycles

    cache_line_size = read_cache_line_size(point_dir)
    llc_accesses = sum_exact(
        stats,
        [
            "board.cache_hierarchy.ruby_system.L2Cache_Controller.L1_GETS",
            "board.cache_hierarchy.ruby_system.L2Cache_Controller.L1_GETX",
        ],
    )
    llc_misses = sum_exact(
        stats,
        [
            "board.cache_hierarchy.ruby_system.L2Cache_Controller.NP.L1_GETS",
            "board.cache_hierarchy.ruby_system.L2Cache_Controller.NP.L1_GETX",
        ],
    )
    llc_hits = max(llc_accesses - llc_misses, 0.0)
    llc_hit_rate = llc_hits / llc_accesses if llc_accesses > 0 else None
    llc_mpki = llc_misses * 1000.0 / sim_insts if sim_insts > 0 else None
    llc_fetched_bytes = llc_misses * cache_line_size
    llc_fetched_bytes_per_inst = (
        llc_fetched_bytes / sim_insts if sim_insts > 0 else None
    )

    ruby_seq_hits = stats.get(
        "board.cache_hierarchy.ruby_system.m_hitLatencyHistSeqr::total", 0.0
    )
    ruby_seq_misses = stats.get(
        "board.cache_hierarchy.ruby_system.m_missLatencyHistSeqr::total", 0.0
    )
    ruby_seq_accesses = ruby_seq_hits + ruby_seq_misses
    ruby_seq_hit_rate = (
        ruby_seq_hits / ruby_seq_accesses if ruby_seq_accesses > 0 else None
    )

    return {
        "variant": metadata.get("variant", point_dir.name),
        "gapbs_kernel": metadata.get("gapbs_kernel", "pr_spmv"),
        "gapbs_scale": metadata.get("gapbs_scale", ""),
        "gapbs_trials": metadata.get("gapbs_trials", ""),
        "num_cores": metadata.get("num_cores", ""),
        "omp_threads": metadata.get("omp_threads", ""),
        "roi_cpu": metadata.get("roi_cpu", ""),
        "aes_latency": metadata.get("aes_latency", ""),
        "integrity_mac_enable": metadata.get("integrity_mac_enable", ""),
        "cxl_extra_data_slots": metadata.get("cxl_extra_data_slots", ""),
        "sim_insts": int(sim_insts),
        "num_cycles": int(num_cycles or 0),
        "ipc": "" if ipc is None else f"{ipc:.8f}",
        "sim_ticks": int(sim_ticks),
        "cache_line_size": cache_line_size,
        "llc_accesses": int(llc_accesses),
        "llc_hits": int(llc_hits),
        "llc_misses": int(llc_misses),
        "llc_mpki": "" if llc_mpki is None else f"{llc_mpki:.8f}",
        "llc_hit_rate": "" if llc_hit_rate is None else f"{llc_hit_rate:.8f}",
        "llc_fetched_bytes": int(llc_fetched_bytes),
        "llc_fetched_bytes_per_inst": (
            ""
            if llc_fetched_bytes_per_inst is None
            else f"{llc_fetched_bytes_per_inst:.8f}"
        ),
        "ruby_sequencer_accesses": int(ruby_seq_accesses),
        "ruby_sequencer_hit_rate": (
            "" if ruby_seq_hit_rate is None else f"{ruby_seq_hit_rate:.8f}"
        ),
        "integrity_mac_read_reqs": int(sum_matching(stats, "integrityMacReadReqs")),
        "integrity_mac_read_bytes": int(sum_matching(stats, "integrityMacReadBytes")),
        "integrity_mac_write_reqs": int(sum_matching(stats, "integrityMacWriteReqs")),
        "integrity_mac_write_bytes": int(sum_matching(stats, "integrityMacWriteBytes")),
        "ipc_stat": ipc_stat,
        "cycles_stat": cycles_stat,
        "point_dir": str(point_dir),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path, help="Step 16 m5out root.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("artifacts/figures/gapbs_interleave_ipc"),
        help="Directory for parsed CSV output.",
    )
    parser.add_argument(
        "--include-incomplete",
        action="store_true",
        help="Include point directories without status.txt=0. Default: skip them.",
    )
    args = parser.parse_args()

    rows = []
    for metadata_path in sorted(args.outdir.glob("*/step16_point.json")):
        row = parse_point(metadata_path.parent, args.include_incomplete)
        if row is not None:
            rows.append(row)

    args.output_root.mkdir(parents=True, exist_ok=True)
    output_csv = args.output_root / "gapbs_ipc_results.csv"
    fieldnames = [
        "variant",
        "gapbs_kernel",
        "gapbs_scale",
        "gapbs_trials",
        "num_cores",
        "omp_threads",
        "roi_cpu",
        "aes_latency",
        "integrity_mac_enable",
        "cxl_extra_data_slots",
        "sim_insts",
        "num_cycles",
        "ipc",
        "sim_ticks",
        "cache_line_size",
        "llc_accesses",
        "llc_hits",
        "llc_misses",
        "llc_mpki",
        "llc_hit_rate",
        "llc_fetched_bytes",
        "llc_fetched_bytes_per_inst",
        "ruby_sequencer_accesses",
        "ruby_sequencer_hit_rate",
        "integrity_mac_read_reqs",
        "integrity_mac_read_bytes",
        "integrity_mac_write_reqs",
        "integrity_mac_write_bytes",
        "ipc_stat",
        "cycles_stat",
        "point_dir",
    ]
    with output_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} row(s) to {output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
