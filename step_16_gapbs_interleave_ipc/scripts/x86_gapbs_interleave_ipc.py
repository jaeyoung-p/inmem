#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Run one GAPBS-style PageRank SpMV interleave IPC point."""

import argparse
import json
from pathlib import Path

import m5

from gem5.coherence_protocol import CoherenceProtocol
from gem5.components.boards.large_mem_x86 import LargeMemoryX86Board
from gem5.components.cachehierarchies.ruby.mesi_three_level_cache_hierarchy import (
    MESIThreeLevelCacheHierarchy,
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
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.override import overrides
from gem5.utils.requires import requires


NUMACTL_DISK_IMAGE = Path.home() / ".cache/gem5/x86-ubuntu-24.04-numactl.img"
THIS_DIR = Path(__file__).resolve().parent
BENCH_SOURCE = (THIS_DIR / "gapbs_pr_spmv_roi.cc").read_text()
GUEST_SCRIPT = (THIS_DIR / "guest_gapbs_ipc.sh").read_text()

VARIANTS = {
    "baseline": {
        "aes_latency": "0ns",
        "integrity_mac_enable": False,
        "cxl_extra_data_slots": 0,
    },
    "aes": {
        "aes_latency": "40ns",
        "integrity_mac_enable": False,
        "cxl_extra_data_slots": 0,
    },
    "aes_mac": {
        "aes_latency": "40ns",
        "integrity_mac_enable": True,
        "cxl_extra_data_slots": 0,
    },
    "aes_extra_slot": {
        "aes_latency": "40ns",
        "integrity_mac_enable": False,
        "cxl_extra_data_slots": 1,
    },
}


class Step16MESIThreeLevelCacheHierarchy(MESIThreeLevelCacheHierarchy):
    def __init__(self, *args, ruby_directory_tbes: int = 256, **kwargs):
        self._step16_ruby_directory_tbes = ruby_directory_tbes
        super().__init__(*args, **kwargs)

    def incorporate_cache(self, board):
        super().incorporate_cache(board)
        for controller in (
            self._l1_controllers
            + self._l2_controllers
            + self._directory_controllers
        ):
            if hasattr(controller, "number_of_TBEs"):
                controller.number_of_TBEs = self._step16_ruby_directory_tbes


parser = argparse.ArgumentParser()
parser.add_argument(
    "--variant",
    choices=sorted(VARIANTS),
    default="baseline",
    help="Step 16 timing variant. Default: baseline.",
)
parser.add_argument(
    "--gapbs-scale",
    type=int,
    default=16,
    help="Generated graph scale passed as GAPBS -g. Default: 16.",
)
parser.add_argument(
    "--gapbs-trials",
    type=int,
    default=1,
    help="Measured PageRank SpMV trials passed as GAPBS -n. Default: 1.",
)
parser.add_argument(
    "--gapbs-max-iters",
    type=int,
    default=20,
    help="Maximum PageRank iterations passed as GAPBS -i. Default: 20.",
)
parser.add_argument(
    "--gapbs-kernel",
    choices=["pr_spmv"],
    default="pr_spmv",
    help="Graph kernel to run. Default: pr_spmv.",
)
parser.add_argument(
    "--gapbs-file",
    default="",
    help=(
        "Optional guest-visible GAPBS .sg graph path passed as -f. "
        "The file is still loaded under numactl interleave policy."
    ),
)
parser.add_argument(
    "--cpu-mhz",
    type=float,
    default=2100.0,
    help="CPU frequency. Default: 2100.",
)
parser.add_argument(
    "--num-cores",
    type=int,
    default=1,
    help="Number of KVM/O3 CPU cores exposed to the guest. Default: 1.",
)
parser.add_argument(
    "--omp-threads",
    type=int,
    default=None,
    help="OpenMP thread count for the guest benchmark. Default: --num-cores.",
)
parser.add_argument(
    "--roi-cpu",
    choices=["o3", "timing"],
    default="o3",
    help="Detailed ROI CPU. Final Step 16 numbers should use o3. Default: o3.",
)
parser.add_argument(
    "--max-ticks",
    type=int,
    default=None,
    help="Optional maximum ticks for config-generation smoke validation.",
)
parser.add_argument(
    "--roi-max-insts",
    type=int,
    default=0,
    help=(
        "Optional instruction limit scheduled immediately after the ROI CPU "
        "switch. A value of 0 disables the limit. Default: 0."
    ),
)
parser.add_argument(
    "--ruby-directory-tbes",
    type=int,
    default=4096,
    help="Ruby transient buffer entries where supported. Default: 4096.",
)
parser.add_argument(
    "--l1i-size",
    default="32KiB",
    help="Private L1I size. Default: 32KiB.",
)
parser.add_argument(
    "--l1i-assoc",
    type=int,
    default=8,
    help="Private L1I associativity. Default: 8.",
)
parser.add_argument(
    "--l1d-size",
    default="48KiB",
    help="Private L1D size. Default: 48KiB.",
)
parser.add_argument(
    "--l1d-assoc",
    type=int,
    default=12,
    help="Private L1D associativity. Default: 12.",
)
parser.add_argument(
    "--l2-size",
    default="2MiB",
    help="Private L2 size. Default: 2MiB.",
)
parser.add_argument(
    "--l2-assoc",
    type=int,
    default=16,
    help="Private L2 associativity. Default: 16.",
)
parser.add_argument(
    "--l3-size",
    default="60MiB",
    help="Shared L3 size. Default: 60MiB.",
)
parser.add_argument(
    "--l3-assoc",
    type=int,
    default=20,
    help="Shared L3 associativity. Default: 20.",
)
parser.add_argument(
    "--num-l3-banks",
    type=int,
    default=1,
    help="Number of shared L3 banks. Default: 1.",
)
parser.add_argument(
    "--cxl-flit-size",
    type=int,
    default=256,
    help="CXL.mem flit size in bytes for the slow-tier link model.",
)
parser.add_argument(
    "--cxl-link-bandwidth",
    default="64GiB/s",
    help="Per-direction CXL.mem link bandwidth.",
)
parser.add_argument(
    "--cxl-base-latency",
    default="60ns",
    help="Per-direction fixed CXL.mem base latency. Default: 60ns.",
)
parser.add_argument(
    "--cxl-queue-depth-flits",
    type=int,
    default=256,
    help="CXL.mem FIFO depth per direction in flits. Default: 256.",
)
args = parser.parse_args()

if args.gapbs_scale <= 0:
    raise ValueError("--gapbs-scale must be positive")
if args.gapbs_trials <= 0:
    raise ValueError("--gapbs-trials must be positive")
if args.gapbs_max_iters <= 0:
    raise ValueError("--gapbs-max-iters must be positive")
if args.cpu_mhz <= 0.0:
    raise ValueError("--cpu-mhz must be positive")
if args.num_cores <= 0:
    raise ValueError("--num-cores must be positive")
if args.omp_threads is not None and args.omp_threads <= 0:
    raise ValueError("--omp-threads must be positive")
if args.ruby_directory_tbes <= 0:
    raise ValueError("--ruby-directory-tbes must be positive")
if args.roi_max_insts < 0:
    raise ValueError("--roi-max-insts must be non-negative")
if args.l1i_assoc <= 0 or args.l1d_assoc <= 0:
    raise ValueError("L1 associativity values must be positive")
if args.l2_assoc <= 0 or args.l3_assoc <= 0:
    raise ValueError("L2/L3 associativity values must be positive")
if args.num_l3_banks <= 0:
    raise ValueError("--num-l3-banks must be positive")

variant = VARIANTS[args.variant]
if variant["integrity_mac_enable"] and variant["cxl_extra_data_slots"]:
    raise ValueError("integrity MAC and extra CXL data slots must not be combined")
omp_threads = args.omp_threads if args.omp_threads is not None else args.num_cores

requires(
    coherence_protocol_required=CoherenceProtocol.MESI_THREE_LEVEL,
    kvm_required=True,
)

cache_hierarchy = Step16MESIThreeLevelCacheHierarchy(
    l1i_size=args.l1i_size,
    l1i_assoc=args.l1i_assoc,
    l1d_size=args.l1d_size,
    l1d_assoc=args.l1d_assoc,
    l2_size=args.l2_size,
    l2_assoc=args.l2_assoc,
    l3_size=args.l3_size,
    l3_assoc=args.l3_assoc,
    num_l3_banks=args.num_l3_banks,
    ruby_directory_tbes=args.ruby_directory_tbes,
)

memory = TwoTierMemory(
    cxl_flit_size_bytes=args.cxl_flit_size,
    cxl_link_bandwidth=args.cxl_link_bandwidth,
    cxl_base_latency=args.cxl_base_latency,
    cxl_queue_depth_flits=args.cxl_queue_depth_flits,
    cxl_extra_data_slots=variant["cxl_extra_data_slots"],
    aes_latency=variant["aes_latency"],
    integrity_mac_enable=variant["integrity_mac_enable"],
)

roi_cpu_type = CPUTypes.O3 if args.roi_cpu == "o3" else CPUTypes.TIMING
processor = SimpleSwitchableProcessor(
    starting_core_type=CPUTypes.KVM,
    switch_core_type=roi_cpu_type,
    isa=ISA.X86,
    num_cores=args.num_cores,
)

for proc in processor.start:
    proc.core.usePerf = False

board = LargeMemoryX86Board(
    clk_freq=f"{args.cpu_mhz}MHz",
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

readfile_contents = f"""#!/bin/bash
set -eux
cat > /tmp/gapbs_pr_spmv_roi.cc <<'STEP16_CC_EOF'
{BENCH_SOURCE}
STEP16_CC_EOF
cat > /tmp/guest_gapbs_ipc.sh <<'STEP16_SH_EOF'
{GUEST_SCRIPT}
STEP16_SH_EOF
chmod +x /tmp/guest_gapbs_ipc.sh
export GAPBS_SCALE="{args.gapbs_scale}"
export GAPBS_TRIALS="{args.gapbs_trials}"
export GAPBS_MAX_ITERS="{args.gapbs_max_iters}"
export GAPBS_FILE="{args.gapbs_file}"
export OMP_NUM_THREADS="{omp_threads}"
/tmp/guest_gapbs_ipc.sh
"""
workload.set_parameter("readfile_contents", readfile_contents)
board.set_workload(workload)

point_metadata = {
    "variant": args.variant,
    "gapbs_kernel": args.gapbs_kernel,
    "gapbs_file": args.gapbs_file,
    "gapbs_scale": args.gapbs_scale,
    "gapbs_trials": args.gapbs_trials,
    "gapbs_max_iters": args.gapbs_max_iters,
    "numa_policy": "interleave=0,1",
    "cpu_bind": "node0",
    "roi_cpu": args.roi_cpu,
    "roi_max_insts": args.roi_max_insts,
    "num_cores": args.num_cores,
    "omp_threads": omp_threads,
    "cpu_mhz": args.cpu_mhz,
    "cache_hierarchy": "MESI_Three_Level",
    "l1i_size": args.l1i_size,
    "l1i_assoc": args.l1i_assoc,
    "l1d_size": args.l1d_size,
    "l1d_assoc": args.l1d_assoc,
    "l2_size": args.l2_size,
    "l2_assoc": args.l2_assoc,
    "l3_size": args.l3_size,
    "l3_assoc": args.l3_assoc,
    "num_l3_banks": args.num_l3_banks,
    "ruby_directory_tbes": args.ruby_directory_tbes,
    "aes_latency": variant["aes_latency"],
    "integrity_mac_enable": variant["integrity_mac_enable"],
    "cxl_extra_data_slots": variant["cxl_extra_data_slots"],
    "cxl_flit_size": args.cxl_flit_size,
    "cxl_link_bandwidth": args.cxl_link_bandwidth,
    "cxl_base_latency": args.cxl_base_latency,
    "cxl_queue_depth_flits": args.cxl_queue_depth_flits,
}
metadata_path = Path(m5.options.outdir) / "step16_point.json"
metadata_path.write_text(json.dumps(point_metadata, indent=2) + "\n")


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
        print("Second exit: after_boot.sh started; staying on KVM for setup")

    @overrides(AfterBootExitHandler)
    def _exit_simulation(self) -> bool:
        return False


class SwitchAtRoiExitHandler(ExitHandler, hypercall_num=4):
    @overrides(ExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Fourth exit: Step 16 ROI begins")
        print(f"Switching from KVM to {args.roi_cpu}")
        simulator.switch_processor()
        print("Resetting stats at Step 16 ROI boundary")
        m5.stats.reset()
        if args.roi_max_insts:
            print(f"Scheduling Step 16 ROI instruction limit: {args.roi_max_insts}")
            simulator.schedule_max_insts(args.roi_max_insts)

    @overrides(ExitHandler)
    def _exit_simulation(self) -> bool:
        return False


class DumpAndExitAfterBootScriptExitHandler(ExitHandler, hypercall_num=3):
    @overrides(ExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Third exit: after_boot.sh finished Step 16 script")
        print("Dumping stats after Step 16 ROI")
        m5.stats.dump()

    @overrides(ExitHandler)
    def _exit_simulation(self) -> bool:
        return True


def dump_and_exit_on_max_insts():
    print("Step 16 ROI instruction limit reached")
    print("Dumping stats after Step 16 ROI instruction limit")
    m5.stats.dump()
    return True


simulator = Simulator(
    board=board,
    on_exit_event={ExitEvent.MAX_INSTS: dump_and_exit_on_max_insts},
)
if args.max_ticks is None:
    simulator.run()
else:
    simulator.run(max_ticks=args.max_ticks)
