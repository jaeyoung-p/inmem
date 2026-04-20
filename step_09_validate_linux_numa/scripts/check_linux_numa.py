#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Validate Linux-visible NUMA evidence captured in the Step 9 serial log."""

import argparse
import re
from pathlib import Path


def _require(text: str, needle: str, description: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {description}: {needle}")


def _require_regex(text: str, pattern: str, description: str) -> re.Match[str]:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise SystemExit(f"missing {description}: {pattern}")
    return match


def _node_mem_total(text: str, node: int) -> int:
    match = _require_regex(
        text,
        rf"Node {node} MemTotal:\s+(\d+) kB",
        f"node {node} memory total",
    )
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    args = parser.parse_args()

    serial = args.outdir / "board.pc.com_1.device"
    if not serial.is_file():
        raise SystemExit(f"missing {serial}")

    text = serial.read_text(errors="replace")

    for marker in (
        "=== STEP9 DMESG NUMA ===",
        "=== STEP9 DMESG SRAT ===",
        "=== STEP9 DMESG SLIT ===",
        "=== STEP9 JOURNAL NUMA ===",
        "=== STEP9 JOURNAL SRAT ===",
        "=== STEP9 JOURNAL SLIT ===",
        "=== STEP9 NUMACTL HARDWARE ===",
        "=== STEP9 LSCPU ===",
        "=== STEP9 NODE ONLINE ===",
        "=== STEP9 NODE DETAILS ===",
        "=== STEP9 NUMASTAT ===",
        "=== STEP9 COMPLETE ===",
    ):
        _require(text, marker, f"guest command marker {marker}")

    for needle, description in (
        ("ACPI: SRAT", "kernel SRAT table discovery"),
        ("ACPI: SLIT", "kernel SLIT table discovery"),
        ("ACPI: Reserving SRAT table memory", "kernel SRAT reservation"),
        ("ACPI: Reserving SLIT table memory", "kernel SLIT reservation"),
        ("SRAT: PXM 0 -> APIC 0x00 -> Node 0", "CPU 0 SRAT affinity"),
        ("SRAT: PXM 0 -> APIC 0x01 -> Node 0", "CPU 1 SRAT affinity"),
        (
            "ACPI: SRAT: Node 0 PXM 0 [mem 0x00000000-0x0009fbff]",
            "conventional low RAM node 0 affinity",
        ),
        (
            "ACPI: SRAT: Node 0 PXM 0 [mem 0x00100000-0xbfffffff]",
            "low fast RAM node 0 affinity",
        ),
        (
            "ACPI: SRAT: Node 0 PXM 0 [mem 0x100000000-0x103fffffff]",
            "high fast RAM node 0 affinity",
        ),
        (
            "ACPI: SRAT: Node 1 PXM 1 [mem 0x1040000000-0x203fffffff]",
            "slow RAM node 1 affinity",
        ),
        ("NUMA: Initialized distance table, cnt=2", "SLIT distance parsing"),
        ("NUMA node(s):           2", "lscpu NUMA node count"),
        ("NUMA node0 CPU(s):      0,1", "lscpu node 0 CPU mapping"),
        ("NUMA node1 CPU(s):      ", "lscpu memory-only node 1"),
        ("=== STEP9 COMPLETE ===", "script completion"),
    ):
        _require(text, needle, description)

    _require_regex(
        text,
        r"=== STEP9 NODE ONLINE ===\n\+ cat /sys/devices/system/node/online\n0-1",
        "sysfs online node list 0-1",
    )
    _require_regex(
        text,
        r"--- /sys/devices/system/node/node0 ---\n\+ cat .*/node0/cpulist\n0-1",
        "sysfs node 0 CPU list",
    )
    _require_regex(
        text,
        r"--- /sys/devices/system/node/node1 ---\n\+ cat .*/node1/cpulist\n\s*\+ grep",
        "sysfs node 1 empty CPU list",
    )

    node0_kb = _node_mem_total(text, 0)
    node1_kb = _node_mem_total(text, 1)
    if not (60_000_000 <= node0_kb <= 68_000_000):
        raise SystemExit(f"unexpected node 0 memory size: {node0_kb} kB")
    if not (60_000_000 <= node1_kb <= 68_000_000):
        raise SystemExit(f"unexpected node 1 memory size: {node1_kb} kB")

    dmesg_blocked = "dmesg: read kernel buffer failed" in text
    dmesg_restrict = _require_regex(
        text,
        r"=== STEP9 DMESG POLICY ===\n\+ cat /proc/sys/kernel/dmesg_restrict\n([01])",
        "dmesg policy",
    ).group(1)

    print("Step 9 Linux NUMA validation passed")
    print("- Kernel boot log and journal show SRAT and SLIT parsing")
    print("- Linux reports online NUMA nodes 0-1")
    print("- lscpu reports CPUs 0-1 on node 0 and no CPUs on node 1")
    print(f"- node0 MemTotal is {node0_kb} kB")
    print(f"- node1 MemTotal is {node1_kb} kB")
    if dmesg_blocked:
        print(
            "- dmesg command ran but is blocked by guest dmesg_restrict="
            f"{dmesg_restrict}; journalctl/serial log provide kernel evidence"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
