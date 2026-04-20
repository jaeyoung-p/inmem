#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Check that node 1 CXL delay is not using fixed base latency by default."""

import argparse
import math
import re
from pathlib import Path


STAT_RE = re.compile(r"^(\S+)\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+|nan|inf|-inf))\b")


def parse_stats(path: Path) -> dict[str, float]:
    stats: dict[str, float] = {}
    if not path.is_file():
        return stats

    for line in path.read_text(errors="replace").splitlines():
        match = STAT_RE.match(line)
        if not match:
            continue
        value = float(match.group(2))
        if math.isfinite(value):
            stats[match.group(1)] = value
    return stats


def sum_suffix(stats: dict[str, float], suffix: str) -> float:
    return sum(value for name, value in stats.items() if name.endswith(suffix))


def config_values(config: str, param: str) -> list[int]:
    return [int(value) for value in re.findall(rf"^{param}=(\d+)$", config, re.M)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    parser.add_argument(
        "--allow-fixed-base",
        action="store_true",
        help="Permit non-zero m2s/s2m fixed latency for explicit calibration runs.",
    )
    args = parser.parse_args()

    config_ini = args.outdir / "config.ini"
    if not config_ini.is_file():
        raise SystemExit(f"missing {config_ini}")

    config = config_ini.read_text(errors="replace")
    m2s_latencies = config_values(config, "m2s_latency")
    s2m_latencies = config_values(config, "s2m_latency")
    frontend_latencies = config_values(config, "static_frontend_latency")
    backend_latencies = config_values(config, "static_backend_latency")

    if len(m2s_latencies) != 2 or len(s2m_latencies) != 2:
        raise SystemExit("expected exactly two CxlMemLink latency entries")
    if not args.allow_fixed_base and (any(m2s_latencies) or any(s2m_latencies)):
        raise SystemExit(
            "default node 1 model must not include fixed CXL base latency: "
            f"m2s={m2s_latencies}, s2m={s2m_latencies}"
        )
    if len(frontend_latencies) < 18 or set(frontend_latencies) != {10000}:
        raise SystemExit(
            "all node 0 and node 1 MemCtrls should use 10ns frontend latency"
        )
    if len(backend_latencies) < 18 or set(backend_latencies) != {10000}:
        raise SystemExit(
            "all node 0 and node 1 MemCtrls should use 10ns backend latency"
        )

    stats = parse_stats(args.outdir / "stats.txt")
    m2s_base = sum_suffix(stats, ".m2sBaseLatencyTicks")
    s2m_base = sum_suffix(stats, ".s2mBaseLatencyTicks")
    m2s_queue = sum_suffix(stats, ".m2sQueueWaitTicks")
    s2m_queue = sum_suffix(stats, ".s2mQueueWaitTicks")
    m2s_ser = sum_suffix(stats, ".m2sSerializationTicks")
    s2m_ser = sum_suffix(stats, ".s2mSerializationTicks")

    if stats and not args.allow_fixed_base and (m2s_base != 0 or s2m_base != 0):
        raise SystemExit(
            "stats show fixed CXL base latency despite zero-base config: "
            f"m2sBaseLatencyTicks={m2s_base}, s2mBaseLatencyTicks={s2m_base}"
        )

    print("CXL node 1 latency model check passed")
    print(f"- CXL config fixed base latency ticks: m2s={m2s_latencies}, s2m={s2m_latencies}")
    print("- all 18 MemCtrls use 10ns static frontend/backend latency")
    if stats:
        print(
            "- CXL stats ticks: "
            f"queue={m2s_queue + s2m_queue:.0f}, "
            f"serialization={m2s_ser + s2m_ser:.0f}, "
            f"fixed_base={m2s_base + s2m_base:.0f}"
        )
    else:
        print("- stats.txt not present; config-only check completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
