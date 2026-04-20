#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Smoke config for LargeMemoryX86Board with ordinary 64GiB RAM."""

import argparse
from pathlib import Path

from gem5.coherence_protocol import CoherenceProtocol
from gem5.components.boards.large_mem_x86 import LargeMemoryX86Board
from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)
from gem5.components.memory import SplitRangeChanneledMemory
from gem5.components.memory.dram_interfaces.ddr5 import DDR5_6400_4x8
from gem5.components.memory.single_channel import DIMM_DDR5_6400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_switchable_processor import (
    SimpleSwitchableProcessor,
)
from gem5.isas import ISA
from gem5.resources.resource import DiskImageResource, obtain_resource
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires


NUMACTL_DISK_IMAGE = Path.home() / ".cache/gem5/x86-ubuntu-24.04-numactl.img"


parser = argparse.ArgumentParser()
parser.add_argument(
    "--memory",
    choices=("split", "stock-ddr5"),
    default="split",
    help="Use split-range memory or intentionally incompatible stock DDR5.",
)
parser.add_argument(
    "--max-ticks",
    type=int,
    default=1,
    help="Maximum ticks for config-generation validation.",
)
args = parser.parse_args()

requires(
    coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL,
    kvm_required=True,
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

if args.memory == "split":
    memory = SplitRangeChanneledMemory(
        DDR5_6400_4x8,
        num_channels=2,
        interleaving_size=64,
        size="64GiB",
    )
else:
    memory = DIMM_DDR5_6400(size="64GiB")

processor = SimpleSwitchableProcessor(
    starting_core_type=CPUTypes.KVM,
    switch_core_type=CPUTypes.TIMING,
    isa=ISA.X86,
    num_cores=2,
)

for proc in processor.start:
    proc.core.usePerf = False

board = LargeMemoryX86Board(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

workload = obtain_resource(
    "x86-ubuntu-24.04-boot-with-systemd", resource_version="5.0.0"
)
workload.set_parameter(
    "disk_image",
    DiskImageResource(local_path=str(NUMACTL_DISK_IMAGE), root_partition="1"),
)
board.set_workload(workload)

simulator = Simulator(board=board)
simulator.run(max_ticks=args.max_ticks)
