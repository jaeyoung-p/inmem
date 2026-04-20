# Large-Memory x86 / CXL Type 3 Handoff

Last updated: 2026-04-19T01:01:55Z

## Current Status

The large-memory x86 board path is implemented and validated. Stock
`X86Board` remains on the documented 3GiB memory path, while all large x86
full-system experiments use `LargeMemoryX86Board`.

The current memory model is:

- node0: one uniform 8-channel DDR5 local memory node, split only by the x86
  3-4GiB PCI hole.
- node1: CXL-like memory-only node, routed through `CxlMemLink` with zero
  fixed base latency by default.

Step 9 real Linux NUMA boot validation now passes. The previous sparsemem
panic is resolved by making every guest-visible RAM range directly backed by
real `AbstractMemory` objects and by removing the KVM-incompatible fast
`RangeAddrMapper` path.

Intel MLC was checked on the current host before adding the latest benchmark
work. No `mlc` binary is present in `PATH` or under this workspace, and the host
CPU vendor is `AuthenticAMD` (`AMD EPYC 7763 64-Core Processor`). Step 12
therefore adds an in-tree MLC-style replacement for the needed experiment:
bandwidth versus loaded latency curves per guest NUMA memory node.

Important build rule: this workspace only targets X86. Do not run
`scons build/ALL/gem5.opt`; use `scons build/X86/gem5.opt -j$(nproc)`.

## Physical Memory Layout

Guest physical map:

- conventional low RAM: `[0x0000000000, 0x000009fc00)` = 639KiB usable
- legacy reserved low region: `[0x000009fc00, 0x0000100000)` = reserved
- node0 low RAM: `[0x0000100000, 0x00c0000000)` = usable part of `[0, 3GiB)`
- x86 PCI/platform hole: `[0x00c0000000, 0x0100000000)` = reserved, not RAM
- node0 high RAM: `[0x0100000000, 0x1040000000)` = 61GiB
- node1 CXL slow RAM: `[0x1040000000, 0x2040000000)` = 64GiB

Logical NUMA view:

- node0 memory:
  - `[0, 639KiB)`
  - `[1MiB, 3GiB)`
  - `[4GiB, 65GiB)`
- node1 memory:
  - `[65GiB, 129GiB)`
- All exposed CPUs/APIC IDs attach only to node0.
- node1 is memory-only.

## Node0 Memory Organization

File: `gem5/src/python/gem5/components/memory/tiered.py`

`TwoTierMemory` now models node0 as one uniform 8-channel DDR5 system:

- `node0_low_ctrls[0..7]` back `[0, 3GiB)`.
- `node0_high_ctrls[0..7]` back `[4GiB, 65GiB)`.
- Both low and high halves use the same DRAM interface,
  `DDR5_6400_4x8_32GiB`.
- Both low and high halves use the same controller static frontend/backend
  latency: `10ns`.
- Both low and high halves use identical 8-way 64B interleaving.
- Channel `i` in low matches channel `i` in high.
- There is no low-vs-high latency distinction and no fast-vs-fast-high tier.

gem5 prints the 8-way node0 interleaved ranges in config output as:

```text
<range>:<channel>:64:128:256
```

For example:

```text
0:3221225472:0:64:128:256
4294967296:69793218560:0:64:128:256
```

That corresponds to 64B interleaving with three channel-select bits.

KVM correctness rule:

- Every guest-visible RAM range is backed by real `AbstractMemory`.
- There is no `RangeAddrMapper`.
- There is no shared backing between node0 low and node0 high.
- The low/high split exists only because of the x86 PCI hole.

## Node1 Memory Organization

Node1 keeps the CXL-like path:

- `slow_ctrls[0..1]` back `[65GiB, 129GiB)`.
- `slow_cxl_links[0..1]` sit between Ruby and the slow controllers.
- `CxlMemLink` models the extra CXL-like delay from flit FIFO queueing and
  serialization.
- Default `m2s_latency` and `s2m_latency` are `0ns`; fixed base latency is not
  part of the default node1 model.
- Optional fixed base latency remains available for explicit calibration
  sweeps via `--cxl-base-latency`.
- Slow controller static latency is not inflated; CXL delay stays in the link.

## Ruby Directory Layout

There is one Ruby directory per exposed channel-backed range:

- `directory_controllers00` through `directory_controllers07`:
  node0 low channels 0-7.
- `directory_controllers08` through `directory_controllers15`:
  node0 high channels 0-7.
- `directory_controllers16` and `directory_controllers17`:
  node1 slow channels 0-1 through `CxlMemLink`.

Total memory controllers and DRAM interfaces in the two-tier model:

- 16 node0 DDR5 controllers/interfaces.
- 2 node1 DDR5 controllers/interfaces.
- 18 total `MemCtrl` objects.
- 18 total `DRAMInterface` objects.
- 2 total `CxlMemLink` objects.
- 0 `RangeAddrMapper` objects.

## Board Behavior

File: `gem5/src/python/gem5/components/boards/large_mem_x86.py`

`LargeMemoryX86Board` subclasses stock `X86Board` and owns project-local large
x86 full-system behavior:

- Uses `memory.get_default_memory_ranges()` when available.
- Otherwise splits ordinary memory larger than 3GiB into:
  - `[0, 3GiB)`
  - `[4GiB, 4GiB + excess)`
- Calls `memory.set_memory_range(data_ranges)`.
- Raises a friendly `ValueError` if a stock single-range memory object rejects
  the split.
- Sets `board.mem_ranges` to real data ranges plus the stock 1MiB internal I/O
  marker at `[0xc0000000, 0xc0100000)`.
- Replaces inherited E820 with all real RAM ranges plus explicit reserved PCI
  hole coverage.
- Adds SRAT/SLIT only if memory provides project-local
  `get_numa_memory_ranges()`.
- Currently supports exactly two NUMA nodes, `[0, 1]`.

Current E820 policy for NUMA large-memory runs:

- `[0x00000000, 0x0009fc00)` usable conventional low memory
- `[0x0009fc00, 0x00100000)` reserved
- `[0x00100000, 0xc0000000)` usable low node0 RAM
- `[0xc0000000, 0xffff0000)` reserved PCI/platform hole
- `[0xffff0000, 0x100000000)` reserved m5ops
- high RAM ranges emitted above 4GiB

Current SRAT policy:

- all exposed CPU/APIC IDs map to node0.
- node0 memory affinity:
  - `[0x00000000, 0x0009fc00)`
  - `[0x00100000, 0xc0000000)`
  - `[0x100000000, 0x1040000000)`
- node1 memory affinity:
  - `[0x1040000000, 0x2040000000)`
- SLIT distances: local `10`, remote `20`.

## Other Code Notes

File: `gem5/src/python/gem5/components/memory/split_range.py`

`SplitRangeChanneledMemory` remains a reusable helper for ordinary large RAM
with sparse x86 ranges. It is separate from the CXL/two-tier research path.

Files:

- `gem5/src/sim/kernel_workload.hh`
- `gem5/src/arch/x86/fs_workload.cc`

Kernel entry handling is offset-aware:

- `KernelWorkload::getEntry()` applies `_loadAddrMask` and `_loadAddrOffset`.
- x86 FS workload initializes the PC with `getEntry()`.
- Current configs use offset `0`, so behavior matches the stock entry point.

## Updated Scripts

The following full-system scripts instantiate `LargeMemoryX86Board`:

- `step_04_second_mem_ctrl/scripts/x86_two_tier_kvm_timing.py`
- `step_06_guest_boot_with_two_ranges/scripts/x86_two_tier_e820_boot.py`
- `step_08_expose_fast_slow_as_numa_nodes/scripts/x86_two_tier_numa_config.py`
- `step_09_validate_linux_numa/scripts/x86_two_tier_numa_boot.py`
- `step_10_kvm_to_timing_switch/scripts/x86_two_tier_kvm_to_timing_roi.py`
- `step_11_microbench_validation/scripts/x86_two_tier_numa_microbench.py`
- `step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py`

Important validation updates:

- `step_04_second_mem_ctrl/scripts/check_two_tier_config.py` expects:
  - 18 memory controllers/interfaces
  - 18 Ruby directories
  - no `RangeAddrMapper`
  - identical 8-way node0 low/high interleaving
- `step_05_route_ranges_to_ctrls/scripts/two_tier_ruby_traffic.py` accepts
  `--tier node0`; `--tier fast` remains a compatibility alias.
- `step_05_route_ranges_to_ctrls/scripts/check_route_ranges.py` validates:
  - node0-high traffic reaches all eight node0-high controllers
  - slow traffic crosses both CXL links
  - slow and node0 traffic remain separated
- Step 10 and Step 11 config checkers expect 18 `MemCtrl` and 18
  `DRAMInterface` instances.
- Step 11 also includes:
  - `check_cxl_latency_model.py` to prove the default has no fixed CXL base
    latency and that all controllers keep 10ns static frontend/backend latency.
  - `visualize_microbench.py` to convert `MB_RESULT` serial output into CSV and
    SVG access-time/bandwidth plots.
  - `run_latency_sweep.sh` to compare the default `0ns` fixed-base model with
    an explicit `80ns` calibration run.
- Step 12 adds:
  - `numa_bwlat.c`, a pthread/`mbind` benchmark that sweeps background
    read-stream worker count while one thread measures dependent pointer-chase
    loaded latency.
  - `x86_two_tier_numa_bwlat.py`, an eight-core-by-default KVM-to-Timing
    full-system config for bandwidth pressure experiments.
  - `visualize_bwlat.py`, which converts `BWL_RESULT` serial output into
    `bw_latency_results.csv` and `bw_latency_results.svg`.
  - `check_bwlat_config.py`, a packaging checker for the eight-core
    config/readfile path.
- Step 12 expected result:
  - node0 should have the lowest unloaded pointer-chase latency and higher
    sustainable bandwidth because it is local eight-channel DDR5.
  - node1 should show higher loaded latency and lower sustainable bandwidth
    when the CXL-like link serialization/FIFO queueing becomes visible.
  - zero-worker latency must use a working set larger than the shared Ruby L2
    footprint. The earlier 4 MiB latency-buffer runs measured warmed-cache
    pointer chasing and incorrectly made node0 and node1 look identical at
    `workers=0`.
  - CXL flit size, link bandwidth, queue depth, and optional fixed base latency
    sweeps should move the node1 curve while leaving node0 effectively
    unchanged.
- Recommended first saturation run is now the 16-core helper:
  `step_12_bw_latency_curve/scripts/run_16core_curve.sh`. It uses one latency
  thread, up to 15 bandwidth workers, worker step `2`, 16 MiB worker buffers,
  a 64 MiB latency buffer, and writes `artifacts/m5out_16c`. If node0 bandwidth
  is still clearly rising at `workers=15`, use a later 32-core run; node1
  flattening earlier is expected.
- The 16-core helper now honors `BWL_WORKER_STEP` even when `BWL_CPU_MHZ` is
  passed. A previous run at `artifacts/m5out_16c_fixed` swept every worker
  count from `0` through `15`; it completed and produced CSV/SVG output, but it
  was more expensive than intended and used the obsolete 4 MiB latency buffer.
  That dense run reached about `11307 MiB/s` on node0 and `9054 MiB/s` on node1
  at 15 workers, but its `workers=0` latencies should not be used.
- For higher injected read bandwidth, use
  `step_12_bw_latency_curve/scripts/run_32core_curve.sh`. It defaults to 32
  guest cores, one latency thread, 31 bandwidth workers, and worker step `4`.
  TimingSimpleCPU worker streams are request-generation limited, so more guest
  worker cores are the main lever for pushing substantially beyond the 16-core
  bandwidth.

Intentionally unchanged:

- Step 02 baseline remains on stock `X86Board` with 3GiB RAM.
- Node1 CXL-like memory path remains routed through `CxlMemLink`; its default
  fixed base latency is now zero.
- The x86 PCI hole and low-memory boot handling remain unchanged.

## Validation Completed

All commands below were run with `build/X86/gem5.opt` only.

### Build / Static

Passed:

```sh
cd /home/cc/inmem/gem5
python3 -m py_compile \
  src/python/gem5/components/memory/tiered.py \
  ../step_04_second_mem_ctrl/scripts/check_two_tier_config.py \
  ../step_05_route_ranges_to_ctrls/scripts/check_route_ranges.py \
  ../step_05_route_ranges_to_ctrls/scripts/two_tier_ruby_traffic.py \
  ../step_10_kvm_to_timing_switch/scripts/check_kvm_timing_config.py \
  ../step_11_microbench_validation/scripts/check_microbench_config.py \
  ../step_11_microbench_validation/scripts/check_cxl_latency_model.py \
  ../step_11_microbench_validation/scripts/visualize_microbench.py

scons build/X86/gem5.opt -j$(nproc)
```

### Step 4 Two-Tier Config

Passed:

```sh
cd /home/cc/inmem/gem5
build/X86/gem5.opt \
  --outdir=../step_04_second_mem_ctrl/artifacts/m5out_x86_node0_8ch \
  ../step_04_second_mem_ctrl/scripts/x86_two_tier_kvm_timing.py \
  --max-ticks 1

python3 ../step_04_second_mem_ctrl/scripts/check_two_tier_config.py \
  ../step_04_second_mem_ctrl/artifacts/m5out_x86_node0_8ch/config.ini
```

Observed:

- node0 is one 8-channel DDR5 memory system split by PCI hole.
- node0 low/high use identical 8-way 64B interleaving.
- every guest-visible RAM range has direct KVM-safe backing memory.
- node1 traffic crosses two `CxlMemLink` queues.
- 18 Ruby directories exist, one per exposed channel range.

### Step 5 Route Validation

Passed:

```sh
cd /home/cc/inmem/gem5
build/X86/gem5.opt \
  --outdir=../step_05_route_ranges_to_ctrls/artifacts/m5out_x86_node0_8ch_node0 \
  ../step_05_route_ranges_to_ctrls/scripts/two_tier_ruby_traffic.py \
  --tier node0

build/X86/gem5.opt \
  --outdir=../step_05_route_ranges_to_ctrls/artifacts/m5out_x86_node0_8ch_slow \
  ../step_05_route_ranges_to_ctrls/scripts/two_tier_ruby_traffic.py \
  --tier slow

python3 ../step_05_route_ranges_to_ctrls/scripts/check_route_ranges.py \
  --fast-outdir ../step_05_route_ranges_to_ctrls/artifacts/m5out_x86_node0_8ch_node0 \
  --slow-outdir ../step_05_route_ranges_to_ctrls/artifacts/m5out_x86_node0_8ch_slow
```

Observed:

- node0-high traffic increments all eight node0-high controllers.
- slow traffic increments slow CXL links/controllers/directories.
- node0 and slow traffic remain separated.

### Step 8 ACPI NUMA Config

Passed:

```sh
cd /home/cc/inmem/gem5
build/X86/gem5.opt \
  --outdir=../step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out_x86_node0_8ch \
  ../step_08_expose_fast_slow_as_numa_nodes/scripts/x86_two_tier_numa_config.py \
  --max-ticks 1

python3 ../step_08_expose_fast_slow_as_numa_nodes/scripts/check_acpi_numa_config.py \
  ../step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out_x86_node0_8ch
```

Observed:

- RSDT/XSDT contain MADT, SRAT, and SLIT.
- SRAT maps APIC IDs 0 and 1 to node0.
- SRAT maps node0 low/high RAM around the PCI hole to the same node.
- SRAT maps node1 slow RAM at 65GiB-129GiB.
- SLIT distance matrix is local=10, remote=20.

### Step 9 Linux NUMA Boot

Passed:

```sh
cd /home/cc/inmem/gem5
build/X86/gem5.opt \
  --outdir=../step_09_validate_linux_numa/artifacts/m5out_x86_node0_8ch \
  ../step_09_validate_linux_numa/scripts/x86_two_tier_numa_boot.py

python3 ../step_09_validate_linux_numa/scripts/check_linux_numa.py \
  ../step_09_validate_linux_numa/artifacts/m5out_x86_node0_8ch
```

Observed:

- kernel boot log and journal show SRAT and SLIT parsing.
- Linux reports online NUMA nodes `0-1`.
- `lscpu` reports CPUs `0,1` on node0 and no CPUs on node1.
- node0 `MemTotal`: `65948604 kB`.
- node1 `MemTotal`: `66058812 kB`.
- serial output contains `=== STEP9 COMPLETE ===`.
- no `subsection_map_init`, `__bitmap_set`, or kernel panic was observed.
- `dmesg` command ran but is blocked by guest `dmesg_restrict=1`;
  journal/serial logs provide kernel evidence.

### Step 10 / Step 11 Config Smokes

Passed:

```sh
cd /home/cc/inmem/gem5
build/X86/gem5.opt \
  --outdir=../step_10_kvm_to_timing_switch/artifacts/m5out_x86_node0_8ch \
  ../step_10_kvm_to_timing_switch/scripts/x86_two_tier_kvm_to_timing_roi.py \
  --max-ticks 1

python3 ../step_10_kvm_to_timing_switch/scripts/check_kvm_timing_config.py \
  ../step_10_kvm_to_timing_switch/artifacts/m5out_x86_node0_8ch
```

Passed:

```sh
cd /home/cc/inmem/gem5
build/X86/gem5.opt \
  --outdir=../step_11_microbench_validation/artifacts/m5out_zero_base_smoke \
  ../step_11_microbench_validation/scripts/x86_two_tier_numa_microbench.py \
  --max-ticks 1

python3 ../step_11_microbench_validation/scripts/check_microbench_config.py \
  ../step_11_microbench_validation/artifacts/m5out_zero_base_smoke

python3 ../step_11_microbench_validation/scripts/check_cxl_latency_model.py \
  ../step_11_microbench_validation/artifacts/m5out_zero_base_smoke
```

Observed:

- Step 10 config contains KVM start cores, Timing switch cores, SRAT/SLIT,
  18 DDR5-derived memory interfaces, and no `RangeAddrMapper`.
- Step 11 config/readfile packaging matches the new memory topology, keeps
  the ROI switch path, and embeds the `read_seq`, `write_seq`,
  `readwrite_seq`, `read_stride`, and `chase` probes.
- Step 11 default CXL fixed base latency is zero in both directions:
  `m2s=[0, 0]`, `s2m=[0, 0]`.
- A calibration smoke config with `--cxl-base-latency=80ns` was also generated
  at `step_11_microbench_validation/artifacts/m5out_fixed_base_smoke` and
  validated with `check_cxl_latency_model.py --allow-fixed-base`.

### Step 12 Bandwidth / Latency Curve

Current-host MLC check:

```sh
command -v mlc || command -v mlc_avx512 || command -v mlc_internal || true
find /home/cc/inmem -iname '*mlc*' -o -iname 'mlc'
lscpu
```

Observed:

- no MLC executable was found in `PATH` or this workspace.
- host CPU vendor/model is `AuthenticAMD`, `AMD EPYC 7763 64-Core Processor`.
- host has 256 online CPUs and two NUMA nodes, but this does not provide Intel
  MLC in the current environment.

Passed:

```sh
cd /home/cc/inmem
cc -O2 -Wall -Wextra -pthread \
  -o step_12_bw_latency_curve/artifacts/numa_bwlat_host_smoke \
  step_12_bw_latency_curve/scripts/numa_bwlat.c

python3 -m py_compile \
  step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py \
  step_12_bw_latency_curve/scripts/visualize_bwlat.py \
  step_12_bw_latency_curve/scripts/check_bwlat_config.py

gem5/build/X86/gem5.opt \
  --outdir=step_12_bw_latency_curve/artifacts/m5out \
  step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py \
  --max-ticks 1

python3 step_12_bw_latency_curve/scripts/check_bwlat_config.py \
  step_12_bw_latency_curve/artifacts/m5out

gem5/build/X86/gem5.opt \
  --outdir=step_12_bw_latency_curve/artifacts/m5out_short \
  step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py \
  --num-cores 2 \
  --bwl-max-workers 1 \
  --bwl-latency-iters 2048 \
  --bwl-worker-mib 1 \
  --bwl-latency-mib 1

python3 step_12_bw_latency_curve/scripts/check_bwlat_config.py \
  --min-cores 2 \
  step_12_bw_latency_curve/artifacts/m5out_short

python3 step_12_bw_latency_curve/scripts/visualize_bwlat.py \
  step_12_bw_latency_curve/artifacts/m5out_short
```

Observed:

- the standalone host smoke emitted `BWL_RESULT` rows.
- Step 12 config generation completed with eight KVM start CPUs and eight
  Timing switch CPUs.
- Step 12 packaging validation confirms 18 memory controllers/interfaces, two
  `CxlMemLink` instances, no `RangeAddrMapper`, zero fixed CXL base latency,
  SRAT/SLIT, and an embedded pthread/`mbind` bandwidth-latency workload.
- the reduced two-core full guest smoke emitted `BWL_RESULT` rows for nodes 0
  and 1 and produced `bw_latency_results.csv` plus `bw_latency_results.svg`.
  This pre-fix short run is an end-to-end smoke only and is not valid for
  performance interpretation because it used the older jiffy-clock timing path.
- 16-core config-generation smoke passed:
  `gem5/build/X86/gem5.opt --outdir=step_12_bw_latency_curve/artifacts/m5out_16c_config step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py --num-cores 16 --bwl-worker-step 2 --max-ticks 1`.
- 16-core packaging validation passed:
  `python3 step_12_bw_latency_curve/scripts/check_bwlat_config.py --min-cores 16 step_12_bw_latency_curve/artifacts/m5out_16c_config`; `config.ini` contains 16 `X86KvmCPU` and 16 `BaseTimingSimpleCPU` instances.
- Full 16-core curve is intentionally left as an explicit long run via
  `step_12_bw_latency_curve/scripts/run_16core_curve.sh`; it should be run when
  the workspace can spend the required Timing-mode runtime.
- Bad-result diagnosis: the original `m5out_16c_short`, `m5out_16c_long`, and
  `m5out_16c_full` curves are invalid. The guest log shows TSC calibration
  failed and Linux switched to `refined-jiffies`, so `clock_gettime()` was
  0ms/1ms quantized. That made bandwidth and latency nonsense.
- Fix applied after that diagnosis:
  - `numa_bwlat.c` now times with gem5 x86 `rdtsc` cycles and prints
    `clock_seconds` only as a diagnostic.
  - `run_16core_curve.sh` now defaults to 16 MiB worker buffers, a 64 MiB
    latency buffer, `BWL_LATENCY_ITERS=65536`, and `BWL_CPU_MHZ=3000`.
  - the 64 MiB latency buffer fixes the equal `workers=0` node0/node1 latency
    problem caused by the obsolete 4 MiB cache-resident pointer-chase set.
- Cycle-timed tiny full guest smoke passed on
  `step_12_bw_latency_curve/artifacts/m5out_cycle_tiny`: it emitted nonzero
  `cycles`, TSC-derived `seconds`, and diagnostic `clock_seconds` that still
  demonstrates the broken jiffy clock path.
- Updated config-generation smoke passed on
  `step_12_bw_latency_curve/artifacts/m5out_cycle_config`; the embedded readfile
  contains `rdtsc`, `BWL_CPU_MHZ`, `cycles`, and `clock_seconds`.
- Do not use x86 `clflush` in the Step 12 TimingSimpleCPU benchmark path. A
  full 16-core run with the `clflush` version aborted at tick
  `22616912553562` in `DataTranslation::finish` with
  `Assertion mode == state->mode failed`.
- Final no-`clflush` config-generation validation passed on
  `step_12_bw_latency_curve/artifacts/m5out_no_clflush_config`; the embedded
  readfile contains `rdtsc`, `BWL_CPU_MHZ`, `cycles`, and `clock_seconds`, and
  contains no `clflush`.

## Notes / Caveats

- `TwoTierMemory` still uses its historic class name, but node0 is no longer
  two fast tiers. It is one 8-channel local node split by the PCI hole.
- `DDR5_6400_4x8_32GiB` remains the interface class for all controllers. With
  the current address assignment, gem5 emits expected capacity mismatch
  warnings for node0 channel-backed subranges; these warnings do not affect the
  config, routing, or Linux NUMA validation.
- `SplitRangeChanneledMemory` intentionally creates duplicated controller sets
  per range, matching the legacy x86 FS workaround. It is not the CXL/two-tier
  research path.
- `get_default_memory_ranges()` and `get_numa_memory_ranges()` are project-local
  optional hooks, not upstream stdlib APIs.
- `LargeMemoryX86Board` currently supports only the two-node `[0, 1]` NUMA
  policy because the SLIT policy is hardcoded for two nodes.
