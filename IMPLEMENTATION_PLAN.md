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
- Node1 currently has two DDR5 channels behind two `CxlMemLink` objects, but
  the next topology change is to replace those with one shared CXL bottleneck
  feeding two backing media controllers.
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

## Next Topology Change

Priority: this topology change must be done before the real flit-packing work.
The project should not mix "shared node1 bottleneck" and "real flit packer"
as one implementation step, because that would make validation and debugging
needlessly ambiguous.

The current node1 topology is too generous for both unloaded latency
interpretation and loaded bandwidth scaling because it exposes two independent
`CxlMemLink` objects, one per node1 channel. That behaves like two separate CXL
links:

```text
directory16 -> CxlMemLink0 -> slow_ctrl0
directory17 -> CxlMemLink1 -> slow_ctrl1
```

The intended topology is one shared host-side CXL bottleneck feeding two
backing media controllers:

```text
directory16 \
             -> shared CXL link/queue/serializer -> node1 media fanout -> slow_ctrl0
directory17 /                                                      \-> slow_ctrl1
```

The next implementation should therefore:

1. Replace the two independent node1 `CxlMemLink` objects with one shared CXL
   object for node1 traffic.
2. Preserve two backing DDR5 controllers so node1 media still has internal
   parallelism after the shared host link.
3. Make M2S and S2M queue occupancy and serialization state truly shared across
   all node1 traffic.
4. Keep routing by node1 address range/channel after the shared link so the
   two backing controllers still own disjoint interleaved ranges.

The preferred design is a shared multi-port CXL link or a shared-link-plus-fanout
object, not collapsing node1 to a single backing DDR5 controller.

Expected behavioral change after this topology update:

- node1 loaded bandwidth should drop relative to the current two-link model;
- node1 loaded latency should rise faster under worker pressure;
- node1 worker contention should reflect one shared CXL bottleneck;
- `workers=0` latency will still depend mostly on fixed CXL base latency plus
  one-packet serialization cost, not on queueing.

If unloaded node1 latency is still too close to node0 after the shared-link
change, the model should add explicit fixed CXL base latency calibration
instead of trying to force the gap through contention alone.

## Flit Packing Roadmap

This roadmap starts only after the shared-link topology change above lands.
In other words, the implementation order is:

1. shared node1 CXL bottleneck
2. simple shared-link smoke test
3. real 256B flit packing interactions
4. follow-on protocol/detail work

The reason for this ordering is simple: topology and packing affect the same
benchmark curves, and they need to be separated so each behavioral change can
be attributed cleanly.

Step 2 should stay minimal:

- config generation succeeds
- exactly one node1 CXL bottleneck is present in `config.ini`/`config.json`
- both node1 directory paths traverse that shared object
- one short smoke run boots and reaches the ROI without topology-specific
  failures

Do not require a full Step 12 curve or detailed performance analysis before
starting the real flit-packer work.

The current `CxlMemLink` has moved from whole-256B token charging to 16B
slot-count charging for 256B mode, which is enough to model simple extra-data
cost. It is not enough to model real flit packing interactions.

Minimum required implementation for the next CXL model upgrade:

- separate internal message types for `M2S Req`, `M2S RwD`, `S2M NDR`, and
  `S2M DRS`
- real 256B flit packing
- rollover/spillover across flits

These are the minimum pieces needed if added extra slots are supposed to change
observed latency/bandwidth through packing behavior rather than only through
raw serialized transfer time.

Current state:

- ordinary reads use `M2S Req` outbound and `S2M DRS` inbound
- writes use `M2S RwD` outbound and `S2M NDR` inbound
- extra 16B payload can be represented as an additional serialized slot
- this affects latency, queue occupancy, and bandwidth
- this does not affect slot selection, rollover, or packing efficiency

If the experiment needs additional payload to perturb actual flit utilization,
the next implementation must replace the current slot-count approximation with
an explicit 256B flit packer.

### Scope Freeze

The first real packing implementation should stay narrow:

- 256B flit mode only
- direct-attached Type 3 memory path only
- message classes:
  - `M2S Req`
  - `M2S RwD`
  - `S2M NDR`
  - `S2M DRS`
- no BISnp/BIRsp in the first pass
- no latency-optimized 256B halves in the first pass
- no IDE / CRC / replay correctness model beyond occupancy effects

This scope is enough to make Step 12 traffic observe real packing behavior.

### Stage 1: Message Representation

Add explicit internal message descriptors inside `CxlMemLink`, for example:

- `M2SReq`
- `M2SRwD`
- `S2MNDR`
- `S2MDRS`

Each descriptor should carry:

- message class
- associated gem5 `PacketPtr`
- whether it needs response tracking
- number of required data slots
- whether a trailer is required
- which slot formats are legal
- completion callback / send-ready bookkeeping

This is the minimum abstraction needed before any real packing can happen.

### Stage 2: Per-Direction Flit Packers

Replace the current "units per packet" delay model with one packer per
direction:

- one packer for `M2S`
- one packer for `S2M`

Each packer should:

- accept queued message descriptors
- choose slot formats for the next 256B flit
- account for header slots and implicit data slots
- produce actual emitted flits
- hand back packet completion/send timing when the packet's flits drain

### Stage 3: 256B Packing Rules

Implement only the subset of packing rules needed for the first pass:

- H-slot vs G-slot legality for supported message classes
- one data-header start per non-MDH flit
- implicit 4x16B data slots after a valid data header
- tightly packed rule within the flit
- per-flit message-count limits for the supported message classes
- trailer placement for RwD/DRS only if needed for the chosen experiment

The goal here is not full spec coverage; it is enough fidelity that adding one
extra 16B changes how many flits are emitted and when packets spill across flit
boundaries.

### Stage 4: Rollover and Spillover

Add rollover state so a data-bearing message that does not fit fully in one
flit continues into the next emitted flit with correct timing.

This is the key behavior required for:

- sustained bandwidth realism
- flit-fill efficiency differences
- additional payload bytes changing observed throughput

Without rollover, the packer would still be too approximate for the intended
use.

### Stage 5: Queueing Model Update

Change queueing from "reserved flits per packet" to two layers:

- pending protocol messages waiting for packing
- emitted flits waiting for transmission

This should preserve backpressure behavior while allowing multiple messages to
share a flit and allowing one message to span multiple flits.

### Stage 6: Validation

Before reconnecting this to Step 12, build targeted micro-tests:

1. one-stream 64B reads
2. one-stream 64B writes
3. mixed read/write stream
4. back-to-back DRS-heavy stream
5. same tests with one extra 16B payload slot enabled

For each test, record:

- submitted message count
- emitted flit count
- average slots used per message
- average flit utilization
- latency and achieved bandwidth

The validation target is hand-checkable agreement with the limited subset of
the packing rules from:

- `3.3 CXL.mem`
- `4.3.4 256B Flit Packing Rules`
- `6.2.3.1 256B Flit Format`

### Stage 7: Order of Major Follow-On Work

After the first real flit packer lands:

1. optional fixed base-latency calibration
2. latency-optimized 256B mode if needed
3. BISnp/BIRsp support
4. richer retry / replay behavior
5. QoS telemetry / DevLoad-driven throttling

This ordering keeps topology changes and protocol-packing changes separable.

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

Current interpretation caveat:

- Step 12 zero-worker latency is now protected against cache-resident pointer
  chasing by the 64 MiB latency buffer.
- Step 12 node1 loaded bandwidth is still based on the older two-independent-link
  node1 topology until the shared-link change above lands.

## Validation Requirements

- After gem5 source changes, rebuild `build/X86/gem5.opt`.
- For topology checks, inspect `config.ini`/`config.json` and use the step
  checker scripts.
- For Linux NUMA, validate kernel SRAT/SLIT logs, sysfs node lists, CPU lists,
  and node memory totals.
- For CXL checks, prove link parameters affect node1 and not node0.
- For the shared-link update, prove there is exactly one node1 CXL bottleneck
  object in the config and that both node1 directory paths traverse it.
- For the shared-link update, validate that node1 aggregate bandwidth falls and
  node1 loaded latency rises relative to the current two-link model under the
  same benchmark settings.
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
