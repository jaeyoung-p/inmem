#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Two-tier x86 FS workflow: boot with KVM, switch to Timing for ROI."""

import argparse
from pathlib import Path

import m5

from gem5.coherence_protocol import CoherenceProtocol
from gem5.components.boards.large_mem_x86 import LargeMemoryX86Board
from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)
from gem5.components.memory import TwoTierMemory
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_switchable_processor import (
    SimpleSwitchableProcessor,
)
from gem5.isas import ISA
from gem5.resources.resource import DiskImageResource, obtain_resource
from gem5.simulate.exit_handler import (
    AfterBootExitHandler,
    ExitHandler,
)
from gem5.simulate.simulator import Simulator
from gem5.utils.override import overrides
from gem5.utils.requires import requires


NUMACTL_DISK_IMAGE = Path.home() / ".cache/gem5/x86-ubuntu-24.04-numactl.img"


READFILE_CONTENTS = r"""#!/bin/bash
set -x
echo "=== STEP10 ROI BEGIN ==="
cat /sys/devices/system/node/online || true
for node in /sys/devices/system/node/node*; do
    echo "--- ${node} ---"
    cat "${node}/cpulist" 2>/dev/null || true
    grep -E "MemTotal|MemFree" "${node}/meminfo" 2>/dev/null || true
done
echo "=== STEP10 ROI PLACEHOLDER ==="
echo "Replace this block with the measurement workload."
echo "=== STEP10 ROI END ==="
sleep 5
"""


parser = argparse.ArgumentParser()
parser.add_argument(
    "--max-ticks",
    type=int,
    default=None,
    help="Optional maximum ticks for config-generation smoke validation.",
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

memory = TwoTierMemory(
    cxl_flit_size_bytes=args.cxl_flit_size,
    cxl_link_bandwidth=args.cxl_link_bandwidth,
    cxl_base_latency=args.cxl_base_latency,
    cxl_queue_depth_flits=args.cxl_queue_depth_flits,
)

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
workload.set_parameter("readfile_contents", READFILE_CONTENTS)
board.set_workload(workload)


class KernelBootedExitHandler(ExitHandler, hypercall_num=1):
    @overrides(ExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("First exit: kernel booted under KVM")

    @overrides(ExitHandler)
    def _exit_simulation(self) -> bool:
        return False


class SwitchAndResetAfterBootExitHandler(AfterBootExitHandler):
    @overrides(AfterBootExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Second exit: after_boot.sh started")
        print("Switching from KVM to Timing CPU")
        simulator.switch_processor()
        print("Resetting stats at ROI boundary")
        m5.stats.reset()

    @overrides(AfterBootExitHandler)
    def _exit_simulation(self) -> bool:
        return False


class DumpAndExitAfterBootScriptExitHandler(ExitHandler, hypercall_num=3):
    @overrides(ExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Third exit: after_boot.sh finished ROI script")
        print("Dumping stats at ROI boundary")
        m5.stats.dump()

    @overrides(ExitHandler)
    def _exit_simulation(self) -> bool:
        return True


simulator = Simulator(board=board)
if args.max_ticks is None:
    simulator.run()
else:
    simulator.run(max_ticks=args.max_ticks)
