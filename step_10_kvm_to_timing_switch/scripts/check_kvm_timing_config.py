#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Validate the Step 10 KVM-to-Timing config object graph."""

import argparse
from pathlib import Path


def _parse_config_ini(path: Path) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    current = None
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            sections[current] = {}
            continue
        if current is None or "=" not in line:
            continue
        key, value = line.split("=", 1)
        sections[current][key] = value
    return sections


def _count_type(sections: dict[str, dict[str, str]], simobject_type: str) -> int:
    return sum(1 for data in sections.values() if data.get("type") == simobject_type)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    args = parser.parse_args()

    config_ini = args.outdir / "config.ini"
    if not config_ini.is_file():
        raise SystemExit(f"missing {config_ini}")

    config_script = Path(__file__).with_name("x86_two_tier_kvm_to_timing_roi.py")
    if config_script.is_file():
        script_text = config_script.read_text()
        if "LargeMemoryX86Board" not in script_text:
            raise SystemExit("Step 10 FS script should instantiate LargeMemoryX86Board")
        if "from gem5.components.boards.x86_board import X86Board" in script_text:
            raise SystemExit("Step 10 FS script should not import stock X86Board")

    sections = _parse_config_ini(config_ini)
    if _count_type(sections, "X86KvmCPU") != 2:
        raise SystemExit("expected two starting X86KvmCPU cores")
    if _count_type(sections, "BaseTimingSimpleCPU") != 2:
        raise SystemExit("expected two switched BaseTimingSimpleCPU cores")
    if _count_type(sections, "MemCtrl") != 18:
        raise SystemExit("expected eighteen MemCtrl instances")
    if _count_type(sections, "DRAMInterface") != 18:
        raise SystemExit("expected eighteen DRAMInterface instances")
    if _count_type(sections, "RangeAddrMapper") != 0:
        raise SystemExit("node 0 ranges should use direct controllers under KVM")
    if _count_type(sections, "CxlMemLink") != 2:
        raise SystemExit("expected two slow CxlMemLink instances")
    if _count_type(sections, "X86ACPISrat") != 1:
        raise SystemExit("expected one SRAT table")
    if _count_type(sections, "X86ACPISlit") != 1:
        raise SystemExit("expected one SLIT table")

    text = config_ini.read_text()
    for needle in (
        "switched_out=false",
        "switched_out=true",
        "flit_size_bytes=256",
        "m2s_latency=80000",
        "s2m_latency=80000",
    ):
        if needle not in text:
            raise SystemExit(f"missing expected config entry: {needle}")
    if "static_frontend_latency=40000" in text:
        raise SystemExit("slow controller frontend latency should not be inflated")
    if "static_backend_latency=40000" in text:
        raise SystemExit("slow controller backend latency should not be inflated")
    if text.count("static_frontend_latency=10000") < 18:
        raise SystemExit("expected all eighteen MemCtrls to use 10ns frontend latency")
    if text.count("static_backend_latency=10000") < 18:
        raise SystemExit("expected all eighteen MemCtrls to use 10ns backend latency")

    print("Step 10 KVM-to-Timing config validation passed")
    print("- FS script uses LargeMemoryX86Board")
    print("- two KVM start cores are present")
    print("- two Timing switch cores are present and initially switched out")
    print("- eighteen DDR5-derived DRAM interfaces are present")
    print("- node 0 low/high ranges use direct 8-channel controllers for KVM")
    print("- slow memory is routed through CxlMemLink")
    print("- SRAT/SLIT NUMA tables are present")
    print("- controller latency is uniform; CXL delay is in CxlMemLink")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
