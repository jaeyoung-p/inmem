#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Validate Step 12 DMA-based bandwidth/latency config packaging."""

import argparse
import json
import re
from pathlib import Path


def latency_text_to_ticks(text: str) -> int:
    match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*(ps|ns|us|ms|s)\s*", text)
    if match is None:
        raise SystemExit(f"unsupported latency text for checker: {text}")

    value = float(match.group(1))
    unit = match.group(2)
    ticks_per_unit = {
        "ps": 1,
        "ns": 1_000,
        "us": 1_000_000,
        "ms": 1_000_000_000,
        "s": 1_000_000_000_000,
    }[unit]
    ticks = value * ticks_per_unit
    if not ticks.is_integer():
        raise SystemExit(f"latency does not map to an integer tick count: {text}")
    return int(ticks)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    parser.add_argument(
        "--expected-node",
        type=int,
        choices=[0, 1],
        required=True,
        help="Expected latency/injection NUMA node.",
    )
    parser.add_argument(
        "--min-dma-injectors",
        type=int,
        default=0,
        help="Minimum expected PyTrafficGen injectors. Default: 0.",
    )
    parser.add_argument(
        "--expected-aes-latency",
        default=None,
        help=(
            "Optional expected MemCtrl aes_latency value in config ticks, "
            "for example 40000 for 40ns."
        ),
    )
    parser.add_argument(
        "--expected-aes-latency-text",
        default=None,
        help=(
            "Optional expected MemCtrl aes_latency as text, for example 40ns. "
            "This also checks point metadata."
        ),
    )
    args = parser.parse_args()

    config_ini = args.outdir / "config.ini"
    if not config_ini.is_file():
        raise SystemExit(f"missing {config_ini}")

    metadata_path = args.outdir / "step12_point.json"
    if not metadata_path.is_file():
        raise SystemExit(f"missing {metadata_path}")
    metadata = json.loads(metadata_path.read_text())
    if int(metadata["node"]) != args.expected_node:
        raise SystemExit(
            f"point metadata node mismatch: expected {args.expected_node}, "
            f"found {metadata['node']}"
        )

    config_script = Path(__file__).with_name("x86_two_tier_dma_bwlat.py")
    script_text = config_script.read_text()
    for needle in (
        "LargeMemoryX86Board",
        "MESITwoLevelCacheHierarchy",
        "CoherenceProtocol.MESI_TWO_LEVEL",
        "PyTrafficGen",
        "STEP12_NODE",
        "STEP12_LATENCY_MIB",
        "STEP12_LATENCY_ITERS",
        "STEP12_CPU_MHZ",
        "--aes-latency",
    ):
        if needle not in script_text:
            raise SystemExit(f"missing script evidence: {needle}")

    readfiles = sorted(args.outdir.glob("readfile_*"))
    if len(readfiles) != 1:
        raise SystemExit(f"expected one readfile artifact, found {len(readfiles)}")

    config = config_ini.read_text()
    readfile = readfiles[0].read_text()

    if config.count("type=MemCtrl") != 36:
        raise SystemExit("expected thirty-six MemCtrl instances")
    if config.count("type=DRAMInterface") != 36:
        raise SystemExit("expected thirty-six DRAMInterface instances")
    if config.count("type=CxlMemLink") != 1:
        raise SystemExit("expected one shared CxlMemLink instance")
    if config.count("type=X86KvmCPU") < 1:
        raise SystemExit("expected one KVM start CPU")
    if config.count("type=BaseTimingSimpleCPU") < 1:
        raise SystemExit("expected one switched TimingSimpleCPU")
    if config.count("type=PyTrafficGen") < args.min_dma_injectors:
        raise SystemExit(
            f"expected at least {args.min_dma_injectors} PyTrafficGen injectors"
        )

    for needle in (
        "flit_size_bytes=256",
        "m2s_latency=60000",
        "s2m_latency=60000",
        "type=X86ACPISrat",
        "type=X86ACPISlit",
    ):
        if needle not in config:
            raise SystemExit(f"missing config evidence: {needle}")

    expected_aes_latency = args.expected_aes_latency
    if args.expected_aes_latency_text is not None:
        expected_aes_latency = str(
            latency_text_to_ticks(args.expected_aes_latency_text)
        )
        if metadata.get("aes_latency") != args.expected_aes_latency_text:
            raise SystemExit(
                "point metadata aes_latency mismatch: expected "
                f"{args.expected_aes_latency_text}, found "
                f"{metadata.get('aes_latency')}"
            )

    if expected_aes_latency is not None:
        expected = f"aes_latency={expected_aes_latency}"
        if config.count(expected) != 36:
            raise SystemExit(
                f"expected thirty-six MemCtrl entries with {expected}"
            )
        if metadata.get("aes_latency") is None:
            raise SystemExit("missing aes_latency in point metadata")

    for needle in (
        "numa_latency.c",
        "guest_dma_bwlat.sh",
        "LAT_RESULT",
        "STEP12_NODE",
        "STEP12_LATENCY_MIB",
        "STEP12_LATENCY_ITERS",
        "STEP12_CPU_MHZ",
        "gem5-bridge hypercall 4",
        'numactl --cpunodebind=0 --membind="${STEP12_NODE}"',
        "=== STEP12 COMPLETE ===",
    ):
        if needle not in readfile:
            raise SystemExit(f"missing readfile evidence: {needle}")

    print("Step 12 DMA bandwidth/latency packaging validation passed")
    print("- FS script uses LargeMemoryX86Board")
    print("- FS script uses the Ruby MESI_Two_Level cache hierarchy")
    print("- config keeps one shared CxlMemLink in front of node1")
    print(f"- point metadata targets NUMA node {args.expected_node}")
    print(f"- config contains at least {args.min_dma_injectors} PyTrafficGen injector(s)")
    if expected_aes_latency is not None:
        print(f"- all MemCtrl instances use aes_latency={expected_aes_latency}")
    print("- readfile embeds the guest latency benchmark and ROI switch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
