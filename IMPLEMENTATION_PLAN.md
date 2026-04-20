# Implementation Plan

## Goal

Provide a reproducible gem5 X86 full-system setup for a local DDR5 NUMA node
and a CXL-like memory-only NUMA node, then validate topology, routing, and
bandwidth-versus-loaded-latency behavior.

Build target:

```sh
cd /home/cc/inmem/gem5
scons build/X86/gem5.opt -j$(nproc)
```

Do not use `build/ALL/gem5.opt` for this project.

## Current Architecture

| Node | Range | Meaning |
| --- | ---: | --- |
| 0 | `[0, 3GiB)` | local DDR5 below x86 PCI hole |
| none | `[3GiB, 4GiB)` | PCI/platform hole |
| 0 | `[4GiB, 65GiB)` | same local DDR5 node above the hole |
| 1 | `[65GiB, 129GiB)` | CXL-like memory-only RAM |

Key invariants:

- `LargeMemoryX86Board` owns the large x86 E820/SRAT/SLIT path.
- `TwoTierMemory` owns the fixed node0/node1 memory topology.
- Node0 is one 8-channel local DDR5 node split only by the PCI hole.
- Node1 has two DDR5 channels behind two `CxlMemLink` objects.
- All guest-visible RAM is backed directly by `AbstractMemory`; no
  `RangeAddrMapper` remains in the current design.
- Ruby sees 18 directories and 18 `MemCtrl` objects.
- Default fixed CXL base latency is `0ns`; default node1 delta comes from flit
  serialization and queueing.

## Completed Milestones

1. Baseline x86 FS boot with KVM fast-forward and Timing switch packaged in
   `step_02_baseline_fs_config`.
2. Large-memory board and fixed memory component added in
   `step_04_second_mem_ctrl`.
3. Ruby range-to-controller routing validated in
   `step_05_route_ranges_to_ctrls`.
4. E820 multi-range Linux boot path added in
   `step_06_guest_boot_with_two_ranges`.
5. ACPI SRAT/SLIT NUMA exposure added in
   `step_08_expose_fast_slow_as_numa_nodes`.
6. Linux NUMA boot validation completed in `step_09_validate_linux_numa`.
7. KVM-to-Timing ROI switch packaged in `step_10_kvm_to_timing_switch`.
8. NUMA placement microbenchmarks added in `step_11_microbench_validation`.
9. MLC-style bandwidth/loaded-latency curve added in
   `step_12_bw_latency_curve`.

## CXL Model Boundary

The model intentionally stays abstract:

- Linux sees node1 as ordinary NUMA RAM, not CXL-enumerated device memory.
- No guest driver, DAX, devdax, pmem, or CXL.io management path is modeled.
- CPU-originated memory traffic to node1 crosses `CxlMemLink`.
- The link models flit counts, FIFO queueing, serialization delay, optional
  fixed latency, and per-direction stats.
- Backing media remains gem5 DDR5 unless later experiments require a more
  detailed media model.

Future calibration can tune link bandwidth, queue depth, flit size, optional
base latency, and possibly replace backing media with Ramulator behind the CXL
link. Those are calibration choices, not prerequisites for the current
topology.

## Step 12 Current Plan

Intel MLC is unavailable in this workspace, so Step 12 provides an in-tree
replacement.

Run first:

```sh
cd /home/cc/inmem
step_12_bw_latency_curve/scripts/run_16core_curve.sh
```

If the node0 curve is still rising at the right edge or node1 does not reach
the desired injected bandwidth, run:

```sh
cd /home/cc/inmem
step_12_bw_latency_curve/scripts/run_32core_curve.sh
```

Current benchmark safeguards:

- TSC-cycle timing via `rdtsc`.
- `clock_seconds` printed only as a diagnostic.
- 64 MiB latency buffer to avoid cache-resident zero-worker latency.
- 16 MiB worker buffers.
- Worker-step parsing works when `BWL_CPU_MHZ` is supplied.
- Worker hot loop avoids per-cache-line stop checks.

Rejected approaches:

- Intel MLC: not installed, and host is AMD EPYC.
- `clock_gettime()` timing: invalid in the guest after TSC calibration failure
  and `refined-jiffies` fallback.
- `clflush`: triggered a gem5 x86 TimingSimpleCPU page-walker assertion.

## Validation Requirements

- After gem5 source changes, rebuild `build/X86/gem5.opt`.
- For topology checks, inspect `config.ini`/`config.json` and use the step
  checker scripts.
- For Linux NUMA, validate kernel SRAT/SLIT logs, sysfs node lists, CPU lists,
  and node memory totals.
- For CXL checks, prove link parameters affect node1 and not node0.
- For Step 12, run `check_bwlat_config.py` after config generation and
  `visualize_bwlat.py` after a full run.

## Validation Record

Passed in prior runs:

- gem5 X86 build.
- Step 4 `check_two_tier_config.py`.
- Step 5 `check_route_ranges.py`.
- Step 8 `check_acpi_numa_config.py`.
- Step 9 `check_linux_numa.py`.
- Step 10 `check_kvm_timing_config.py`.
- Step 11 `check_microbench_config.py`.
- Step 11 `check_cxl_latency_model.py`.
- Step 12 host compile smoke.
- Step 12 Python compile smoke.
- Step 12 `check_bwlat_config.py`.

Known invalid historical results:

- early Step 12 `clock_gettime()` runs;
- Step 12 zero-worker latency from 4 MiB latency-buffer runs;
- Step 12 `clflush` run that aborted in the page walker.

## References

- CXL spec markdown: `doc/spec/cxl-spec-v3.2-markdown/index.md`
- CXL spec PDF: `doc/spec/cxl-spec-v3.2.pdf`
