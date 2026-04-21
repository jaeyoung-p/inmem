# Large-Memory x86 / CXL NUMA Handoff

Last updated: 2026-04-21

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

- outer repo: `204cc9a`
- gem5: `38a8a95792`

## Current Memory Topology

| Node | Range | Meaning |
| --- | ---: | --- |
| 0 | `[0, 3GiB)` | local DDR5 below PCI hole |
| none | `[3GiB, 4GiB)` | x86 PCI/platform hole |
| 0 | `[4GiB, 65GiB)` | same local DDR5 node above the hole |
| 1 | `[65GiB, 129GiB)` | CXL-like memory-only RAM |

Node0 is one logical 8-channel local DDR5 node split only by the PCI hole.

Important current caveat: node1 still uses two independent `CxlMemLink`
objects. The next planned change is to replace that with one shared CXL
bottleneck feeding two backing media controllers.

Another important current caveat: the current `CxlMemLink` timing model now
counts 256B-mode traffic at 16B slot granularity, but it still does not model
real flit packing interactions. Adding one extra 16B transfer to writes or
read returns is achievable in the current model and will affect serialization,
queue occupancy, and bandwidth, but it will not affect H-slot/G-slot packing
choices or flit-fill efficiency.

## Current CXL Calculation

Current implementation references:

- `doc/spec/cxl-spec-v3.2-markdown/index.md`
- `gem5/src/mem/CxlMemLink.py`
- `gem5/src/mem/cxl_mem_link.hh`
- `gem5/src/mem/cxl_mem_link.cc`

The live model is a deliberately abstract `CxlMemLink`, not a full CXL Type 3
device. It models:

- one host-to-device FIFO (`M2S`)
- one device-to-host FIFO (`S2M`)
- 256B-mode slot-count-based serialization for CXL.cachemem payload
- optional fixed per-direction base latency

Current default parameters in the project are:

- `flit_size_bytes = 256`
- `bandwidth = 64GiB/s` per direction
- `m2s_latency = 0ns`
- `s2m_latency = 0ns`
- `request_header_flits = 1`
- `response_header_flits = 1`

The code computes:

```text
256B mode:
  serialization_unit = 16B slot
  data_units(pkt)    = ceil(pkt_size / 16B)

M2S request flits:
  ordinary read  = request_header_flits
  write / RwD    = request_header_flits + data_units(pkt)

S2M response flits:
  read response  = response_header_flits + data_units(pkt)
  write response = response_header_flits

serialization_delay(units) = ceil(units * 16B / link_bandwidth)
```

This matches the CXL 3.2 split between header slots and data slots:

- `M2S Req` is header-only
- `M2S RwD` is one header slot plus data slots
- `S2M DRS` is one header slot plus data slots

For the current Step 12 unloaded pointer-chase read path, the request is an
ordinary 64B cacheline read:

```text
M2S Req units = 1
S2M DRS units = 1 + ceil(64 / 16) = 5
total CXL units per read = 6
```

At `64GiB/s`:

```text
1 unit = 16 B / 64 GiB/s = 0.233 ns
6 units = 1.397 ns
```

So the current unloaded extra node1 latency should be approximately:

```text
delta(node1 - node0) ~= M2S Req serialization + S2M DRS serialization
                     ~= 1 slot + (1 header slot + 4 data slots)
                     ~= 6 slots
                     ~= 1.397 ns
```

For a full 64B write on `M2S RwD`, the request-side serialization is:

```text
M2S RwD units = 1 header slot + 4 data slots = 5
request-side serialization = 80 B / 64 GiB/s = 1.164 ns
```

This slot-based serialization is much smaller than the older whole-256B-token
model. That means large unloaded node1 latency gaps will not come from payload
size alone; they require fixed base latency and/or additional device pipeline
modeling.

Current boundary for "extra 16B" modeling:

- for writes, one additional 16B unit can be charged on `M2S RwD`
- for reads, one additional 16B unit can be charged on `S2M DRS`
- this is achievable cleanly in the current model
- this changes timing only; it does not change actual flit packing behavior

The earlier fixed worker-0 smoke result:

```text
node0 = 82.066 ns
node1 = 94.818 ns
delta = 12.752 ns
```

was collected before this slot-based correction, so that delta should not be
read as the current expected CXL serialization penalty.

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
- physical-link sharing
  - current node1 topology instantiates two independent `CxlMemLink` objects
  - this behaves like two separate physical links and doubles available CXL
    serialization bandwidth for node1
  - the intended next step is one shared bottleneck feeding two backing media
    controllers
- 256B flit payload structure from Sections `4.3.4` and `6.2.3.1`
  - spec flits include headers, CRC, FEC, packing rules, slot formats, and
    message-rate limits per rolling 128B group
  - current model treats traffic as serialized slot units and does not model
    slot packing efficiency, rollover behavior, or protocol-specific message
    placement inside flits
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

Practical consequence: today, unloaded node1 latency is almost entirely the
serialization calculation above, while loaded node1 behavior is dominated by
queueing plus the incorrect two-link topology. If unloaded node1 latency needs
to be materially larger than about one request flit plus one response-with-data
transfer, the model must add explicit fixed CXL base latency or a more detailed
device/link pipeline.

If the project needs extra data bytes to change flit-fill efficiency rather
than only serialized transfer time, `CxlMemLink` must move from the current
slot-count model to an actual 256B flit packer with message descriptors,
slot-format selection, implicit data-slot tracking, and rollover.

Minimum required implementation for that upgrade:

- separate internal message types for:
  - `M2S Req`
  - `M2S RwD`
  - `S2M NDR`
  - `S2M DRS`
- real 256B flit packing
- rollover/spillover across flits

Without those three pieces, an added extra slot only changes serialized timing;
it does not change the bandwidth/latency curve through real CXL packing
interactions.

## Current Step 12 State

Intel MLC is not available in this workspace, so Step 12 uses the in-tree
benchmark.

Current safe defaults:

- TSC-cycle timing via `rdtsc`
- `BWL_WORKER_MIB=16`
- `BWL_LATENCY_MIB=64`
- `BWL_LATENCY_ITERS=65536`

Current helper runs:

- `step_12_bw_latency_curve/scripts/run_16core_curve.sh`
- `step_12_bw_latency_curve/scripts/run_32core_curve.sh`

Known invalid old Step 12 results:

- old `clock_gettime()` runs after guest `refined-jiffies` fallback
- old 4 MiB latency-buffer zero-worker runs
- `clflush`-based runs

## Current Interpretation

- Step 12 zero-worker latency is now protected against cache-resident pointer
  chasing by the 64 MiB latency buffer.
- Step 12 node1 loaded bandwidth is still affected by the older two-link node1
  topology until the shared-link change lands.
- Extra 16B payload accounting is feasible in the current `CxlMemLink`, but it
  will not create real packing interactions until the flit-packer work lands.
- If unloaded node1 latency still looks too close to node0 after the shared-link
  change, the next lever is explicit fixed CXL base-latency calibration.

## Current Caveats

- gem5 prints expected DDR capacity mismatch warnings because the DDR5
  interface capacity is larger than assigned interleaved subranges.
- `TwoTierMemory` is a historical name; node0 is now one local memory node.
- `LargeMemoryX86Board` currently supports only the two-node policy used here.
