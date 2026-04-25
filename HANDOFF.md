# Large-Memory x86 / CXL NUMA Handoff

Last updated: 2026-04-25

This file is the current-status document. For repository structure and working
rules, read `AGENTS.md`. For the roadmap and planned technical changes, read
`IMPLEMENTATION_PLAN.md`.

## Current State

The live model is:

```text
x86 sparse RAM map -> local node0 DDR5 -> CXL-like memory-only node1 -> Linux NUMA
```

Current repositories:

- outer repo: `git@github.com:jaeyoung-p/inmem.git`
- gem5 submodule/fork: `git@github.com:jaeyoung-p/gem5_25.1.0.0.git`

Recent commits:

- outer repo: `1bf2826`
- gem5: `01143e5842`

## Current Memory Topology

| Node | Range | Meaning |
| --- | ---: | --- |
| 0 | `[0, 3GiB)` | local DDR5 below PCI hole |
| none | `[3GiB, 4GiB)` | x86 PCI/platform hole |
| 0 | `[4GiB, 65GiB)` | same local DDR5 node above the hole |
| 1 | `[65GiB, 129GiB)` | CXL-like memory-only RAM |

Node0 is one logical 8-channel local DDR5 node split only by the PCI hole.
In this project, that "8-channel" statement means eight logical 64-bit DDR5
channels. gem5's `DDR5_4400_4x8` interface models one 32-bit DDR5 subchannel,
so node0 is represented as sixteen x32 subchannels. Because node0 has separate
below-hole and above-hole memory objects for KVM-safe sparse RAM backing, the
generated config contains sixteen low-range controllers plus sixteen
high-range controllers, but each node0 address range is still 16-way
interleaved.

Node1 now uses one shared `CxlMemLink` object as the host-side CXL.mem
bottleneck feeding four backing `DDR5_4400_4x8` x32 subchannels. This
represents two logical 64-bit DDR5 channels for the CXL-like memory node. All
node1 directory paths traverse that shared link, so M2S/S2M queueing and
serialization are truly shared across all node1 traffic.

Current Step 12 bandwidth target convention:

- node0 should behave like 8x DDR5-4400 logical 64-bit channels, with the
  intended observed saturation region around 218 GB/s;
- node1 should behave like 2x DDR5-4400 logical 64-bit channels behind the
  shared CXL.mem link, with the intended observed saturation region around
  52 GB/s;
- do not "simplify" the topology back to 8 and 2 `DDR5_4400_4x8` objects,
  because that models only half the intended 64-bit-channel width.

## Current CXL Calculation

Current implementation references:

- `doc/spec/cxl-spec-v3.2-markdown/index.md`
- `gem5/src/mem/CxlMemLink.py`
- `gem5/src/mem/cxl_mem_link.hh`
- `gem5/src/mem/cxl_mem_link.cc`

The live model is a deliberately abstract `CxlMemLink`, not a full CXL Type 3
device. It now models:

- one shared host-to-device FIFO (`M2S`) across all node1 traffic
- one shared device-to-host FIFO (`S2M`) across all node1 traffic
- explicit internal message classes for:
  - `M2S Req`
  - `M2S RwD`
  - `S2M NDR`
  - `S2M DRS`
- first-pass real 256B flit packing
- rollover/spillover of data-bearing messages across flits
- optional fixed per-direction base latency

Current default parameters in the project are:

- `flit_size_bytes = 256`
- `bandwidth = 64GiB/s` per direction
- `m2s_latency = 60ns`
- `s2m_latency = 60ns`
- `request_header_flits = 1`
- `response_header_flits = 1`

The older slot-count-only calculation in this file is now obsolete. The live
code no longer computes packet delay as a simple count of serialized 16B
units; it builds actual 256B flits, tracks which message headers and implicit
data slots fit in each emitted flit, and carries partially sent RwD/DRS
messages across subsequent flits.

Practical consequence: added payload bytes can now change not only raw
serialized transfer time but also flit count, rollover behavior, queue
occupancy, and packing efficiency. The model is still intentionally first-pass
and does not yet claim full spec-accurate packing coverage.

## Current CXL Missing Pieces

Compared with the CXL 3.2 material indexed in
`doc/spec/cxl-spec-v3.2-markdown/index.md`, the current model is intentionally
incomplete.

Relevant spec areas:

- `3.3 CXL.mem`
- `3.3.2 CXL.mem Channel Description`
- `3.3.4 QoS Telemetry for Memory`
- `4.3.4 256B Flit Packing Rules`
- `6.2.3.1 256B Flit Format`
- `6.3 256B Flit Mode Retry Buffers`
- `14.3.6.1.5 Egress Port Backpressure Test`

What the current model does not represent:

- full CXL.mem channel set from Section `3.3.2`
  - spec defines multiple independent CXL.mem channels
  - current gem5 object collapses traffic into one `M2S` FIFO and one `S2M`
    FIFO, with no BISnp/BIRsp behavior
- 256B flit payload structure from Sections `4.3.4` and `6.2.3.1`
  - the current model now has first-pass real 256B packing and rollover
  - it still does not cover the full slot-format space, full trailer detail,
    or every message-rate corner case from the spec
- latency-optimized 256B flit halves from Section `6.2.3.1.2`
  - current model has no half-flit timing distinction
- unified retry-buffer / replay behavior from Section `6.3`
  - current model has FIFO capacity and retry at the gem5 port boundary, but
    not spec-level retry buffers, replay, CRC/FEC handling, or credit return
- QoS telemetry from Section `3.3.4`
  - no `DevLoad` indication
  - no host-side throttling loop
  - no modeled egress-port-congestion reporting or temporary-throughput
    reduction behavior
- device-management / enumeration aspects
  - no CXL.io enumeration, DVSEC, HDM decoder programming, mailbox, or FM/API
    model
  - node1 remains ordinary Linux NUMA RAM from the guest point of view

Practical consequence: node1 loaded behavior now reflects one shared host-side
CXL bottleneck plus first-pass flit packing. The remaining fidelity gap is no
longer "two links vs one link" or "slot counts vs flits"; it is the narrower
set of unsupported protocol details and the lack of targeted packing
micro-validation/calibration.

## Current Step 12 State

Intel MLC is not available in this workspace, so Step 12 uses the in-tree
benchmark.

Current safe defaults:

- TSC-cycle timing via `rdtsc`
- KVM fast-forward, then `TimingSimpleCPU` at the ROI
- Ruby `MESI_Two_Level` cache hierarchy
- `L1I=32KiB`, `L1D=32KiB`, shared banked `L2=512KiB`
- board clock `2.1GHz`
- `LATENCY_MIB=64`
- `LATENCY_ITERS=65536` in the shell helper unless overridden
- `CPU_MHZ=2100`
- aggregate DMA sweep mode via `DMA_TOTAL_RATES`
- `DMA_TARGET_PER_INJECTOR=8GiB/s`
- `DMA_BLOCK_SIZE=256`
- `DMA_MAX_OUTSTANDING=2048`
- `DMA_DURATION=1s`
- `RUBY_DIRECTORY_TBES=4096`
- node1-first aggregate offered-rate sweep
  `8, 16, 32, 64, 128, 192, 224, 256 GiB/s`
- default output directory
  `step_12_bw_latency_curve/artifacts/m5out_dma_16x4_ddr5_4400_64k`

The user-facing DMA block size is 256B for range splitting and metadata.
`PyTrafficGen` still emits legal 64B cache-line requests internally because
`BaseTrafficGen` rejects block sizes larger than the system cache line. The
offered byte rate is preserved by adjusting the request period.

Canonical helper run:

- `step_12_bw_latency_curve/scripts/run_dma_bwlat_parallel.sh`

Step 12 has been intentionally cleaned up to this DMA-only path. The old
serial sweep helper, worker-core configs, worker visualizers, worker benchmark
sources, and worker disk image were removed. The benchmark source that must
remain is `step_12_bw_latency_curve/scripts/numa_latency.c`; it is embedded
into the guest readfile and built inside the guest for each point.

Known invalid old Step 12 results:

- old `clock_gettime()` runs after guest `refined-jiffies` fallback
- old worker-core loaded-latency runs
- `clflush`-based runs from the older TimingSimpleCPU path

## Current Interpretation

- Step 12 now measures one latency probe core under DMA-injected read
  bandwidth, not under additional worker CPU cores.
- The DMA injectors preserve Ruby, directories, the shared node1 `CxlMemLink`,
  memory controllers, and DRAM service behavior.
- The DMA injectors intentionally do not model worker-core cache interaction.
- The latency benchmark now enters ROI itself after pointer-chase setup, so
  setup/placement work stays under KVM and only the measured loop plus active
  injection run in detailed mode.
- If unloaded node1 latency still looks too close to node0, the next lever is
  explicit fixed CXL base-latency calibration.

## Current Validation Status

- incremental `build/X86/gem5.opt` builds cleanly
- after the 16x4 DDR5_4400 subchannel update, a Step 12 config-generation
  smoke produced:
  - `36` `MemCtrl` objects
  - `36` `DRAMInterface` objects
  - exactly one `CxlMemLink`
  - four node1 CXL-side memory ports/ranges
- `step_12_bw_latency_curve/scripts/check_dma_bwlat_config.py` passed on that
  generated config with `--expected-node 1 --min-dma-injectors 4`
- Step 12 was hard-reset to the DMA-injected design described above
- Step 12 currently switches from KVM fast-forward cores to `TimingSimpleCPU` at the ROI
- Step 12 DMA config packaging smoke passed for the current `MESI_Two_Level`
  one-core path
- the old post-ROI failure was traced with `gdb` to stale `CxlMemLink` port
  event callbacks after `std::vector` reallocation; that fix is pushed in gem5
  commit `01143e5842`

What remains open is narrower than before:

- the canonical full sweep should be rerun after topology/protocol changes
  using `step_12_bw_latency_curve/scripts/run_dma_bwlat_parallel.sh`

## Current Caveats

- gem5 prints expected DDR capacity mismatch warnings because the DDR5
  interface capacity is larger than assigned interleaved subranges.
- `TwoTierMemory` is a historical name; node0 is now one local memory node.
- `LargeMemoryX86Board` currently supports only the two-node policy used here.
