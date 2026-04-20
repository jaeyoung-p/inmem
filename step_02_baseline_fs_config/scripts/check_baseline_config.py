#!/usr/bin/env python3
"""Check expected single-memory baseline objects in a gem5 config.ini."""

from __future__ import annotations

import argparse
import configparser
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_ini",
        type=Path,
        help="Path to m5out/config.ini from the Step 2 baseline run.",
    )
    args = parser.parse_args()

    if not args.config_ini.is_file():
        print(f"missing config.ini: {args.config_ini}", file=sys.stderr)
        return 1

    cfg = configparser.ConfigParser(strict=False, interpolation=None)
    cfg.optionxform = str
    cfg.read(args.config_ini)

    failures = []
    config_script = Path(__file__).with_name("x86_baseline_kvm_timing.py")
    if config_script.is_file():
        script_text = config_script.read_text()
        if "from gem5.components.boards.x86_board import X86Board" not in script_text:
            failures.append("baseline script should import stock X86Board")
        if "LargeMemoryX86Board" in script_text:
            failures.append("baseline script should not use LargeMemoryX86Board")

    board = cfg["board"] if cfg.has_section("board") else {}
    if board.get("mem_ranges") != "0:3221225472 3221225472:3222274048":
        failures.append(
            "board.mem_ranges should be one 3GiB RAM range plus the x86 I/O "
            "bridge range"
        )
    if board.get("memories") != "board.memory.mem_ctrl.dram":
        failures.append("board.memories should reference the single DRAM interface")

    if not cfg.has_section("board.memory.mem_ctrl"):
        failures.append("missing board.memory.mem_ctrl")
    elif cfg["board.memory.mem_ctrl"].get("type") != "MemCtrl":
        failures.append("board.memory.mem_ctrl should be type MemCtrl")

    if not cfg.has_section("board.cache_hierarchy.ruby_system.directory_controllers"):
        failures.append("missing Ruby directory controller")
    else:
        directory = cfg["board.cache_hierarchy.ruby_system.directory_controllers"]
        if directory.get("addr_ranges") != "0:3221225472":
            failures.append("Ruby directory should own only the 3GiB RAM range")
        if directory.get("memory_out_port") != "board.memory.mem_ctrl.port":
            failures.append("Ruby directory should connect to the single MemCtrl")

    if failures:
        print("baseline config validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("baseline config validation passed")
    print("- baseline script uses stock X86Board")
    print("- one 3GiB ordinary RAM range")
    print("- one MemCtrl")
    print("- one Ruby directory mapped to that MemCtrl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
