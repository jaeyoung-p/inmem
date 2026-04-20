#!/usr/bin/env python3
"""Validate TwoTierMemory Ruby directory routing and traffic separation."""

from __future__ import annotations

import argparse
import configparser
import json
import sys
from pathlib import Path
from typing import Any


NODE0_LOW_RANGE = "0:3221225472"
NODE0_HIGH_RANGE = "4294967296:69793218560"
SLOW_RANGE = "69793218560:138512695296"
NODE0_CHANNELS = 8
SLOW_CHANNELS = 2


def node0_channel_range(addr_range: str, channel: int) -> str:
    return f"{addr_range}:{channel}:64:128:256"


def slow_channel_range(addr_range: str, channel: int) -> str:
    return f"{addr_range}:{channel}:64"


def directory_path(index: int) -> str:
    return f"board.cache_hierarchy.ruby_system.directory_controllers{index:02d}"


EXPECTED_CHANNELS = [
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

NODE0_LOW_DIRS = [
    directory_path(channel)
    for channel in range(NODE0_CHANNELS)
]
NODE0_HIGH_DIRS = [
    directory_path(NODE0_CHANNELS + channel)
    for channel in range(NODE0_CHANNELS)
]
NODE0_DIRS = NODE0_LOW_DIRS + NODE0_HIGH_DIRS
NODE0_LOW_CTRLS = [
    f"board.memory.node0_low_ctrls{channel}"
    for channel in range(NODE0_CHANNELS)
]
NODE0_HIGH_CTRLS = [
    f"board.memory.node0_high_ctrls{channel}"
    for channel in range(NODE0_CHANNELS)
]
NODE0_CTRLS = NODE0_LOW_CTRLS + NODE0_HIGH_CTRLS
SLOW_DIRS = [
    directory_path(2 * NODE0_CHANNELS + channel)
    for channel in range(SLOW_CHANNELS)
]
SLOW_CTRLS = [
    f"board.memory.slow_ctrls{channel}"
    for channel in range(SLOW_CHANNELS)
]
SLOW_CXL_LINKS = [
    f"board.memory.slow_cxl_links{channel}"
    for channel in range(SLOW_CHANNELS)
]


def load_ini(path: Path) -> configparser.ConfigParser:
    cfg = configparser.ConfigParser(strict=False, interpolation=None)
    cfg.optionxform = str
    if not path.is_file():
        raise FileNotFoundError(path)
    cfg.read(path)
    return cfg


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open() as fh:
        return json.load(fh)


def collect_paths(obj: Any, by_path: dict[str, dict[str, Any]]) -> None:
    if isinstance(obj, dict):
        path = obj.get("path")
        if isinstance(path, str):
            by_path[path] = obj
        for value in obj.values():
            collect_paths(value, by_path)
    elif isinstance(obj, list):
        for value in obj:
            collect_paths(value, by_path)


def parse_stats(path: Path) -> dict[str, float]:
    if not path.is_file():
        raise FileNotFoundError(path)

    stats: dict[str, float] = {}
    with path.open() as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "-")):
                continue
            parts = stripped.split()
            if len(parts) < 2:
                continue
            try:
                stats[parts[0]] = float(parts[1])
            except ValueError:
                continue
    return stats


def check_config(outdir: Path, failures: list[str]) -> None:
    cfg = load_ini(outdir / "config.ini")

    dir_sections = [
        section
        for section in cfg.sections()
        if section.startswith(
            "board.cache_hierarchy.ruby_system.directory_controllers"
        )
        and cfg[section].get("type") == "MESI_Two_Level_Directory_Controller"
    ]

    if len(dir_sections) != len(EXPECTED_CHANNELS):
        failures.append(
            f"{outdir}: expected {len(EXPECTED_CHANNELS)} Ruby directories, "
            f"found {len(dir_sections)}"
        )
        return

    owners: dict[str, list[str]] = {}
    for section in dir_sections:
        ranges = cfg[section].get("addr_ranges", "")
        if not ranges:
            failures.append(f"{section}: missing addr_ranges")
            continue
        owners.setdefault(ranges, []).append(section)

    expected = {
        addr_range: (dir_path, peer_port)
        for addr_range, dir_path, peer_port in EXPECTED_CHANNELS
    }
    for addr_range, (dir_path, peer_port) in expected.items():
        dirs = owners.get(addr_range, [])
        if dirs != [dir_path]:
            failures.append(f"{addr_range}: expected owner {dir_path}, got {dirs}")
            continue
        dir_port = cfg[dir_path].get("memory_out_port")
        peer_path, peer_key = peer_port.rsplit(".", 1)
        peer_value = cfg[peer_path].get(peer_key)
        if dir_port != peer_port:
            failures.append(
                f"{dir_path}.memory_out_port should peer with "
                f"{peer_port}, got {dir_port}"
            )
        if peer_value != f"{dir_path}.memory_out_port":
            failures.append(
                f"{peer_port} should peer with "
                f"{dir_path}.memory_out_port, got {peer_value}"
            )

    for channel, link in enumerate(SLOW_CXL_LINKS):
        ctrl = SLOW_CTRLS[channel]
        expected_range = slow_channel_range(SLOW_RANGE, channel)
        if cfg[link].get("ranges") != expected_range:
            failures.append(
                f"{link}.ranges should be {expected_range}, "
                f"got {cfg[link].get('ranges')}"
            )
        if cfg[link].get("flit_size_bytes") != "256":
            failures.append(f"{link}.flit_size_bytes should be 256")
        if cfg[link].get("mem_side_port") != f"{ctrl}.port":
            failures.append(f"{link}.mem_side_port should peer with {ctrl}.port")
        if cfg[ctrl].get("port") != f"{link}.mem_side_port":
            failures.append(f"{ctrl}.port should peer with {link}.mem_side_port")

    config_json = load_json(outdir / "config.json")
    by_path: dict[str, dict[str, Any]] = {}
    collect_paths(config_json, by_path)

    for addr_range, (dir_path, peer_port) in expected.items():
        directory = by_path.get(dir_path)
        if not directory:
            failures.append(f"config.json missing {dir_path}")
            continue
        if directory.get("addr_ranges") != addr_range.split():
            failures.append(
                f"config.json {dir_path}.addr_ranges should be "
                f"{addr_range.split()}, "
                f"got {directory.get('addr_ranges')}"
            )
        peer = directory.get("memory_out_port", {}).get("peer")
        if peer != peer_port:
            failures.append(
                f"config.json {dir_path}.memory_out_port.peer should be "
                f"{peer_port}, got {peer}"
            )


def check_traffic(
    outdir: Path,
    active_dirs: list[str],
    idle_dirs: list[str],
    active_ctrls: list[str],
    idle_ctrls: list[str],
    active_cxl_links: list[str],
    idle_cxl_links: list[str],
    failures: list[str],
) -> None:
    stats = parse_stats(outdir / "stats.txt")

    active_reads_by_ctrl = {
        ctrl: stats.get(f"{ctrl}.readReqs", 0) for ctrl in active_ctrls
    }
    idle_reads = {
        ctrl: stats.get(f"{ctrl}.readReqs", 0) for ctrl in idle_ctrls
    }
    active_dir_reqs = sum(
        stats.get(f"{directory}.requestToMemory.m_msg_count", 0)
        for directory in active_dirs
    )
    idle_dir_reqs = {
        directory: stats.get(f"{directory}.requestToMemory.m_msg_count", 0)
        for directory in idle_dirs
    }
    active_cxl_m2s_by_link = {
        link: stats.get(f"{link}.m2sPackets", 0) for link in active_cxl_links
    }
    idle_cxl_m2s = {
        link: stats.get(f"{link}.m2sPackets", 0) for link in idle_cxl_links
    }

    inactive_reads = {
        ctrl: value for ctrl, value in active_reads_by_ctrl.items() if value <= 0
    }
    if inactive_reads:
        failures.append(
            f"{outdir}: every active controller readReqs should be > 0, "
            f"got {inactive_reads}"
        )
    nonzero_idle_reads = {
        ctrl: value for ctrl, value in idle_reads.items() if value != 0
    }
    if nonzero_idle_reads:
        failures.append(
            f"{outdir}: idle controller readReqs should be 0, "
            f"got {nonzero_idle_reads}"
        )
    if active_dir_reqs <= 0:
        failures.append(
            f"{outdir}: active directory requestToMemory count should sum to > 0"
        )
    nonzero_idle_dirs = {
        directory: value for directory, value in idle_dir_reqs.items() if value != 0
    }
    if nonzero_idle_dirs:
        failures.append(
            f"{outdir}: idle directory requestToMemory counts should be 0, "
            f"got {nonzero_idle_dirs}"
        )
    inactive_cxl = {
        link: value for link, value in active_cxl_m2s_by_link.items() if value <= 0
    }
    if inactive_cxl:
        failures.append(
            f"{outdir}: every active CXL link m2sPackets should be > 0, "
            f"got {inactive_cxl}"
        )
    nonzero_idle_cxl = {
        link: value for link, value in idle_cxl_m2s.items() if value != 0
    }
    if nonzero_idle_cxl:
        failures.append(
            f"{outdir}: idle CXL link m2sPackets should be 0, "
            f"got {nonzero_idle_cxl}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast-outdir", type=Path, required=True)
    parser.add_argument("--slow-outdir", type=Path, required=True)
    args = parser.parse_args()

    failures: list[str] = []

    for outdir in (args.fast_outdir, args.slow_outdir):
        try:
            check_config(outdir, failures)
        except Exception as err:
            failures.append(f"{outdir}: config validation error: {err}")

    try:
        check_traffic(
            args.fast_outdir,
            active_dirs=NODE0_HIGH_DIRS,
            idle_dirs=NODE0_LOW_DIRS + SLOW_DIRS,
            active_ctrls=NODE0_HIGH_CTRLS,
            idle_ctrls=NODE0_LOW_CTRLS + SLOW_CTRLS,
            active_cxl_links=[],
            idle_cxl_links=SLOW_CXL_LINKS,
            failures=failures,
        )
        check_traffic(
            args.slow_outdir,
            active_dirs=SLOW_DIRS,
            idle_dirs=NODE0_DIRS,
            active_ctrls=SLOW_CTRLS,
            idle_ctrls=NODE0_CTRLS,
            active_cxl_links=SLOW_CXL_LINKS,
            idle_cxl_links=[],
            failures=failures,
        )
    except Exception as err:
        failures.append(f"stats validation error: {err}")

    if failures:
        print("route validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("route validation passed")
    print("- config.ini has one Ruby directory per exposed tier channel")
    print("- node 0 low/high ranges use identical 8-way controller paths")
    print("- slow traffic crosses CxlMemLink before slow DDR5 controllers")
    print("- node0-high traffic increments only node0-high controllers/directories")
    print("- slow traffic increments only slow CXL links/controllers/directories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
