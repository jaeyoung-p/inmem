#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Parse Step 16 gem5 stats into an IPC CSV."""
""" python3 step_16_gapbs_interleave_ipc/scripts/parse_gapbs_ipc_stats.py \
    --output-root artifacts/figures/gapbs_interleave_ipc/all_runs \
    step_16_gapbs_interleave_ipc/artifacts
"""

import argparse
import csv
import json
import math
import re
import sys
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


def read_roi_core_stats(stats):
    cores = {}
    patterns = {
        "cycles": re.compile(r"^board\.processor\.switch(?P<core>\d*)\.core\.numCycles$"),
        "ipc": re.compile(r"^board\.processor\.switch(?P<core>\d*)\.core\.ipc$"),
        "insts": re.compile(
            r"^board\.processor\.switch(?P<core>\d*)\.core\.commitStats0\.numInsts$"
        ),
    }

    for name, value in stats.items():
        if not math.isfinite(value):
            continue
        for field, regex in patterns.items():
            match = regex.match(name)
            if match is None:
                continue
            core = int(match.group("core") or 0)
            cores.setdefault(core, {})[field] = value
            break

    return cores


def format_core_values(cores, field):
    parts = []
    for core in sorted(cores):
        value = cores[core].get(field)
        if value is None:
            continue
        if field == "ipc":
            parts.append(f"{core}:{value:.8f}")
        else:
            parts.append(f"{core}:{int(value)}")
    return ";".join(parts)


def point_completed(point_dir: Path):
    stats_path = point_dir / "stats.txt"
    return stats_path.is_file() and stats_path.stat().st_size > 0


def point_skip_reason(point_dir: Path):
    metadata_path = point_dir / "step16_point.json"
    stats_path = point_dir / "stats.txt"
    if not metadata_path.is_file():
        return "missing step16_point.json"
    if not stats_path.is_file():
        return "missing stats.txt"
    if stats_path.stat().st_size == 0:
        return "empty stats.txt"
    return ""


def point_dirs(root: Path):
    if (root / "step16_point.json").is_file():
        yield root
        return

    for metadata_path in sorted(root.rglob("step16_point.json")):
        yield metadata_path.parent


def parse_point(point_dir: Path, include_incomplete: bool):
    metadata_path = point_dir / "step16_point.json"
    stats_path = point_dir / "stats.txt"
    if not metadata_path.is_file() or not stats_path.is_file():
        return None
    if not include_incomplete and not point_completed(point_dir):
        reason = point_skip_reason(point_dir)
        print(
            f"warning: skipping incomplete point ({reason}): {point_dir}",
            file=sys.stderr,
        )
        return None

    metadata = json.loads(metadata_path.read_text())
    stats = read_stats(stats_path)

    sim_insts = stats.get("simInsts", 0.0)
    sim_ticks = stats.get("simTicks", 0.0)
    roi_cores = read_roi_core_stats(stats)
    roi_core_cycles = [
        core.get("cycles", 0.0)
        for core in roi_cores.values()
        if core.get("cycles", 0.0) > 0
    ]
    roi_core_insts = [
        core.get("insts", 0.0)
        for core in roi_cores.values()
        if core.get("insts", 0.0) > 0
    ]
    num_cycles = max(roi_core_cycles, default=0.0)
    aggregate_insts = sum(roi_core_insts) if roi_core_insts else sim_insts
    ipc = aggregate_insts / num_cycles if num_cycles > 0 else None
    active_roi_cores = sum(
        1
        for core in roi_cores.values()
        if core.get("cycles", 0.0) > 0 and core.get("insts", 0.0) > 0
    )
    max_core_ipc = max(
        (
            core.get("ipc", 0.0)
            for core in roi_cores.values()
            if core.get("ipc") is not None and core.get("ipc", 0.0) > 0
        ),
        default=None,
    )
    ipc_stat = "sum(switch*.commitStats0.numInsts)/max(switch*.numCycles)"
    cycles_stat = "max(board.processor.switch*.core.numCycles)"

    if not include_incomplete and (sim_insts <= 0 or not num_cycles or num_cycles <= 0):
        print(
            f"warning: skipping point without measured ROI stats: {point_dir}",
            file=sys.stderr,
        )
        return None

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
        "run_dir": point_dir.parent.name,
        "variant": metadata.get("variant", point_dir.name),
        "gapbs_kernel": metadata.get("gapbs_kernel", "pr_spmv"),
        "gapbs_scale": metadata.get("gapbs_scale", ""),
        "gapbs_trials": metadata.get("gapbs_trials", ""),
        "num_cores": metadata.get("num_cores", ""),
        "omp_threads": metadata.get("omp_threads", ""),
        "roi_cpu": metadata.get("roi_cpu", ""),
        "roi_warmup_insts": metadata.get("roi_warmup_insts", ""),
        "roi_max_insts": metadata.get("roi_max_insts", ""),
        "l3_size": metadata.get("l3_size", ""),
        "l3_assoc": metadata.get("l3_assoc", ""),
        "aes_latency": metadata.get("aes_latency", ""),
        "integrity_mac_enable": metadata.get("integrity_mac_enable", ""),
        "cxl_extra_data_slots": metadata.get("cxl_extra_data_slots", ""),
        "sim_insts": int(sim_insts),
        "num_cycles": int(num_cycles or 0),
        "ipc": "" if ipc is None else f"{ipc:.8f}",
        "active_roi_cores": active_roi_cores,
        "max_core_ipc": "" if max_core_ipc is None else f"{max_core_ipc:.8f}",
        "core_ipcs": format_core_values(roi_cores, "ipc"),
        "core_cycles": format_core_values(roi_cores, "cycles"),
        "core_insts": format_core_values(roi_cores, "insts"),
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
        help="Include point directories without non-empty stats.txt. Default: skip them.",
    )
    args = parser.parse_args()

    rows = []
    total_points = 0
    for point_dir in point_dirs(args.outdir):
        total_points += 1
        row = parse_point(point_dir, args.include_incomplete)
        if row is not None:
            rows.append(row)

    args.output_root.mkdir(parents=True, exist_ok=True)
    output_csv = args.output_root / "gapbs_ipc_results.csv"
    fieldnames = [
        "run_dir",
        "variant",
        "gapbs_kernel",
        "gapbs_scale",
        "gapbs_trials",
        "num_cores",
        "omp_threads",
        "roi_cpu",
        "roi_warmup_insts",
        "roi_max_insts",
        "l3_size",
        "l3_assoc",
        "aes_latency",
        "integrity_mac_enable",
        "cxl_extra_data_slots",
        "sim_insts",
        "num_cycles",
        "ipc",
        "active_roi_cores",
        "max_core_ipc",
        "core_ipcs",
        "core_cycles",
        "core_insts",
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

    skipped = total_points - len(rows)
    print(f"wrote {len(rows)} row(s) to {output_csv}")
    if skipped:
        print(f"skipped {skipped} incomplete/unparseable point(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
