#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Validate Step 12 bandwidth/latency config and readfile packaging."""

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    parser.add_argument(
        "--min-cores",
        type=int,
        default=8,
        help="Minimum expected KVM and Timing CPU instances. Default: 8.",
    )
    args = parser.parse_args()

    config_ini = args.outdir / "config.ini"
    if not config_ini.is_file():
        raise SystemExit(f"missing {config_ini}")

    config_script = Path(__file__).with_name("x86_two_tier_numa_bwlat.py")
    if config_script.is_file():
        script_text = config_script.read_text()
        if "LargeMemoryX86Board" not in script_text:
            raise SystemExit("Step 12 FS script should instantiate LargeMemoryX86Board")
        if "num_cores=args.num_cores" not in script_text:
            raise SystemExit("Step 12 FS script should expose --num-cores")
        if "default=8" not in script_text:
            raise SystemExit("Step 12 should default to eight guest cores")
        if "--bwl-max-workers" not in script_text:
            raise SystemExit("Step 12 should expose benchmark-size overrides")

    readfiles = sorted(args.outdir.glob("readfile_*"))
    if len(readfiles) != 1:
        raise SystemExit(f"expected one readfile artifact, found {len(readfiles)}")

    config = config_ini.read_text()
    readfile = readfiles[0].read_text()

    if config.count("type=MemCtrl") != 18:
        raise SystemExit("expected eighteen MemCtrl instances")
    if config.count("type=DRAMInterface") != 18:
        raise SystemExit("expected eighteen DRAMInterface instances")
    if config.count("type=RangeAddrMapper") != 0:
        raise SystemExit("node 0 ranges should use direct controllers under KVM")
    if config.count("type=CxlMemLink") != 1:
        raise SystemExit("expected one shared CxlMemLink instance")
    if config.count("type=X86KvmCPU") < args.min_cores:
        raise SystemExit(f"expected at least {args.min_cores} KVM start CPUs")
    if config.count("type=BaseTimingSimpleCPU") < args.min_cores:
        raise SystemExit(
            f"expected at least {args.min_cores} Timing switch CPUs"
        )

    for needle in (
        "flit_size_bytes=256",
        "m2s_latency=0",
        "s2m_latency=0",
        "type=X86ACPISrat",
        "type=X86ACPISlit",
    ):
        if needle not in config:
            raise SystemExit(f"missing config evidence: {needle}")
    for needle in (
        "m2s_latency=80000",
        "s2m_latency=80000",
    ):
        if needle in config:
            raise SystemExit(
                "node 1 should not have fixed CXL base latency in the "
                f"default validation config: found {needle}"
            )

    for needle in (
        "pthread_create",
        "SYS_mbind",
        "MPOL_BIND",
        "BWL_RESULT",
        "BWL_MAX_WORKERS",
        'BWL_WORKER_MIB="${BWL_WORKER_MIB:-16}"',
        'BWL_LATENCY_MIB="${BWL_LATENCY_MIB:-64}"',
        "BWL_RECOMMENDED_LATENCY_MIB",
        "BWL_LATENCY_ITERS",
        "BWL_CPU_MHZ",
        "rdtsc",
        "=== STEP12 ROI SWITCH ===",
        "gem5-bridge hypercall 4",
        "for node in 0 1",
        'numactl --cpunodebind=0 --membind="${node}"',
        "=== STEP12 COMPLETE ===",
    ):
        if needle not in readfile:
            raise SystemExit(f"missing readfile evidence: {needle}")

    print("Step 12 bandwidth/latency packaging validation passed")
    print("- FS script uses LargeMemoryX86Board")
    print(f"- config exposes at least {args.min_cores} guest cores")
    print("- config preserves eighteen DDR5-derived memory interfaces/controllers")
    print("- config includes direct node 0 controllers and one shared slow CxlMemLink bottleneck")
    print("- default CXL fixed base latency is zero for both directions")
    print("- config contains SRAT/SLIT NUMA tables")
    print("- readfile embeds the pthread/mbind bandwidth-latency benchmark")
    print("- readfile runs the benchmark for NUMA nodes 0 and 1")
    print("- readfile switches to Timing at the benchmark ROI boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
