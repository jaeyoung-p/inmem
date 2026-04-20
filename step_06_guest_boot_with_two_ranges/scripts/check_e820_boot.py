#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Validate that the two-tier RAM ranges are exposed through x86 E820."""

import argparse
import re
from pathlib import Path


EXPECTED_E820 = [
    (0x0, 0x9FC00, 1),
    (0x9FC00, 0x60400, 2),
    (0x100000, 0xBFF00000, 1),
    (0xC0000000, 0x3FFF0000, 2),
    (0xFFFF0000, 0x10000, 2),
    (0x100000000, 0xF40000000, 1),
    (0x1040000000, 0x1000000000, 1),
]

EXPECTED_SERIAL_LINES = [
    "BIOS-e820: [mem 0x0000000000100000-0x00000000bfffffff] usable",
    "BIOS-e820: [mem 0x0000000100000000-0x000000103fffffff] usable",
    "BIOS-e820: [mem 0x0000001040000000-0x000000203fffffff] usable",
]


def _parse_e820_entries(config_ini: Path) -> list[tuple[int, int, int]]:
    entries: dict[int, dict[str, int]] = {}
    current = None

    section_re = re.compile(
        r"^\[board\.workload\.e820_table\.entries(\d+)\]$"
    )
    for raw_line in config_ini.read_text().splitlines():
        line = raw_line.strip()
        match = section_re.match(line)
        if match:
            current = int(match.group(1))
            entries[current] = {}
            continue

        if current is None or "=" not in line:
            continue

        key, value = line.split("=", 1)
        if key in {"addr", "size", "range_type"}:
            entries[current][key] = int(value, 0)

    parsed = []
    for index in sorted(entries):
        entry = entries[index]
        parsed.append((entry["addr"], entry["size"], entry["range_type"]))
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    args = parser.parse_args()

    config_ini = args.outdir / "config.ini"
    serial = args.outdir / "board.pc.com_1.device"

    if not config_ini.is_file():
        raise SystemExit(f"missing {config_ini}")
    if not serial.is_file():
        raise SystemExit(f"missing {serial}")

    config_script = Path(__file__).with_name("x86_two_tier_e820_boot.py")
    if config_script.is_file():
        script_text = config_script.read_text()
        if "LargeMemoryX86Board" not in script_text:
            raise SystemExit("Step 6 FS script should instantiate LargeMemoryX86Board")
        if "from gem5.components.boards.x86_board import X86Board" in script_text:
            raise SystemExit("Step 6 FS script should not import stock X86Board")

    actual_e820 = _parse_e820_entries(config_ini)
    if actual_e820 != EXPECTED_E820:
        raise SystemExit(
            "unexpected E820 entries\n"
            f"expected: {EXPECTED_E820}\n"
            f"actual:   {actual_e820}"
        )

    serial_text = serial.read_text(errors="replace")
    missing = [
        expected
        for expected in EXPECTED_SERIAL_LINES
        if expected not in serial_text
    ]
    if missing:
        raise SystemExit(
            "serial log is missing expected evidence:\n"
            + "\n".join(f"- {line}" for line in missing)
        )

    print("Step 6 E820 boot validation passed")
    print("- FS script uses LargeMemoryX86Board")
    print("- config.ini exposes node 0 RAM around the x86 PCI hole")
    print("- config.ini exposes node 1 RAM at 65GiB-129GiB")
    print("- Linux boot log reports all usable ranges as BIOS-e820 usable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
