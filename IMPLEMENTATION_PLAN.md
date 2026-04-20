# Fixed NUMA RAM Model for gem5 x86 FS

## Summary

This project now uses an x86-only full-system memory model with:

`x86 sparse RAM map -> one 8-channel local node0 -> CXL-like memory-only node1 -> boots -> NUMA visible`

The current source tree intentionally targets X86. Do not build or validate
`build/ALL/gem5.opt` for this work; the expected build target is
`build/X86/gem5.opt`.

The original step folders are historical evidence for the completed baseline.
Documentation-only material lives in `step_00_design_and_usage`; the remaining
step folders patch code, run gem5, boot Linux, or validate artifacts. Most step
folders contain:

- `README.md`
- `NOTES.md`
- `artifacts/`
- `patches/`
- `scripts/`

## Current Memory Organization

The live physical memory layout keeps the x86 PCI hole and exposes two NUMA
nodes to Linux:

| NUMA node | Region | Start | End Exclusive | Size | Meaning |
| --- | --- | ---: | ---: | ---: | --- |
| 0 | node0 low RAM | `0x0000000000` | `0x00c0000000` | 3GiB | local DDR5 below the x86 PCI hole |
| none | x86 PCI/platform hole | `0x00c0000000` | `0x0100000000` | 1GiB | not guest RAM |
| 0 | node0 high RAM | `0x0100000000` | `0x1040000000` | 61GiB | same local DDR5 system above the hole |
| 1 | node1 RAM | `0x1040000000` | `0x2040000000` | 64GiB | CXL-like memory-only node |

Node `0` totals 64GiB. Node `1` totals 64GiB.

Node0 low and node0 high are the same local memory system, artificially split
only because x86 reserves `[3GiB, 4GiB)` for the PCI/platform hole. They are not
separate memory classes, tiers, or latency domains.

## Key Interfaces

Large x86 full-system configs use `LargeMemoryX86Board`; stock `X86Board`
remains on its documented small-memory path. The memory component is
`TwoTierMemory`.

`TwoTierMemory` exposes:

- `node0_ranges`: `[0, 3GiB)` and `[4GiB, 65GiB)`
- `node1_ranges`: `[65GiB, 129GiB)`
- `node0_low_ctrls[0..7]`: eight DDR5 channel controllers backing low node0 RAM
- `node0_high_ctrls[0..7]`: eight DDR5 channel controllers backing high node0 RAM
- `slow_ctrls[0..1]`: node1 DDR5 controllers behind the CXL-like path
- `slow_cxl_links[0..1]`: one `CxlMemLink` per node1 slow channel
- `get_mem_ports()`: 16 direct node0 controller ports followed by 2 node1 CXL CPU-side ports
- `get_memory_controllers()`: all 18 memory controllers
- `get_uninterleaved_range()`: the three guest RAM ranges
- `get_default_memory_ranges()`: project-local large-board range hook
- `get_numa_memory_ranges()`: `{0: node0_ranges, 1: node1_ranges}` for SRAT/SLIT metadata

Every node0 controller uses the same DRAM interface and timing model:
`DDR5_6400_4x8_32GiB`. There is no low-versus-high latency distinction.

Node1 remains the CXL-like memory-only node. Its extra latency is modeled only
through `CxlMemLink`; the backing DDR5 controllers use the same static DDR
frontend/backend latency values as node0.

Node `1` latency is modeled as:

`CXL M2S queue/serialization -> DDR5 media -> CXL S2M queue/serialization`

The default model does not add fixed CXL base latency to node `1`. Optional
`m2s_latency`/`s2m_latency` parameters remain available for calibration sweeps,
but the validation default is `0ns` in both directions.

## Interleaving Contract

Node0 is one uniform 8-channel DDR5 system split into two physical ranges by
the PCI hole. For both node0 low and node0 high:

- `num_channels = 8`
- `interleaving_size = 64B`
- channel bits are identical across low and high
- channel `i` in low maps to channel `i` in high
- low/high use separate backing `AbstractMemory` objects for KVM correctness

The resulting node0 channel range strings use the same pattern for both ranges:

`<range>:<channel>:64:128:256`

For node0, this uses 3 channel bits for 8-way interleaving. Do not replace this
with 2-way striping or with different low/high interleave patterns.

There is no `RangeAddrMapper` in the current design. Every guest RAM range is
backed directly by real memory objects.

## Ruby Directories

Ruby directory count is 18:

- 8 directories for `node0_low_ctrls`
- 8 directories for `node0_high_ctrls`
- 2 directories for node1 slow controllers behind `CxlMemLink`

Each directory corresponds to one channel-backed address range. Node1 directory
behavior and the `CxlMemLink` path remain unchanged.

## x86 Board and NUMA Exposure

`LargeMemoryX86Board` exposes the sparse x86 map through E820:

- `[0, 639KiB)` usable
- `[639KiB, 1MiB)` reserved
- `[1MiB, 3GiB)` usable
- `[3GiB, 4GiB)` PCI/platform hole
- `[4GiB, 65GiB)` usable node0 high RAM
- `[65GiB, 129GiB)` usable node1 RAM

SRAT/SLIT exposure:

- CPUs/APIC IDs attach only to node0
- node0 memory affinity covers `[0, 639KiB)`, `[1MiB, 3GiB)`, and `[4GiB, 65GiB)`
- node1 memory affinity covers `[65GiB, 129GiB)`
- node1 remains memory-only

Do not change the low-memory boot layout, PCI hole, node1 slow memory design, or
the CXL path as part of node0 channel work.

## Step Plan

1. Completed baseline: `step_00_design_and_usage`, `step_02_baseline_fs_config`, `step_04_second_mem_ctrl`, `step_05_route_ranges_to_ctrls`, `step_06_guest_boot_with_two_ranges`, `step_08_expose_fast_slow_as_numa_nodes`, `step_09_validate_linux_numa`, `step_10_kvm_to_timing_switch`, and `step_11_microbench_validation` are merged conceptually into one finished milestone: ordinary two-node RAM routes to separate controllers, boots x86 Linux, exposes local/CXL-like RAM as NUMA nodes, supports KVM-to-Timing ROI switching, and has a small NUMA placement microbenchmark.

2. Completed node0 redesign: node0 is now one uniform 8-channel DDR5 local memory node. The low and high physical ranges are only fragments of that same node, split by the x86 PCI hole. Node0 has 16 direct Ruby-facing controllers/directories: 8 low and 8 high, with identical 8-way interleaving. Node1 remains unchanged as a CXL-like memory-only node with 2 slow channels behind `CxlMemLink`.

3. Planned calibration/features pass: tune CXL link defaults, add broader read/write sweeps, and decide whether the backing media should remain gem5 DDR5 or move to Ramulator for final experiments.

4. Added bandwidth-versus-loaded-latency curve pass: Intel MLC was checked on
   the current host and is not usable from this workspace (`mlc` is absent, and
   the host is AMD EPYC). `step_12_bw_latency_curve` provides an in-tree
   MLC-style replacement that defaults the guest to eight cores, sweeps
   background read-stream workers, and records pointer-chase loaded latency for
   NUMA memory nodes `0` and `1`. The expected curve is lower latency and
   higher sustained bandwidth for local node `0`, and higher loaded latency with
   lower sustained bandwidth for CXL-like node `1` once link serialization and
   queueing pressure are visible.

5. Recommended saturation pass starts with 16 guest cores via
   `step_12_bw_latency_curve/scripts/run_16core_curve.sh`. The run uses one
   latency thread and up to 15 bandwidth workers with worker step `2`. Treat 16
   cores as sufficient only if node `0` bandwidth flattens by the right edge of
   the graph; otherwise run a later 32-core curve. Node `1` may flatten earlier
   because it is behind two CXL-like links.

6. Added efficient higher-pressure pass:
   `step_12_bw_latency_curve/scripts/run_32core_curve.sh` defaults to 32 guest
   cores, one latency thread, 31 bandwidth workers, and worker step `4`. This
   is the recommended next run when the 16-core curve does not inject enough
   read bandwidth. The benchmark now parses `worker_step` correctly when
   `cpu_mhz` is also supplied, and the worker hot loop avoids a stop check on
   every cache line so it spends more TimingSimpleCPU work on read generation.

7. Fixed the zero-worker latency interpretation problem: the previous 4 MiB
   latency buffer fit in the aggregate Ruby L2 for 16-core and 32-core runs, so
   `workers=0` measured warmed-cache pointer-chase latency and made node0 and
   node1 appear the same. Step 12 now defaults to a 64 MiB latency buffer and
   16 MiB worker buffers, and the checker requires those defaults in the guest
   workload packaging.

## CXL Type 3 Plan

The local CXL 3.2 spec notes that a Type 3 memory expansion device supports
CXL.io and CXL.mem, and a passive HDM-H memory expander primarily services host
requests over CXL.mem without using CXL.cache. It also describes CXL.cachemem
68B and 256B flit modes. The first model should use those facts as boundaries
while staying intentionally abstract.

Stage 3A: Define the modeling boundary. Completed.

- Keep Linux exposure as ordinary NUMA RAM at first: no guest driver, no DAX/devdax, no pmem, no CXL enumeration requirement.
- Treat node `1` as HDM-H-like host-managed memory.
- Model only the CXL.mem data path for CPU-originated reads and writes.
- Keep CXL.io management/configuration out of the timing path for this stage.

Stage 3B: Add an explicit CXL link object on the slow path. Completed.

- Add a gem5 `ClockedObject` bridge, `CxlMemLink`, with a CPU-side response port and a memory-side request port.
- Connect only node `1` Ruby directory memory-out ports through this object.
- Leave node `0` local RAM directly connected to DDR5 controllers.
- Preserve the current `TwoTierMemory` API so board, E820, SRAT, SLIT, and workload scripts keep working.

Stage 3C: Model flit queueing and serialization. Completed initial version.

- Add parameters: `flit_size_bytes` (`68` or `256` expected), `bandwidth`, `m2s_latency`, `s2m_latency`, `m2s_queue_depth_flits`, `s2m_queue_depth_flits`, `request_header_flits`, and `response_header_flits`.
- Convert each gem5 memory packet into simplified CXL.mem message work:
  - read: M2S request flits plus S2M data-response flits;
  - write: M2S request-with-data flits plus S2M no-data response flits.
- Compute queue occupancy and serialization delay from flit count, not just packet count. Changing `flit_size_bytes` must change queue residence time and bandwidth pressure.
- Start with deterministic FIFO queues; add credits, retry, and control flit overhead only after the simple model is validated.

Stage 3D: Add stats and validation hooks. Initial validation completed.

- Track per-direction flits, packets, queue occupancy, queue wait time,
  serialization time, optional base latency, stalls from full queues, and total
  added CXL delay.
- Validate synthetic reads/writes to node `0` versus node `1`.
- Sweep `flit_size_bytes`, queue depth, and link bandwidth; node `1`
  latency/bandwidth should move while node `0` remains unchanged.
- Default validation requires `m2s_latency=0` and `s2m_latency=0`, so node `1`
  extra delay comes from queue wait and flit serialization only.

Stage 3E: Calibration/features.

- Add a dedicated checker for CXL parameter sweeps so flit size, bandwidth,
  optional base latency, and queue depth regressions are caught automatically.
  Completed initial checker: `step_11_microbench_validation/scripts/check_cxl_latency_model.py`.
- Add write-heavy and mixed read/write synthetic probes. Completed initial
  guest suite: `read_seq`, `write_seq`, `readwrite_seq`, `read_stride`, and
  dependent-load `chase`.
- Add visualization for access-latency and bandwidth discrepancies. Completed
  initial SVG/CSV generator:
  `step_11_microbench_validation/scripts/visualize_microbench.py`.
- Decide whether the CXL queues should model separate request/data/response virtual channels or a shared per-direction FIFO.
- Decide whether the CXL link should keep counting in-flight propagation as FIFO occupancy or split queue occupancy from link occupancy.
- Calibrate default CXL bandwidth/latency values against the target CXL generation/link width.

Stage 3F: Decide whether Ramulator is needed.

- Keep gem5 DDR5 backing memory for the first CXL-link model.
- Use Ramulator only if the experiment needs more faithful media timing, bank behavior, refresh behavior, or a memory technology not well represented by gem5's built-in DRAM interface.
- If Ramulator is added, keep it behind the CXL link object so CXL queueing remains separable from media timing.

## Validation Requirements

- After every gem5 source patch: `cd /home/cc/inmem/gem5 && scons build/X86/gem5.opt -j$(nproc)`.
- Do not run `scons build/ALL/gem5.opt -j$(nproc)` for this project unless a future task explicitly adds non-X86 ISA support.
- Every new stage must update this `IMPLEMENTATION_PLAN.md` when completed.
- Routing validation must inspect `config.ini/config.json` and include stats or debug evidence that node0-range and node1-range traffic separate at the controller level.
- Guest memory validation before NUMA must show all guest RAM ranges as System RAM and explicitly note expected NUMA behavior for that stage.
- NUMA validation must include kernel boot log checks for NUMA, SRAT, and SLIT parsing.
- CXL validation must include sweeps proving that flit size, link bandwidth,
  optional fixed base latency, and queue depth affect only node `1` traffic.
  The default pass must additionally prove that fixed CXL base latency is zero.
- Bandwidth/latency curve validation must use
  `step_12_bw_latency_curve/scripts/check_bwlat_config.py` for packaging and
  `step_12_bw_latency_curve/scripts/visualize_bwlat.py` after a full run to
  create `bw_latency_results.csv` and `bw_latency_results.svg` from
  `BWL_RESULT` serial output.

## Locked Architecture

- stdlib memory component defines two NUMA nodes using three guest RAM ranges.
- x86 board exposes those ranges through E820.
- Ruby routing uses address ranges to build one directory per channel-backed range.
- ACPI maps CPU and memory affinity to Linux NUMA nodes via minimal SRAT/SLIT.
- Node `0` is one 8-channel DDR5 local node split into low/high physical ranges only by the PCI hole.
- Node `0` low and high ranges use identical channel interleaving and uniform DRAM timing.
- Node `0` low/high controllers are separate backing objects for KVM correctness; they are still one logical local memory system.
- Node `1` has two CXL Type 3-like paths: Ruby directory -> `CxlMemLink` -> DDR5 channel.
- No `RangeAddrMapper` is used.

## Validation Record

- `python3 -m py_compile` passed for the edited memory, board, traffic, and validation scripts.
- `scons build/X86/gem5.opt -j$(nproc)` completed successfully.
- `step_04_second_mem_ctrl/scripts/check_two_tier_config.py` passed on `step_04_second_mem_ctrl/artifacts/m5out_x86_node0_8ch/config.ini`; it validates 18 controllers, 18 directories, 8-way node0 low interleaving, 8-way node0 high interleaving, 2-way node1 interleaving, and no mapper-backed RAM.
- `step_05_route_ranges_to_ctrls/scripts/check_route_ranges.py` passed on `step_05_route_ranges_to_ctrls/artifacts/m5out_x86_node0_8ch_node0` and `step_05_route_ranges_to_ctrls/artifacts/m5out_x86_node0_8ch_slow`; it validates node0-high traffic reaches all eight high controllers and node1 traffic crosses only slow CXL links.
- `step_08_expose_fast_slow_as_numa_nodes/scripts/check_acpi_numa_config.py` passed on `step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out_x86_node0_8ch`.
- `step_09_validate_linux_numa/scripts/check_linux_numa.py` passed on `step_09_validate_linux_numa/artifacts/m5out_x86_node0_8ch`; Linux reports online NUMA nodes `0-1`, CPUs `0,1` on node0, no CPUs on node1, node0 MemTotal `65948604 kB`, and node1 MemTotal `66058812 kB`.
- `step_10_kvm_to_timing_switch/scripts/check_kvm_timing_config.py` passed on `step_10_kvm_to_timing_switch/artifacts/m5out_x86_node0_8ch`.
- `step_11_microbench_validation/scripts/check_microbench_config.py` passed on `step_11_microbench_validation/artifacts/m5out_x86_node0_8ch`.
- `step_11_microbench_validation/scripts/check_microbench_config.py` passed on `step_11_microbench_validation/artifacts/m5out_zero_base_smoke`; this validates zero fixed CXL base latency in the default config and the expanded benchmark suite packaging.
- `step_11_microbench_validation/scripts/check_cxl_latency_model.py` passed on `step_11_microbench_validation/artifacts/m5out_zero_base_smoke`; it reports CXL config fixed base latency ticks `m2s=[0, 0]`, `s2m=[0, 0]` and all 18 MemCtrls at 10ns static frontend/backend latency.
- E820/SRAT inspection shows node0 ranges `[0, 639KiB)`, `[1MiB, 3GiB)`, and `[4GiB, 65GiB)` map to node0; node1 range `[65GiB, 129GiB)` maps to the memory-only node1.
- Intel MLC availability check on the current host found no `mlc` executable in
  `PATH` or under the workspace; `lscpu` reports vendor `AuthenticAMD` and
  model `AMD EPYC 7763 64-Core Processor`.
- Step 12 host compile smoke passed:
  `cc -O2 -Wall -Wextra -pthread -o step_12_bw_latency_curve/artifacts/numa_bwlat_host_smoke step_12_bw_latency_curve/scripts/numa_bwlat.c`.
- Step 12 Python compile smoke passed:
  `python3 -m py_compile step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py step_12_bw_latency_curve/scripts/visualize_bwlat.py step_12_bw_latency_curve/scripts/check_bwlat_config.py`.
- Step 12 config-generation smoke passed:
  `gem5/build/X86/gem5.opt --outdir=step_12_bw_latency_curve/artifacts/m5out step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py --max-ticks 1`.
- Step 12 packaging validation passed:
  `python3 step_12_bw_latency_curve/scripts/check_bwlat_config.py step_12_bw_latency_curve/artifacts/m5out`; it validates the eight-core default config, 18 controllers/interfaces, two `CxlMemLink` instances, zero fixed CXL base latency, SRAT/SLIT, and embedded pthread/`mbind` `BWL_RESULT` workload.
- Step 12 reduced full guest smoke passed with `--num-cores 2`,
  `--bwl-max-workers 1`, and `--bwl-latency-iters 2048`; it emitted
  `BWL_RESULT` rows for nodes `0` and `1`, and
  `step_12_bw_latency_curve/scripts/visualize_bwlat.py` wrote
  `bw_latency_results.csv` and `bw_latency_results.svg` under
  `step_12_bw_latency_curve/artifacts/m5out_short`. This short run validates
  plumbing only; larger latency-iteration counts are required for quantitative
  curves.
- Step 12 16-core config-generation smoke passed:
  `gem5/build/X86/gem5.opt --outdir=step_12_bw_latency_curve/artifacts/m5out_16c_config step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py --num-cores 16 --bwl-worker-step 2 --max-ticks 1`.
- Step 12 16-core packaging validation passed:
  `python3 step_12_bw_latency_curve/scripts/check_bwlat_config.py --min-cores 16 step_12_bw_latency_curve/artifacts/m5out_16c_config`; the config contains 16 KVM start CPUs and 16 Timing switch CPUs.
- Step 12 bad-result root cause found: the first 16-core full/long/short
  outputs used `clock_gettime(CLOCK_MONOTONIC)`, but guest Linux switched to
  `refined-jiffies` after failing TSC calibration. Elapsed time was therefore
  0ms or 1ms quantized, causing impossible bandwidth and meaningless latency.
- Step 12 benchmark timing fixed: `numa_bwlat.c` now uses gem5 x86 `rdtsc`
  cycles for `seconds`, `latency_ns`, and `bandwidth_mib_s`, prints
  `clock_seconds` only as a diagnostic, and accepts `BWL_CPU_MHZ`.
- Step 12 cycle-timed tiny full guest smoke passed on
  `step_12_bw_latency_curve/artifacts/m5out_cycle_tiny`; it emitted nonzero
  `cycles` and TSC-derived `seconds` while `clock_seconds` still showed the
  coarse jiffy behavior.
- Step 12 updated config-generation smoke passed on
  `step_12_bw_latency_curve/artifacts/m5out_cycle_config`; the embedded readfile
  includes `rdtsc`, `BWL_CPU_MHZ`, `cycles`, and `clock_seconds`.
- Step 12 `clflush` attempt is rejected: a full 16-core run using x86
  `clflush` aborted in `DataTranslation::finish` with
  `Assertion mode == state->mode failed`. Do not use `clflush` in this
  TimingSimpleCPU full-system benchmark path.
- Step 12 final no-`clflush` config-generation validation passed on
  `step_12_bw_latency_curve/artifacts/m5out_no_clflush_config`; the embedded
  readfile contains `rdtsc`, `BWL_CPU_MHZ`, `cycles`, and `clock_seconds`, and
  contains no `clflush`.

Known caveat: gem5 emits expected DRAM capacity mismatch warnings because each
`DDR5_6400_4x8_32GiB` interface has larger modeled capacity than its assigned
interleaved subrange. This is not a validation failure for the current channel
routing and NUMA work.

## References

- CXL spec chapters: `./doc/spec/cxl-spec-v3.2-markdown/index.md`
- Original CXL spec PDF: `./doc/spec/cxl-spec-v3.2.pdf`
