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
- Node1 has two DDR5 backing channels behind one shared `CxlMemLink`
  bottleneck.
- All guest-visible RAM is backed directly by `AbstractMemory`; no
  `RangeAddrMapper` remains in the current design.
- Ruby sees 18 directories and 18 `MemCtrl` objects.
- Default fixed CXL base latency is `60ns` per direction, in addition to flit
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
10. Node1 topology changed from two independent `CxlMemLink` objects to one
    shared node1 host-side bottleneck feeding two backing media controllers.
11. `CxlMemLink` upgraded to a first-pass 256B flit packer with explicit
    internal `M2S Req`, `M2S RwD`, `S2M NDR`, and `S2M DRS` message classes.
12. Rollover/spillover across flits landed for data-bearing messages.
13. Post-ROI stale-port-event crash fixed by stabilizing `CxlMemLink` port
    object addresses during construction.

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

## Current CXL Status

The major architectural change originally planned here is complete. Node1 now
has one shared multi-port `CxlMemLink` bottleneck in front of two backing DDR5
controllers, and the first-pass 256B packer is live in that shared object.

The current implementation order that actually landed was:

1. shared node1 CXL bottleneck
2. simple shared-link config validation
3. first-pass real 256B flit packing
4. rollover/spillover across flits
5. post-ROI runtime stabilization

The live first-pass packing scope is intentionally narrow:

- 256B flit mode only
- direct-attached Type 3 memory path only
- message classes:
  - `M2S Req`
  - `M2S RwD`
  - `S2M NDR`
  - `S2M DRS`
- no BISnp/BIRsp
- no latency-optimized 256B halves
- no IDE / CRC / replay correctness model beyond occupancy effects

That scope is enough to move the model from packet-level slot charging to real
shared-link flit behavior for Step 12 traffic.

## Remaining CXL Model Work

The remaining work is no longer topology conversion or basic message/flit
representation. It is the narrower follow-on set below.

### Stage 1: Targeted Packer Validation

Before using the first-pass packer for detailed performance claims, add
targeted micro-tests for:

1. one-stream 64B reads
2. one-stream 64B writes
3. mixed read/write stream
4. back-to-back DRS-heavy stream
5. the same tests with one extra 16B payload slot enabled

For each test, record:

- submitted message count
- emitted flit count
- average slots used per message
- average flit utilization
- latency and achieved bandwidth

The validation target is hand-checkable agreement with the limited subset of:

- `3.3 CXL.mem`
- `4.3.4 256B Flit Packing Rules`
- `6.2.3.1 256B Flit Format`

### Stage 2: Packing Fidelity Gaps

The first-pass packer still needs follow-on work in these areas:

- fuller slot-format coverage for supported message classes
- tighter handling of trailer placement/detail for `RwD`/`DRS`
- confirmation of rolling 128B message-count behavior in corner cases
- better standalone tests for mixed header/data packing decisions

### Stage 3: Protocol / Link Detail Work

After the packer validation above is in place:

1. optional fixed base-latency calibration
2. latency-optimized 256B mode if needed
3. BISnp/BIRsp support
4. richer retry / replay behavior
5. QoS telemetry / DevLoad-driven throttling

This ordering keeps calibration, protocol-detail work, and benchmark analysis
separable.

## Step 12 Current Plan

Intel MLC is unavailable in this workspace, so Step 12 provides an in-tree
replacement.

Current Step 12 execution model:

- KVM boot phase, then `TimingSimpleCPU` at the ROI
- Ruby `MESI_Two_Level`
- `L1I=32KiB`, `L1D=32KiB`, shared banked `L2=512KiB`
- one fixed latency core only
- board clock `2.1GHz`
- DMA-side synthetic read injection started at the ROI
- one point per gem5 run

Current measurement boundary:

- Keep: Ruby routing, directory contention, shared `CxlMemLink`, memory
  controllers, and DRAM timing.
- Drop: worker-core cache effects and CPU-worker scheduling effects.
- Measure: one latency core's pointer-chase latency versus controlled injected
  read bandwidth.

Current DMA benchmark structure:

- guest compile/setup runs under KVM
- the latency benchmark allocates and prepares its pointer-chase buffer under
  KVM
- the latency benchmark itself issues `gem5-bridge hypercall 4`
- gem5 switches one core to `TimingSimpleCPU`
- DMA injection starts at the ROI
- only the measured latency loop runs in detailed mode

Canonical frozen Step 12 run:

```sh
cd /home/cc/inmem
DMA_TOTAL_RATES="8GiB/s 16GiB/s 32GiB/s 64GiB/s 128GiB/s 192GiB/s 224GiB/s 256GiB/s" \
DMA_TARGET_PER_INJECTOR="8GiB/s" \
RUBY_DIRECTORY_TBES=4096 \
LATENCY_ITERS=65536 \
OUTDIR=step_12_bw_latency_curve/artifacts/m5out_dma_16x4_ddr5_4400_64k \
step_12_bw_latency_curve/scripts/run_dma_bwlat_parallel.sh
```

Current benchmark safeguards:

- TSC-cycle timing via `rdtsc`.
- 64 MiB latency buffer to avoid cache-resident zero-worker latency.
- DMA injection targets one contiguous range per point.
- node0 DMA injection uses the high local range above the PCI hole.
- offered rate is now an explicit sweep axis; do not infer it from worker
  count.
- Step 12 is frozen to the DMA-only path above. The old serial helper,
  worker-core configs, worker benchmark sources, worker visualizers, and worker
  disk image have been removed. Keep `scripts/numa_latency.c`, because it is
  the benchmark code embedded into the guest and built inside the image for
  each DMA point.

Rejected approaches:

- Intel MLC: not installed, and host is AMD EPYC.
- `clock_gettime()` timing: invalid in the guest after TSC calibration failure
  and `refined-jiffies` fallback.
- `clflush`: triggered a gem5 x86 TimingSimpleCPU page-walker assertion.
- worker-core bandwidth generation: too much simulation cost for the target
  pure memory/CXL curve

Current interpretation caveat:

- Step 12 now measures CPU latency under DMA-injected bandwidth, not under
  additional worker CPU cores.
- Step 12 node1 loaded behavior reflects one shared host-side CXL bottleneck.
- Detailed node1 performance interpretation still depends on the targeted
  packer validation above.
- The canonical validation pass is node1-only with aggregate offered-rate sweep
  `8, 16, 32, 64, 128, 192, 224, 256 GiB/s`.

## Validation Requirements

- After gem5 source changes, rebuild `build/X86/gem5.opt`.
- For topology checks, inspect `config.ini`/`config.json` and use the step
  checker scripts.
- For Linux NUMA, validate kernel SRAT/SLIT logs, sysfs node lists, CPU lists,
  and node memory totals.
- For CXL checks, prove link parameters affect node1 and not node0.
- For the current shared-link design, prove there is exactly one node1 CXL
  bottleneck object in the config and that both node1 directory paths traverse
  it.
- For current CXL runtime validation, a short ROI smoke should boot, switch
  from KVM to O3, and avoid the old immediate post-ROI crash/deadlock.
- For Step 12, run `check_dma_bwlat_config.py` after config generation and
  `visualize_dma_bwlat.py` after a point run or a full sweep.

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
- pre-reset Step 12 worker-core host compile smoke.
- pre-reset Step 12 worker-core Python compile smoke.
- new Step 12 DMA config packaging smoke is complete.
- end-to-end node1 DMA point validation is still pending.
- shared-link config generation showing exactly one `CxlMemLink` and both
  node1 paths traversing it.
- post-fix short ROI smokes that advance beyond the old immediate post-ROI
  crash point.

Known invalid historical results:

- early Step 12 `clock_gettime()` runs;
- Step 12 zero-worker latency from 4 MiB latency-buffer runs;
- Step 12 `clflush` run that aborted in the page walker.

## References

- CXL spec markdown: `doc/spec/cxl-spec-v3.2-markdown/index.md`
- CXL spec PDF: `doc/spec/cxl-spec-v3.2.pdf`
