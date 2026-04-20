#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Validate LargeMemoryX86Board ordinary 64GiB split-range smoke config."""

import argparse
import configparser
from pathlib import Path


LOW_RANGE = "0:3221225472"
HIGH_RANGE = "4294967296:69793218560"
IO_RANGE = "3221225472:3222274048"
EXPECTED_E820 = [
    (0x0, 0x9FC00, 1),
    (0x9FC00, 0x60400, 2),
    (0x100000, 0xBFF00000, 1),
    (0xC0000000, 0x3FFF0000, 2),
    (0xFFFF0000, 0x10000, 2),
    (0x100000000, 0xF40000000, 1),
]


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


def _count_type(cfg: configparser.ConfigParser, simobject_type: str) -> int:
    return sum(
        1 for section in cfg.sections() if cfg[section].get("type") == simobject_type
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("config_ini", type=Path)
    args = parser.parse_args()

    cfg = configparser.ConfigParser(strict=False, interpolation=None)
    cfg.optionxform = str
    if not args.config_ini.is_file():
        raise SystemExit(f"missing {args.config_ini}")
    cfg.read(args.config_ini)

    board = cfg["board"] if cfg.has_section("board") else {}
    expected_ranges = f"{LOW_RANGE} {HIGH_RANGE} {IO_RANGE}"
    if board.get("mem_ranges") != expected_ranges:
        raise SystemExit(
            f"unexpected board.mem_ranges: {board.get('mem_ranges')}"
        )
    if _count_type(cfg, "MemCtrl") != 4:
        raise SystemExit("expected two ranges times two channels = four MemCtrls")
    if _parse_e820_entries(cfg) != EXPECTED_E820:
        raise SystemExit("unexpected E820 entries for ordinary 64GiB split RAM")

    print("LargeMemoryX86Board ordinary-RAM smoke validation passed")
    print("- 64GiB RAM is split below and above the x86 PCI hole")
    print("- controller count is two ranges times two channels")
    print("- E820 reserves the 3-4GiB PCI hole")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
