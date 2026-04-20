# Large-Memory x86 / CXL NUMA Handoff

Last updated: 2026-04-20

## Current State

This workspace targets gem5 X86 full-system only. Use:

```sh
cd /home/cc/inmem/gem5
scons build/X86/gem5.opt -j$(nproc)
```

Do not use `build/ALL/gem5.opt` for this project.

The live model is:

```text
x86 sparse RAM map -> local node0 DDR5 -> CXL-like memory-only node1 -> Linux NUMA
```

Stock `X86Board` remains on the upstream small-memory path. Large-memory runs
use `LargeMemoryX86Board` and `TwoTierMemory`.

## Repositories

- outer repo: `git@github.com:jaeyoung-p/inmem.git`
- gem5 submodule/fork: `git@github.com:jaeyoung-p/gem5_25.1.0.0.git`
- outer commit at last handoff: `62c5820`
- gem5 commit at last handoff: `38a8a95792`

Generated outputs are intentionally ignored through `**/artifacts/`, `m5out`
patterns, `__pycache__`, `doc/`, and `source.sh`.

## Memory Map

| Node | Range | Size | Meaning |
| --- | ---: | ---: | --- |
| 0 | `[0, 3GiB)` | 3GiB | local DDR5 below PCI hole |
| none | `[3GiB, 4GiB)` | 1GiB | x86 PCI/platform hole |
| 0 | `[4GiB, 65GiB)` | 61GiB | local DDR5 above PCI hole |
| 1 | `[65GiB, 129GiB)` | 64GiB | CXL-like memory-only RAM |

Node0 low and node0 high are one logical 8-channel local DDR5 node split only
by the x86 PCI hole. Node1 is memory-only and reachable through two
`CxlMemLink` paths.

## Key Source Files

- `gem5/src/python/gem5/components/boards/large_mem_x86.py`
- `gem5/src/python/gem5/components/memory/tiered.py`
- `gem5/src/python/gem5/components/memory/split_range.py`
- `gem5/src/mem/CxlMemLink.py`
- `gem5/src/mem/cxl_mem_link.hh`
- `gem5/src/mem/cxl_mem_link.cc`
- `gem5/src/arch/x86/bios/ACPI.py`
- `gem5/src/arch/x86/bios/acpi.hh`
- `gem5/src/arch/x86/bios/acpi.cc`

## Architecture Rules

- Every guest-visible RAM range is directly backed by real `AbstractMemory`.
- No `RangeAddrMapper` is used in the current CXL/NUMA path.
- Node0 has 16 direct controllers/directories: 8 for low RAM, 8 for high RAM.
- Node0 low and high use identical 8-way, 64B interleaving.
- Node1 has 2 DDR5 controllers behind 2 `CxlMemLink` objects.
- Total Ruby directories and `MemCtrl` objects: 18.
- All controllers use `DDR5_6400_4x8_32GiB` and 10ns static frontend/backend
  latency.
- Node1 fixed CXL base latency defaults to `0ns`; extra default delay comes
  from flit serialization and queueing.
- `LargeMemoryX86Board` emits E820, SRAT, and SLIT for exactly two nodes.

## Step Index

- `step_00_design_and_usage`: design summary and project constraints.
- `step_02_baseline_fs_config`: stock single-memory KVM-to-Timing baseline.
- `step_04_second_mem_ctrl`: large-memory board and `TwoTierMemory`.
- `step_05_route_ranges_to_ctrls`: Ruby address-range routing validation.
- `step_06_guest_boot_with_two_ranges`: E820 multi-range boot validation.
- `step_08_expose_fast_slow_as_numa_nodes`: ACPI SRAT/SLIT construction.
- `step_09_validate_linux_numa`: Linux NUMA boot validation.
- `step_10_kvm_to_timing_switch`: ROI switch control flow.
- `step_11_microbench_validation`: small NUMA placement microbenchmarks.
- `step_12_bw_latency_curve`: MLC-style bandwidth versus loaded-latency curve.

## Step 12 Current Guidance

Intel MLC is not available in this workspace and the host CPU is AMD EPYC, so
Step 12 uses an in-tree benchmark.

Current defaults:

- 8 guest cores in the generic config.
- `run_16core_curve.sh`: 16 cores, worker step 2.
- `run_32core_curve.sh`: 32 cores, worker step 4.
- `BWL_WORKER_MIB=16`.
- `BWL_LATENCY_MIB=64`.
- `BWL_LATENCY_ITERS=65536`.
- TSC-cycle timing via `rdtsc`; `clock_seconds` is diagnostic only.

Important invalid results:

- Old `clock_gettime()` runs are invalid because the guest fell back to
  `refined-jiffies`, causing 0ms/1ms timing quantization.
- Old 4 MiB latency-buffer zero-worker points are invalid because they mostly
  measured warmed-cache pointer chasing.
- Do not use `clflush` in this TimingSimpleCPU x86 FS path; it triggered a page
  walker assertion.

Expected curve:

- Node0 should have lower unloaded latency and higher sustainable bandwidth.
- Node1 should show higher loaded latency and lower bandwidth when CXL
  serialization/queueing becomes visible.
- CXL flit size, bandwidth, queue depth, and optional base latency should move
  node1 while leaving node0 effectively unchanged.

## Validation Commands

Static checks:

```sh
cd /home/cc/inmem
python3 -m py_compile \
  step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py \
  step_12_bw_latency_curve/scripts/visualize_bwlat.py \
  step_12_bw_latency_curve/scripts/check_bwlat_config.py
```

Step 12 package check after a config-generation run:

```sh
python3 step_12_bw_latency_curve/scripts/check_bwlat_config.py \
  step_12_bw_latency_curve/artifacts/m5out
```

Run the recommended first full curve:

```sh
cd /home/cc/inmem
step_12_bw_latency_curve/scripts/run_16core_curve.sh
```

Run the higher-pressure curve:

```sh
cd /home/cc/inmem
step_12_bw_latency_curve/scripts/run_32core_curve.sh
```

## Known Caveats

- gem5 prints expected DDR capacity mismatch warnings because the DDR5
  interface capacity is larger than assigned interleaved subranges.
- `TwoTierMemory` is a historical name; node0 is now one local memory node, not
  two fast tiers.
- `get_default_memory_ranges()` and `get_numa_memory_ranges()` are
  project-local stdlib hooks.
- `LargeMemoryX86Board` currently supports only the two-node policy used here.
