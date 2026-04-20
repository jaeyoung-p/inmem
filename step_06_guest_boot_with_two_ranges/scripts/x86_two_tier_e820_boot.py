#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Boot x86 Linux with TwoTierMemory and collect pre-NUMA memory evidence."""

from pathlib import Path

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
echo "=== STEP6 /proc/iomem ==="
cat /proc/iomem
echo "=== STEP6 /proc/meminfo ==="
cat /proc/meminfo
echo "=== STEP6 NUMA ONLINE ==="
cat /sys/devices/system/node/online || true
ls -d /sys/devices/system/node/node* || true
echo "=== STEP6 DMESG MEMORY/NUMA ==="
dmesg | grep -Ei "e820|BIOS-e820|System RAM|numa|srat|slit" || true
echo "=== STEP6 COMPLETE ==="
/sbin/m5 exit || m5 exit || true
"""


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

memory = TwoTierMemory()

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
        print("First exit: kernel booted")

    @overrides(ExitHandler)
    def _exit_simulation(self) -> bool:
        return False


class KeepKvmAfterBootExitHandler(AfterBootExitHandler):
    @overrides(AfterBootExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Second exit: after_boot.sh started")
        print("Keeping KVM for Step 6 guest memory-map evidence")

    @overrides(AfterBootExitHandler)
    def _exit_simulation(self) -> bool:
        return False


class AfterBootScriptExitHandler(ExitHandler, hypercall_num=3):
    _count = 0

    @overrides(ExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        type(self)._count += 1
        print(
            "Third exit: after_boot.sh boundary "
            f"{type(self)._count}; continuing once for readfile commands"
        )

    @overrides(ExitHandler)
    def _exit_simulation(self) -> bool:
        return type(self)._count > 1


simulator = Simulator(board=board)
simulator.run()
