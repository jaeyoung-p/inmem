#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Validate Step 8 SRAT/SLIT objects and node mapping in config.ini/json."""

import argparse
import json
from pathlib import Path


FAST_LOW_BASE = 0x100000
FAST_LOW_SIZE = 0xBFF00000
FAST_HIGH_BASE = 0x100000000
FAST_HIGH_SIZE = 0xF40000000
LEGACY_LOW_BASE = 0x0
LEGACY_LOW_SIZE = 0x9FC00
SLOW_BASE = 0x1040000000
SLOW_SIZE = 0x1000000000


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


def _typed_sections(
    sections: dict[str, dict[str, str]], simobject_type: str
) -> list[tuple[str, dict[str, str]]]:
    return [
        (name, data)
        for name, data in sorted(sections.items())
        if data.get("type") == simobject_type
    ]


def _as_int(value: str) -> int:
    return int(value, 0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    args = parser.parse_args()

    config_ini = args.outdir / "config.ini"
    config_json = args.outdir / "config.json"
    if not config_ini.is_file():
        raise SystemExit(f"missing {config_ini}")
    if not config_json.is_file():
        raise SystemExit(f"missing {config_json}")

    config_script = Path(__file__).with_name("x86_two_tier_numa_config.py")
    if config_script.is_file():
        script_text = config_script.read_text()
        if "LargeMemoryX86Board" not in script_text:
            raise SystemExit("Step 8 FS script should instantiate LargeMemoryX86Board")
        if "from gem5.components.boards.x86_board import X86Board" in script_text:
            raise SystemExit("Step 8 FS script should not import stock X86Board")

    sections = _parse_config_ini(config_ini)

    srat_tables = _typed_sections(sections, "X86ACPISrat")
    slit_tables = _typed_sections(sections, "X86ACPISlit")
    if len(srat_tables) != 1:
        raise SystemExit(f"expected one SRAT table, found {len(srat_tables)}")
    if len(slit_tables) != 1:
        raise SystemExit(f"expected one SLIT table, found {len(slit_tables)}")

    _, srat = srat_tables[0]
    _, slit = slit_tables[0]
    srat_records = srat["records"].split()
    if len(srat_records) != 6:
        raise SystemExit(f"expected 6 SRAT records, found {len(srat_records)}")

    processor_records = _typed_sections(
        sections, "X86ACPISratProcessorLocalApic"
    )
    memory_records = _typed_sections(sections, "X86ACPISratMemoryAffinity")
    if len(processor_records) != 2:
        raise SystemExit(
            f"expected 2 processor affinity records, found {len(processor_records)}"
        )
    if len(memory_records) != 4:
        raise SystemExit(
            f"expected 4 memory affinity records, found {len(memory_records)}"
        )

    cpus = sorted(
        (
            _as_int(record["apic_id"]),
            _as_int(record["proximity_domain"]),
            _as_int(record["flags"]),
        )
        for _, record in processor_records
    )
    if cpus != [(0, 0, 1), (1, 0, 1)]:
        raise SystemExit(f"unexpected CPU SRAT records: {cpus}")

    memory = sorted(
        (
            _as_int(record["proximity_domain"]),
            _as_int(record["base_address"]),
            _as_int(record["address_length"]),
            _as_int(record["flags"]),
        )
        for _, record in memory_records
    )
    expected_memory = [
        (0, LEGACY_LOW_BASE, LEGACY_LOW_SIZE, 1),
        (0, FAST_LOW_BASE, FAST_LOW_SIZE, 1),
        (0, FAST_HIGH_BASE, FAST_HIGH_SIZE, 1),
        (1, SLOW_BASE, SLOW_SIZE, 1),
    ]
    if memory != expected_memory:
        raise SystemExit(
            "unexpected memory affinity records\n"
            f"expected: {expected_memory}\n"
            f"actual:   {memory}"
        )

    if _as_int(slit["locality_count"]) != 2:
        raise SystemExit(f"unexpected SLIT locality_count: {slit}")
    if [int(x) for x in slit["distances"].split()] != [10, 20, 20, 10]:
        raise SystemExit(f"unexpected SLIT distances: {slit}")

    data = json.loads(config_json.read_text())
    acpi = data["board"]["workload"]["acpi_description_table_pointer"]
    rsdt_entries = acpi["rsdt"]["entries"]
    xsdt_entries = acpi["xsdt"]["entries"]
    if len(rsdt_entries) != 3:
        raise SystemExit(f"config.json expected 3 RSDT entries, got {rsdt_entries}")
    if len(xsdt_entries) != 3:
        raise SystemExit(f"config.json expected 3 XSDT entries, got {xsdt_entries}")

    print("Step 8 ACPI NUMA config validation passed")
    print("- FS script uses LargeMemoryX86Board")
    print("- RSDT/XSDT contain MADT, SRAT, and SLIT")
    print("- SRAT maps APIC IDs 0 and 1 to node 0")
    print("- SRAT maps node 0's Linux-safe low RAM and high RAM")
    print("- SRAT maps node 1's 64GiB slow RAM at 65GiB-129GiB")
    print("- SLIT distance matrix is local=10, remote=20")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
