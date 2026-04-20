#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Run a NUMA bandwidth-versus-loaded-latency curve benchmark."""

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
THIS_DIR = Path(__file__).resolve().parent
C_SOURCE = (THIS_DIR / "numa_bwlat.c").read_text()
GUEST_SCRIPT = (THIS_DIR / "guest_numa_bwlat.sh").read_text()


parser = argparse.ArgumentParser()
parser.add_argument(
    "--max-ticks",
    type=int,
    default=None,
    help="Optional maximum ticks for config-generation smoke validation.",
)
parser.add_argument(
    "--num-cores",
    type=int,
    default=8,
    help=(
        "Guest CPU cores. One core runs pointer-chase latency and the rest "
        "can inject bandwidth."
    ),
)
parser.add_argument(
    "--bwl-max-workers",
    type=int,
    default=None,
    help="Override guest BWL_MAX_WORKERS. Default in guest is nproc - 1.",
)
parser.add_argument(
    "--bwl-worker-step",
    type=int,
    default=None,
    help="Override guest BWL_WORKER_STEP. Default is 1.",
)
parser.add_argument(
    "--bwl-worker-mib",
    type=int,
    default=None,
    help="Override guest BWL_WORKER_MIB. Default is 16.",
)
parser.add_argument(
    "--bwl-latency-mib",
    type=int,
    default=None,
    help="Override guest BWL_LATENCY_MIB. Default is 64.",
)
parser.add_argument(
    "--bwl-latency-iters",
    type=int,
    default=None,
    help="Override guest BWL_LATENCY_ITERS. Default is 65536.",
)
parser.add_argument(
    "--bwl-cpu-mhz",
    type=float,
    default=None,
    help="Override guest BWL_CPU_MHZ for TSC-cycle timing. Default is 3000.",
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
    default="0ns",
    help=(
        "Optional per-direction fixed CXL.mem base link latency. The project "
        "default is 0ns so node 1 latency comes from queueing and flit "
        "serialization only."
    ),
)
parser.add_argument(
    "--cxl-queue-depth-flits",
    type=int,
    default=256,
    help="CXL.mem FIFO depth per direction in flits.",
)
args = parser.parse_args()

if args.num_cores < 2:
    raise ValueError("--num-cores must be at least 2 for loaded latency")
for option_name in (
    "bwl_worker_step",
    "bwl_worker_mib",
    "bwl_latency_mib",
    "bwl_latency_iters",
):
    option_value = getattr(args, option_name)
    if option_value is not None and option_value <= 0:
        raise ValueError(f"--{option_name.replace('_', '-')} must be positive")
if args.bwl_max_workers is not None and args.bwl_max_workers < 0:
    raise ValueError("--bwl-max-workers must be non-negative")
if args.bwl_cpu_mhz is not None and args.bwl_cpu_mhz <= 0.0:
    raise ValueError("--bwl-cpu-mhz must be positive")


def guest_export(name: str, value: object) -> str:
    if value is None:
        return ""
    return f'export {name}="{value}"\n'


GUEST_ENV = "".join(
    [
        guest_export("BWL_MAX_WORKERS", args.bwl_max_workers),
        guest_export("BWL_WORKER_STEP", args.bwl_worker_step),
        guest_export("BWL_WORKER_MIB", args.bwl_worker_mib),
        guest_export("BWL_LATENCY_MIB", args.bwl_latency_mib),
        guest_export("BWL_LATENCY_ITERS", args.bwl_latency_iters),
        guest_export("BWL_CPU_MHZ", args.bwl_cpu_mhz),
    ]
)


READFILE_CONTENTS = f"""#!/bin/bash
set -eux
cat > /tmp/numa_bwlat.c <<'STEP12_C_EOF'
{C_SOURCE}
STEP12_C_EOF
cat > /tmp/guest_numa_bwlat.sh <<'STEP12_SH_EOF'
{GUEST_SCRIPT}
STEP12_SH_EOF
chmod +x /tmp/guest_numa_bwlat.sh
{GUEST_ENV}/tmp/guest_numa_bwlat.sh
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
    num_l2_banks=args.num_cores,
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
    num_cores=args.num_cores,
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


class AfterBootStartedExitHandler(AfterBootExitHandler):
    @overrides(AfterBootExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Second exit: after_boot.sh started; staying on KVM for build")

    @overrides(AfterBootExitHandler)
    def _exit_simulation(self) -> bool:
        return False


class SwitchAtRoiExitHandler(ExitHandler, hypercall_num=4):
    @overrides(ExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Fourth exit: Step 12 bandwidth/latency ROI begins")
        print("Switching from KVM to Timing CPU")
        simulator.switch_processor()
        print("Resetting stats at bandwidth/latency ROI boundary")
        m5.stats.reset()

    @overrides(ExitHandler)
    def _exit_simulation(self) -> bool:
        return False


class DumpAndExitAfterBootScriptExitHandler(ExitHandler, hypercall_num=3):
    @overrides(ExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Third exit: after_boot.sh finished Step 12 script")
        print("Dumping stats after bandwidth/latency ROI")
        m5.stats.dump()

    @overrides(ExitHandler)
    def _exit_simulation(self) -> bool:
        return True


simulator = Simulator(board=board)
if args.max_ticks is None:
    simulator.run()
else:
    simulator.run(max_ticks=args.max_ticks)
