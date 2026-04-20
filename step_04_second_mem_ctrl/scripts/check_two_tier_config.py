#!/usr/bin/env python3
"""Validate Step 4 two-tier memory objects in config.ini."""

from __future__ import annotations

import argparse
import configparser
import sys
from pathlib import Path


NODE0_LOW_RANGE = "0:3221225472"
NODE0_HIGH_RANGE = "4294967296:69793218560"
SLOW_RANGE = "69793218560:138512695296"
IO_RANGE = "3221225472:3222274048"
NODE0_CHANNELS = 8
SLOW_CHANNELS = 2
EXPECTED_E820 = [
    (0x0, 0x9FC00, 1),
    (0x9FC00, 0x60400, 2),
    (0x100000, 0xBFF00000, 1),
    (0xC0000000, 0x3FFF0000, 2),
    (0xFFFF0000, 0x10000, 2),
    (0x100000000, 0xF40000000, 1),
    (0x1040000000, 0x1000000000, 1),
]


def node0_channel_range(addr_range: str, channel: int) -> str:
    return f"{addr_range}:{channel}:64:128:256"


def slow_channel_range(addr_range: str, channel: int) -> str:
    return f"{addr_range}:{channel}:64"


def directory_path(index: int) -> str:
    return f"board.cache_hierarchy.ruby_system.directory_controllers{index:02d}"

EXPECTED_CHANNELS = [
    (
        "node0",
        f"board.memory.node0_low_ctrls{channel}",
        node0_channel_range(NODE0_LOW_RANGE, channel),
        "10000",
    )
    for channel in range(NODE0_CHANNELS)
] + [
    (
        "node0",
        f"board.memory.node0_high_ctrls{channel}",
        node0_channel_range(NODE0_HIGH_RANGE, channel),
        "10000",
    )
    for channel in range(NODE0_CHANNELS)
] + [
    (
        "slow",
        f"board.memory.slow_ctrls{channel}",
        slow_channel_range(SLOW_RANGE, channel),
        "10000",
    )
    for channel in range(SLOW_CHANNELS)
]
EXPECTED_CXL_LINKS = [
    (
        f"board.memory.slow_cxl_links{channel}",
        slow_channel_range(SLOW_RANGE, channel),
        f"board.memory.slow_ctrls{channel}",
    )
    for channel in range(SLOW_CHANNELS)
]
EXPECTED_DIRECTORIES = [
    (
        node0_channel_range(NODE0_LOW_RANGE, channel),
        directory_path(channel),
        f"board.memory.node0_low_ctrls{channel}.port",
    )
    for channel in range(NODE0_CHANNELS)
] + [
    (
        node0_channel_range(NODE0_HIGH_RANGE, channel),
        directory_path(NODE0_CHANNELS + channel),
        f"board.memory.node0_high_ctrls{channel}.port",
    )
    for channel in range(NODE0_CHANNELS)
] + [
    (
        slow_channel_range(SLOW_RANGE, channel),
        directory_path(2 * NODE0_CHANNELS + channel),
        f"board.memory.slow_cxl_links{channel}.cpu_side_port",
    )
    for channel in range(SLOW_CHANNELS)
]


def section(cfg: configparser.ConfigParser, name: str):
    if not cfg.has_section(name):
        raise KeyError(name)
    return cfg[name]


def _parse_e820_entries(
    cfg: configparser.ConfigParser,
) -> list[tuple[int, int, int]]:
    entries = []
    for name in cfg.sections():
        if not name.startswith("board.workload.e820_table.entries"):
            continue
        entry = cfg[name]
        entries.append(
            (
                int(entry["addr"]),
                int(entry["size"]),
                int(entry["range_type"]),
            )
        )
    return sorted(entries)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("config_ini", type=Path)
    args = parser.parse_args()

    cfg = configparser.ConfigParser(strict=False, interpolation=None)
    cfg.optionxform = str
    if not args.config_ini.is_file():
        print(f"missing config.ini: {args.config_ini}", file=sys.stderr)
        return 1
    cfg.read(args.config_ini)

    failures = []
    config_script = Path(__file__).with_name("x86_two_tier_kvm_timing.py")
    if config_script.is_file():
        script_text = config_script.read_text()
        if "LargeMemoryX86Board" not in script_text:
            failures.append(
                "two-tier FS script should instantiate LargeMemoryX86Board"
            )
        if "from gem5.components.boards.x86_board import X86Board" in script_text:
            failures.append("two-tier FS script should not import stock X86Board")

    try:
        board = section(cfg, "board")
        expected_board_ranges = (
            f"{NODE0_LOW_RANGE} {NODE0_HIGH_RANGE} {SLOW_RANGE} {IO_RANGE}"
        )
        if board.get("mem_ranges") != expected_board_ranges:
            failures.append(
                f"board.mem_ranges should be '{expected_board_ranges}', got "
                f"'{board.get('mem_ranges')}'"
            )
        expected_memories = {
            f"{ctrl}.dram" for _, ctrl, _, _ in EXPECTED_CHANNELS
        }
        actual_memories = set(board.get("memories", "").split())
        if actual_memories != expected_memories:
            failures.append(
                "board.memories should contain the eighteen DDR5 channel "
                f"interfaces, got {sorted(actual_memories)}"
            )
    except KeyError as err:
        failures.append(f"missing section {err}")

    checks = {}
    for _, ctrl, dram_range, latency in EXPECTED_CHANNELS:
        checks[ctrl] = {
            "type": "MemCtrl",
            "dram": f"{ctrl}.dram",
            "static_frontend_latency": latency,
            "static_backend_latency": latency,
        }
        checks[f"{ctrl}.dram"] = {
            "type": "DRAMInterface",
            "range": dram_range,
            "tCK": "312",
            "burst_length": "16",
            "device_bus_width": "8",
            "device_size": "4294967296",
            "devices_per_rank": "4",
            "ranks_per_channel": "2",
            "bank_groups_per_rank": "8",
        }

    for link, addr_range, ctrl in EXPECTED_CXL_LINKS:
        checks[link] = {
            "type": "CxlMemLink",
            "ranges": addr_range,
            "flit_size_bytes": "256",
            "m2s_latency": "80000",
            "s2m_latency": "80000",
            "m2s_queue_depth_flits": "256",
            "s2m_queue_depth_flits": "256",
            "mem_side_port": f"{ctrl}.port",
        }
        checks[ctrl]["port"] = f"{link}.mem_side_port"

    for name, expected in checks.items():
        try:
            sec = section(cfg, name)
        except KeyError:
            failures.append(f"missing section {name}")
            continue
        for key, value in expected.items():
            if sec.get(key) != value:
                failures.append(
                    f"{name}.{key} should be {value}, got {sec.get(key)}"
                )

    dir_sections = [
        name
        for name in cfg.sections()
        if name.startswith(
            "board.cache_hierarchy.ruby_system.directory_controllers"
        )
        and cfg[name].get("type") == "MESI_Two_Level_Directory_Controller"
    ]
    if len(dir_sections) != len(EXPECTED_DIRECTORIES):
        failures.append(
            f"expected {len(EXPECTED_DIRECTORIES)} Ruby directories, "
            f"found {len(dir_sections)}"
        )
    else:
        by_range = {cfg[name].get("addr_ranges"): name for name in dir_sections}
        for addr_ranges, directory, port in EXPECTED_DIRECTORIES:
            if addr_ranges not in by_range:
                failures.append(f"missing Ruby directory for {addr_ranges}")
                continue
            actual_directory = by_range[addr_ranges]
            if actual_directory != directory:
                failures.append(
                    f"{addr_ranges} should be owned by {directory}, got "
                    f"{actual_directory}"
                )
            elif cfg[actual_directory].get("memory_out_port") != port:
                failures.append(
                    f"{directory} for {addr_ranges} is not connected to {port}"
                )

    for key in ("tCL", "tRCD", "tRP", "tBURST", "banks_per_rank"):
        values = {}
        try:
            for _, ctrl, _, _ in EXPECTED_CHANNELS:
                values[f"{ctrl}.dram"] = section(cfg, f"{ctrl}.dram").get(key)
        except KeyError as err:
            failures.append(f"missing section {err}")
            continue
        if len(set(values.values())) != 1:
            failures.append(
                f"DRAM timing parameter {key} differs across channels: {values}"
            )

    actual_e820 = _parse_e820_entries(cfg)
    if actual_e820 != EXPECTED_E820:
        failures.append(
            "E820 should expose all real two-tier RAM ranges and omit the "
            f"3-4GiB hole; expected {EXPECTED_E820}, got {actual_e820}"
        )

    if failures:
        print("two-tier config validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("two-tier config validation passed")
    print("- two-tier FS script uses LargeMemoryX86Board")
    print("- node 0 models one 8-channel DDR5 memory system split by PCI hole")
    print("- node 1 exposes one 64GiB slow RAM range")
    print("- node 0 low/high ranges use identical 8-way 64B interleaving")
    print("- every guest-visible RAM range has direct KVM-safe backing memory")
    print("- node 1 traffic crosses two CxlMemLink flit queues")
    print("- E820 exposes Linux-safe low RAM, high node 0 RAM, and CXL RAM")
    print("- controller latency is uniform; CXL delay is in CxlMemLink")
    print("- eighteen Ruby directories exist, one per exposed channel range")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
