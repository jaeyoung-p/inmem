#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Run one DMA-injected bandwidth-versus-latency point on the two-tier x86 board."""

import argparse
import json
import math
from pathlib import Path

import m5
from m5.objects import PyTrafficGen
from m5.ticks import fromSeconds
from m5.util.convert import (
    toLatency,
    toMemoryBandwidth,
)

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
C_SOURCE = (THIS_DIR / "numa_latency.c").read_text()
GUEST_SCRIPT = (THIS_DIR / "guest_dma_bwlat.sh").read_text()


def rate_to_Bps(rate_text: str) -> float:
    return float(toMemoryBandwidth(rate_text))


def format_rate_Bps(rate_Bps: float) -> str:
    if rate_Bps == 0:
        return "0"
    if float(rate_Bps).is_integer():
        return f"{int(rate_Bps)}B/s"
    return f"{rate_Bps:.6f}".rstrip("0").rstrip(".") + "B/s"


def split_dma_ranges(start: int, end: int, count: int, block_size: int):
    if count <= 0:
        return []

    aligned_start = ((start + block_size - 1) // block_size) * block_size
    aligned_end = (end // block_size) * block_size
    usable = aligned_end - aligned_start
    if usable < count * block_size:
        return [(start, end) for _ in range(count)]

    slice_size = (usable // count // block_size) * block_size
    if slice_size < block_size:
        return [(start, end) for _ in range(count)]

    ranges = []
    for index in range(count):
        range_start = aligned_start + index * slice_size
        range_end = aligned_end if index == count - 1 else range_start + slice_size
        ranges.append((range_start, range_end))
    return ranges


def traffic_gen_block_size(requested_block_size: int) -> int:
    # BaseTrafficGen requires block_size <= system cache line size. Keep the
    # user-facing DMA block size for metadata/range alignment, but drive the
    # same offered byte rate with legal cache-line-sized traffic requests.
    return min(requested_block_size, 64)


def traffic_sequence(
    generator: PyTrafficGen,
    duration: str,
    rate: str,
    block_size: int,
    start_addr: int,
    end_addr: int,
    post_idle: str,
):
    duration_ticks = fromSeconds(toLatency(duration))
    rate_bytes = toMemoryBandwidth(rate)
    period = fromSeconds(block_size / rate_bytes)
    yield generator.createLinear(
        duration_ticks,
        start_addr,
        end_addr,
        block_size,
        period,
        period,
        100,
        0,
    )
    # Keep the traffic generator alive after the active phase instead of
    # exhausting the iterator. Exhaustion can crash inside BaseTrafficGen.
    yield generator.createIdle(fromSeconds(toLatency(post_idle)))


class Step12DmaBoard(LargeMemoryX86Board):
    def __init__(self, *args, dma_injectors=None, **kwargs):
        self._step12_dma_injectors = list(dma_injectors or [])
        super().__init__(*args, **kwargs)
        for index, injector in enumerate(self._step12_dma_injectors):
            setattr(self, f"step12_dma_injector{index}", injector)

    def get_dma_ports(self):
        return list(super().get_dma_ports()) + [
            injector.port for injector in self._step12_dma_injectors
        ]


class Step12MESITwoLevelCacheHierarchy(MESITwoLevelCacheHierarchy):
    def __init__(self, *args, ruby_directory_tbes: int = 256, **kwargs):
        self._step12_ruby_directory_tbes = ruby_directory_tbes
        super().__init__(*args, **kwargs)

    def incorporate_cache(self, board):
        super().incorporate_cache(board)
        for controller in self._directory_controllers:
            controller.number_of_TBEs = self._step12_ruby_directory_tbes


parser = argparse.ArgumentParser()
parser.add_argument(
    "--max-ticks",
    type=int,
    default=None,
    help="Optional maximum ticks for config-generation smoke validation.",
)
parser.add_argument(
    "--node",
    type=int,
    choices=[0, 1],
    required=True,
    help="NUMA node to probe for latency and DMA injection.",
)
parser.add_argument(
    "--latency-mib",
    type=int,
    default=64,
    help="Latency working set size in MiB. Default: 64.",
)
parser.add_argument(
    "--latency-iters",
    type=int,
    default=65536,
    help="Dependent-load iterations per point. Default: 65536.",
)
parser.add_argument(
    "--cpu-mhz",
    type=float,
    default=2100.0,
    help="CPU frequency for rdtsc-to-ns conversion. Default: 2100.",
)
parser.add_argument(
    "--dma-total-rate",
    default="0",
    help=(
        'Aggregate offered DMA read rate across all injectors, e.g. "64GiB/s". '
        'Use "0" for unloaded latency. Default: 0.'
    ),
)
parser.add_argument(
    "--dma-target-per-injector",
    default="8GiB/s",
    help=(
        "Target per-injector offered rate for automatic injector count when "
        "--dma-total-rate is set. Default: 8GiB/s."
    ),
)
parser.add_argument(
    "--dma-duration",
    default="1s",
    help=(
        "DMA injection duration. Keep this comfortably longer than the whole "
        "post-ROI benchmark window. Default: 1s."
    ),
)
parser.add_argument(
    "--dma-block-size",
    type=int,
    default=256,
    help="DMA injector request size in bytes. Default: 256.",
)
parser.add_argument(
    "--dma-injectors",
    type=int,
    default=None,
    help=(
        "Number of DMA injectors. Default: automatic from --dma-total-rate "
        "and --dma-target-per-injector."
    ),
)
parser.add_argument(
    "--dma-progress-check",
    default="100ms",
    help="PyTrafficGen no-progress watchdog. Default: 100ms.",
)
parser.add_argument(
    "--dma-max-outstanding",
    type=int,
    default=2048,
    help="Maximum outstanding DMA requests per injector. Default: 2048.",
)
parser.add_argument(
    "--dma-post-idle",
    default="1s",
    help="Idle tail after active DMA traffic. Default: 1s.",
)
parser.add_argument(
    "--dma-elastic-req",
    action=argparse.BooleanOptionalAction,
    default=True,
    help="Enable PyTrafficGen backpressure-aware injection. Default: enabled.",
)
parser.add_argument(
    "--ruby-directory-tbes",
    type=int,
    default=256,
    help=(
        "Number of transient buffer entries per MESI_Two_Level directory "
        "controller. Default: 256."
    ),
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

if args.latency_mib <= 0:
    raise ValueError("--latency-mib must be positive")
if args.latency_iters <= 0:
    raise ValueError("--latency-iters must be positive")
if args.cpu_mhz <= 0.0:
    raise ValueError("--cpu-mhz must be positive")
if args.dma_block_size <= 0 or (args.dma_block_size % 64) != 0:
    raise ValueError("--dma-block-size must be a positive multiple of 64")
if args.dma_injectors is not None and args.dma_injectors < 0:
    raise ValueError("--dma-injectors must be non-negative")
if args.dma_max_outstanding < 0:
    raise ValueError("--dma-max-outstanding must be non-negative")
if args.ruby_directory_tbes <= 0:
    raise ValueError("--ruby-directory-tbes must be positive")

dma_requested_injectors = args.dma_injectors
dma_target_per_injector_Bps = rate_to_Bps(args.dma_target_per_injector)
if dma_target_per_injector_Bps <= 0.0:
    raise ValueError("--dma-target-per-injector must be positive")

dma_total_rate_Bps = rate_to_Bps(args.dma_total_rate)
if dma_total_rate_Bps < 0.0:
    raise ValueError("--dma-total-rate must be non-negative")
if dma_total_rate_Bps == 0.0:
    dma_injector_count = 0
elif args.dma_injectors is None:
    dma_injector_count = math.ceil(
        dma_total_rate_Bps / dma_target_per_injector_Bps
    )
else:
    dma_injector_count = args.dma_injectors
    if dma_injector_count <= 0:
        raise ValueError(
            "--dma-injectors must be positive for nonzero --dma-total-rate"
        )
dma_per_injector_rate_Bps = (
    dma_total_rate_Bps / dma_injector_count if dma_injector_count else 0.0
)
dma_per_injector_rate = format_rate_Bps(dma_per_injector_rate_Bps)
dma_total_rate = args.dma_total_rate

dma_traffic_block_size = traffic_gen_block_size(args.dma_block_size)

requires(
    coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL,
    kvm_required=True,
)

cache_hierarchy = Step12MESITwoLevelCacheHierarchy(
    l1i_size="32KiB",
    l1i_assoc=8,
    l1d_size="32KiB",
    l1d_assoc=8,
    l2_size="512KiB",
    l2_assoc=16,
    num_l2_banks=1,
    ruby_directory_tbes=args.ruby_directory_tbes,
)

memory = TwoTierMemory(
    cxl_flit_size_bytes=args.cxl_flit_size,
    cxl_link_bandwidth=args.cxl_link_bandwidth,
    cxl_base_latency=args.cxl_base_latency,
    cxl_queue_depth_flits=args.cxl_queue_depth_flits,
)

if args.node == 0:
    dma_range = memory.node0_ranges[1]
else:
    dma_range = memory.node1_ranges[0]

dma_start = int(dma_range.start)
dma_end = dma_start + dma_range.size()

dma_injectors = [
    PyTrafficGen(
        progress_check=args.dma_progress_check,
        max_outstanding_reqs=args.dma_max_outstanding,
        elastic_req=args.dma_elastic_req,
    )
    for _ in range(dma_injector_count)
]
dma_ranges = split_dma_ranges(
    dma_start, dma_end, len(dma_injectors), args.dma_block_size
)

processor = SimpleSwitchableProcessor(
    starting_core_type=CPUTypes.KVM,
    switch_core_type=CPUTypes.TIMING,
    isa=ISA.X86,
    num_cores=1,
)

for proc in processor.start:
    proc.core.usePerf = False

board = Step12DmaBoard(
    clk_freq=f"{args.cpu_mhz}MHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
    dma_injectors=dma_injectors,
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
cat > /tmp/numa_latency.c <<'STEP12_C_EOF'
{C_SOURCE}
STEP12_C_EOF
cat > /tmp/guest_dma_bwlat.sh <<'STEP12_SH_EOF'
{GUEST_SCRIPT}
STEP12_SH_EOF
chmod +x /tmp/guest_dma_bwlat.sh
export STEP12_NODE="{args.node}"
export STEP12_LATENCY_MIB="{args.latency_mib}"
export STEP12_LATENCY_ITERS="{args.latency_iters}"
export STEP12_CPU_MHZ="{args.cpu_mhz}"
/tmp/guest_dma_bwlat.sh
"""
workload.set_parameter("readfile_contents", readfile_contents)
board.set_workload(workload)

point_metadata = {
    "node": args.node,
    "dma_rate": dma_per_injector_rate,
    "dma_per_injector_rate": dma_per_injector_rate,
    "dma_per_injector_rate_Bps": dma_per_injector_rate_Bps,
    "dma_total_rate": dma_total_rate,
    "dma_total_rate_Bps": dma_total_rate_Bps,
    "dma_target_per_injector": args.dma_target_per_injector,
    "dma_requested_injectors": dma_requested_injectors,
    "dma_duration": args.dma_duration,
    "dma_injectors": len(dma_injectors),
    "dma_block_size": args.dma_block_size,
    "dma_traffic_block_size": dma_traffic_block_size,
    "dma_progress_check": args.dma_progress_check,
    "dma_max_outstanding": args.dma_max_outstanding,
    "ruby_directory_tbes": args.ruby_directory_tbes,
    "dma_post_idle": args.dma_post_idle,
    "dma_elastic_req": args.dma_elastic_req,
    "latency_mib": args.latency_mib,
    "latency_iters": args.latency_iters,
    "cpu_mhz": args.cpu_mhz,
    "dma_range_start": dma_start,
    "dma_range_size": dma_range.size(),
}
metadata_path = Path(m5.options.outdir) / "step12_point.json"
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
        print("Second exit: after_boot.sh started; staying on KVM for guest setup")

    @overrides(AfterBootExitHandler)
    def _exit_simulation(self) -> bool:
        return False


class SwitchAtRoiExitHandler(ExitHandler, hypercall_num=4):
    @overrides(ExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Fourth exit: Step 12 ROI begins")
        print("Switching from KVM to TimingSimpleCPU")
        simulator.switch_processor()
        print("Resetting stats at Step 12 ROI boundary")
        m5.stats.reset()

        if not dma_injectors or dma_total_rate_Bps == 0.0:
            print("Starting Step 12 with no DMA injection")
            return

        print(
            f"Starting {len(dma_injectors)} DMA injector(s) at "
            f"{dma_per_injector_rate} each "
            f"({dma_total_rate} total) across "
            f"[{hex(dma_start)}, {hex(dma_end)})"
        )
        for injector, (range_start, range_end) in zip(dma_injectors, dma_ranges):
            injector.start(
                traffic_sequence(
                    injector,
                    args.dma_duration,
                    dma_per_injector_rate,
                    dma_traffic_block_size,
                    range_start,
                    range_end,
                    args.dma_post_idle,
                )
            )

    @overrides(ExitHandler)
    def _exit_simulation(self) -> bool:
        return False


class DumpAndExitAfterBootScriptExitHandler(ExitHandler, hypercall_num=3):
    @overrides(ExitHandler)
    def _process(self, simulator: "Simulator") -> None:
        print("Third exit: after_boot.sh finished Step 12 script")
        print("Dumping stats after Step 12 ROI")
        m5.stats.dump()

    @overrides(ExitHandler)
    def _exit_simulation(self) -> bool:
        return True


simulator = Simulator(board=board)
if args.max_ticks is None:
    simulator.run()
else:
    simulator.run(max_ticks=args.max_ticks)
