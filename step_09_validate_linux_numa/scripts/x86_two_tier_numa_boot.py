#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Boot x86 Linux and validate guest-visible two-node NUMA topology."""

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
run_dmesg() {
    if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
        sudo -n dmesg
    else
        dmesg
    fi
}
echo "=== STEP9 DMESG NUMA ==="
run_dmesg | grep -i numa || true
echo "=== STEP9 DMESG SRAT ==="
run_dmesg | grep -i srat || true
echo "=== STEP9 DMESG SLIT ==="
run_dmesg | grep -i slit || true
echo "=== STEP9 JOURNAL NUMA ==="
journalctl -k --no-pager | grep -i numa || true
echo "=== STEP9 JOURNAL SRAT ==="
journalctl -k --no-pager | grep -i srat || true
echo "=== STEP9 JOURNAL SLIT ==="
journalctl -k --no-pager | grep -i slit || true
echo "=== STEP9 DMESG POLICY ==="
cat /proc/sys/kernel/dmesg_restrict || true
echo "=== STEP9 NUMACTL HARDWARE ==="
numactl --hardware || true
echo "=== STEP9 LSCPU ==="
lscpu || true
echo "=== STEP9 NODE ONLINE ==="
cat /sys/devices/system/node/online || true
echo "=== STEP9 NODE DETAILS ==="
for node in /sys/devices/system/node/node*; do
    echo "--- ${node} ---"
    cat "${node}/cpulist" 2>/dev/null || true
    grep -E "MemTotal|MemFree" "${node}/meminfo" 2>/dev/null || true
done
echo "=== STEP9 NUMASTAT ==="
numastat || true
echo "=== STEP9 COMPLETE ==="
sleep 5
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


class SwitchProcessorAfterBootExitHandler(AfterBootExitHandler):
    @overrides(AfterBootExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Second exit: after_boot.sh started")
        print("Keeping KVM CPU active for Step 9 guest inspection commands")

    @overrides(AfterBootExitHandler)
    def _exit_simulation(self) -> bool:
        return False


class AfterBootScriptExitHandler(ExitHandler, hypercall_num=3):
    @overrides(ExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Third exit: after_boot.sh finished Step 9 command script")

    @overrides(ExitHandler)
    def _exit_simulation(self) -> bool:
        return True


simulator = Simulator(board=board)
simulator.run()
