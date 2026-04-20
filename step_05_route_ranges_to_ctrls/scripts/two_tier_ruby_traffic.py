#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Synthetic Ruby traffic run for TwoTierMemory route validation."""

import argparse

from gem5.coherence_protocol import CoherenceProtocol
from gem5.components.boards.test_board import TestBoard
from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)
from gem5.components.memory import TwoTierMemory
from gem5.components.processors.linear_generator import LinearGenerator
from gem5.simulate.simulator import Simulator
from gem5.utils.override import overrides
from gem5.utils.requires import requires


NODE0_HIGH_START = 0x100000000
NODE0_HIGH_END = 65 * 1024 * 1024 * 1024
SLOW_START = 0x1040000000
SLOW_END = 0x2040000000


class TwoTierTrafficBoard(TestBoard):
    """TestBoard variant that preserves TwoTierMemory's fixed ranges."""

    @overrides(TestBoard)
    def _setup_memory_ranges(self) -> None:
        memory = self.get_memory()
        if not hasattr(memory, "get_default_memory_ranges"):
            super()._setup_memory_ranges()
            return

        self.mem_ranges = memory.get_default_memory_ranges()
        memory.set_memory_range(self.mem_ranges)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tier",
        choices=("node0", "fast", "slow"),
        required=True,
        help="Which TwoTierMemory node range to drive.",
    )
    parser.add_argument(
        "--bytes",
        type=int,
        default=64 * 1024,
        help="Amount of linear read traffic to issue.",
    )
    parser.add_argument(
        "--read-percent",
        type=int,
        default=100,
        help="Read percentage for the linear generator; use 0 for write traffic.",
    )
    parser.add_argument(
        "--cxl-flit-size",
        type=int,
        default=256,
        help="CXL.mem flit size in bytes for the slow tier link model.",
    )
    parser.add_argument(
        "--cxl-link-bandwidth",
        default="64GiB/s",
        help="Per-direction CXL.mem link bandwidth.",
    )
    parser.add_argument(
        "--cxl-base-latency",
        default="80ns",
        help="Per-direction CXL.mem base link latency.",
    )
    parser.add_argument(
        "--cxl-queue-depth-flits",
        type=int,
        default=256,
        help="CXL.mem FIFO depth per direction in flits.",
    )
    args = parser.parse_args()

    requires(coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL)

    if args.tier in ("node0", "fast"):
        start = NODE0_HIGH_START
        end = min(NODE0_HIGH_END, start + args.bytes)
        tier_name = "node0"
    else:
        start = SLOW_START
        end = min(SLOW_END, start + args.bytes)
        tier_name = "slow"

    generator = LinearGenerator(
        num_cores=1,
        duration="10us",
        rate="8GiB/s",
        block_size=64,
        min_addr=start,
        max_addr=end,
        rd_perc=args.read_percent,
        data_limit=args.bytes,
    )

    cache_hierarchy = MESITwoLevelCacheHierarchy(
        l1d_size="32KiB",
        l1d_assoc=8,
        l1i_size="32KiB",
        l1i_assoc=8,
        l2_size="512KiB",
        l2_assoc=16,
        num_l2_banks=1,
    )

    board = TwoTierTrafficBoard(
        clk_freq="3GHz",
        generator=generator,
        memory=TwoTierMemory(
            cxl_flit_size_bytes=args.cxl_flit_size,
            cxl_link_bandwidth=args.cxl_link_bandwidth,
            cxl_base_latency=args.cxl_base_latency,
            cxl_queue_depth_flits=args.cxl_queue_depth_flits,
        ),
        cache_hierarchy=cache_hierarchy,
    )

    print(
        f"Driving {tier_name} tier with {args.bytes} bytes: "
        f"[0x{start:x}, 0x{end:x})"
    )

    simulator = Simulator(board=board)
    simulator.run()


if __name__ in ("__m5_main__", "__main__"):
    main()
