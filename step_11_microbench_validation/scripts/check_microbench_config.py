#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Validate Step 11 config/readfile packaging."""

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    args = parser.parse_args()

    config_ini = args.outdir / "config.ini"
    if not config_ini.is_file():
        raise SystemExit(f"missing {config_ini}")

    config_script = Path(__file__).with_name("x86_two_tier_numa_microbench.py")
    if config_script.is_file():
        script_text = config_script.read_text()
        if "LargeMemoryX86Board" not in script_text:
            raise SystemExit("Step 11 FS script should instantiate LargeMemoryX86Board")
        if "from gem5.components.boards.x86_board import X86Board" in script_text:
            raise SystemExit("Step 11 FS script should not import stock X86Board")

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
    if config.count("type=CxlMemLink") != 2:
        raise SystemExit("expected two CxlMemLink instances")

    for needle in (
        "type=X86KvmCPU",
        "type=BaseTimingSimpleCPU",
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
    if "static_frontend_latency=40000" in config:
        raise SystemExit("slow controller frontend latency should not be inflated")
    if "static_backend_latency=40000" in config:
        raise SystemExit("slow controller backend latency should not be inflated")
    if config.count("static_frontend_latency=10000") < 18:
        raise SystemExit("expected all eighteen MemCtrls to use 10ns frontend latency")
    if config.count("static_backend_latency=10000") < 18:
        raise SystemExit("expected all eighteen MemCtrls to use 10ns backend latency")

    for needle in (
        "SYS_mbind",
        "MPOL_BIND",
        "MB_RESULT",
        "read_seq",
        "write_seq",
        "readwrite_seq",
        "read_stride",
        "chase",
        "=== STEP11 ROI SWITCH ===",
        "gem5-bridge hypercall 4",
        'for node in 0 1',
        'numactl --cpunodebind=0 --membind="${node}"',
        "=== STEP11 COMPLETE ===",
    ):
        if needle not in readfile:
            raise SystemExit(f"missing readfile evidence: {needle}")

    print("Step 11 microbenchmark packaging validation passed")
    print("- FS script uses LargeMemoryX86Board")
    print("- config contains KVM start and Timing switch cores")
    print("- config preserves eighteen DDR5-derived memory interfaces/controllers")
    print("- config includes direct node 0 controllers and slow CxlMemLinks")
    print("- default CXL fixed base latency is zero for both directions")
    print("- config contains SRAT/SLIT NUMA tables")
    print("- readfile embeds the mbind-based benchmark suite")
    print("- readfile uses numactl command path from the customized guest image")
    print("- readfile switches to Timing at the benchmark ROI boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
