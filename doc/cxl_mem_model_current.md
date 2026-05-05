# Current CXL.mem Model for a Two-Tier NUMA gem5 Platform

## Abstract

This document describes the current CXL.mem implementation used in the
`/home/cc/inmem` project. The model targets a full-system gem5 X86 platform
with two guest-visible NUMA nodes: a local DDR5 node and a remote
CXL-like memory-only node. The implementation is intentionally not a full
CXL Type 3 device model. Instead, it provides a shared host-side CXL.mem
bottleneck with first-pass 256 B flit packing, per-direction queueing, and
serialization delay, while preserving ordinary Linux NUMA RAM semantics in
the guest. This writeup is intended as a shareable implementation note in a
paper style suitable for architecture venues such as ISCA, MICRO, or HPCA.

## 1. Design Objective

The goal of the current model is to study bandwidth-versus-loaded-latency
behavior for a two-tier memory system in gem5 without exposing a guest-visible
CXL software stack. Concretely, the implementation aims to capture three
effects that matter for a remote memory NUMA node:

1. one shared host-side CXL.mem bottleneck across all node1 traffic,
2. flit-level queueing and serialization delay rather than packet-level delay,
3. first-pass packing effects for the CXL.mem message classes exercised by the
   current benchmark path.

The model does not attempt to represent device enumeration, DVSEC/HDM
programming, mailbox behavior, guest drivers, DAX/devdax/pmem semantics, or a
complete CXL.io path. Linux therefore sees the remote tier as ordinary NUMA
RAM.

## 2. System Context

### 2.1 Guest-visible memory map

The current platform exposes the following fixed address layout:

| Node | Address range | Meaning |
| --- | --- | --- |
| 0 | `[0, 3 GiB)` | local DDR5 below the x86 PCI hole |
| none | `[3 GiB, 4 GiB)` | x86 PCI/platform hole |
| 0 | `[4 GiB, 65 GiB)` | local DDR5 above the hole |
| 1 | `[65 GiB, 129 GiB)` | remote CXL-like memory-only node |

Node0 is one logical local NUMA node split only because x86 reserves the
`[3 GiB, 4 GiB)` hole. Node1 is a 64 GiB high-address memory-only NUMA node.

### 2.2 Physical organization

The memory system is implemented in
[`tiered.py`](/home/cc/inmem/gem5/src/python/gem5/components/memory/tiered.py).
Node0 represents 8 logical 64-bit DDR5-4400 channels. Because gem5's
`DDR5_4400_4x8` model is a 32-bit DDR5 subchannel, each node0 range is backed
by 16 x32 `MemCtrl` objects. The low and high node0 address ranges therefore
have separate 16-way-interleaved controller groups, both using the same DDR5
timing parameters and 64 B interleaving granularity. Node1 represents 2
logical 64-bit DDR5-4400 channels, modeled as 4 x32 backing controllers behind
one shared `CxlMemLink` object:

```text
Ruby directories for node1
        |
        v
shared CxlMemLink
   |       |       |       |
   v       v       v       v
slow0   slow1   slow2   slow3
```

This organization makes all host-to-node1 traffic contend for one shared
link-level queueing and serialization resource while preserving two-way media
parallelism behind the host bottleneck.

## 3. Modeling Boundary

The current implementation intentionally models a narrow subset of CXL:

- only CXL.mem traffic is modeled;
- node1 is direct-attached Type 3-style memory from the host perspective;
- the guest sees ordinary NUMA memory rather than an enumerated CXL device;
- the model supports only 256 B flit mode;
- the supported internal message classes are `M2S Req`, `M2S RwD`,
  `S2M NDR`, and `S2M DRS`;
- BISnp/BIRsp, latency-optimized 256 B flits, CRC/FEC/replay correctness,
  and QoS telemetry are not implemented.

This boundary was chosen to match the current benchmark path, which issues
ordinary cache-line reads and writes through Ruby and does not require guest
software-visible CXL management.

## 4. CxlMemLink Structure

The link implementation lives in:

- [`CxlMemLink.py`](/home/cc/inmem/gem5/src/mem/CxlMemLink.py)
- [`cxl_mem_link.hh`](/home/cc/inmem/gem5/src/mem/cxl_mem_link.hh)
- [`cxl_mem_link.cc`](/home/cc/inmem/gem5/src/mem/cxl_mem_link.cc)

The `CxlMemLink` object is a `ClockedObject` with matched vectors of:

- `cpu_side_ports`: response ports that accept host-originated requests and
  later return responses,
- `mem_side_ports`: request ports that forward accepted traffic to backing
  memory controllers and receive their responses.

Each CPU-side port is associated with one forwarded address range. For node1,
these ranges correspond to the four interleaved x32 backing-controller ranges.
The shared object therefore preserves controller ownership by address while
sharing one link model across all node1 ranges.

Internally, the object maintains one state machine per direction:

- `m2sState` for host-to-device traffic,
- `s2mState` for device-to-host traffic.

Each direction tracks:

- queue depth in flits,
- current queued occupancy in flits,
- the next available emission tick,
- a deque of pending protocol messages,
- one optional active data-bearing message being continued across flits,
- one event that emits the next flit.

## 5. Message Representation

The current packer uses explicit internal message descriptors
(`ProtocolMessage`) rather than charging delay directly from the gem5 packet.
Each descriptor contains:

- message class,
- associated `PacketPtr`,
- ingress/egress port identifier,
- message arrival tick,
- total data slots,
- total trailer slots,
- total reserved flits,
- bookkeeping for header transmission,
- emitted flit count,
- transmitted data/trailer slots,
- service start tick and completion tick.

The implemented message-class mapping is:

- host read request -> `M2S Req`,
- host write request -> `M2S RwD`,
- response without data -> `S2M NDR`,
- response with data -> `S2M DRS`.

This explicit representation is the key step that moved the model from a
packet-level serializer to a flit-level packer.

## 6. Timing and Resource Model

### 6.1 Directional bandwidth and base latency

The project topology passes the following default parameters to the link:

- flit size: 256 B,
- per-direction bandwidth: 64 GiB/s by default,
- fixed `M2S` base latency: 60 ns by default,
- fixed `S2M` base latency: 60 ns by default,
- per-direction queue depth: 256 flits by default.

The underlying `CxlMemLink` SimObject declares `0ns` as its standalone
parameter default for `m2s_latency` and `s2m_latency`; the project-local
`TwoTierMemory` and Step scripts override both directions to `60ns`.

Serialization delay is computed at flit granularity:

```text
serialization_delay(flits) = ceil(flits * flit_size_bytes / bandwidth)
```

With the default parameters, one 256 B flit takes:

```text
256 B / 64 GiB/s = 3.725 ns
```

### 6.2 Queueing semantics

Queue capacity is enforced in units of emitted flits, not packets. A message
is admitted only if its reserved flit count fits within the corresponding
directional queue depth.

The `M2S` side additionally reserves expected `S2M` response capacity at
request-admission time. This couples forward and reverse backpressure and
prevents a request from entering the link when the eventual response could not
be accommodated. In effect, the model approximates a bounded outstanding
response resource without implementing a full spec credit/replay protocol.

### 6.3 Delay accounting

When a message completes transmission through the packer, the link computes:

- queue wait = first flit start - message arrival,
- serialization = completion tick - first flit start,
- total ready time = completion tick + fixed directional base latency.

The gem5 packet is then released toward the next component at the computed
ready tick. The model records queue wait, serialization, total delay, queue
occupancy, and full-queue events as gem5 statistics.

## 7. First-Pass 256 B Flit Packer

### 7.1 Basic model

The packer emits one 256 B protocol flit at a time. Each flit contains 15
logical packing slots after accounting for the flit header. The implementation
treats:

- slot 0 as the header-position-constrained slot,
- slots 1-14 as follow-on positions that may carry either headers or
  continuation data, subject to the simplified packing rules below.

Data-bearing messages (`M2S RwD`, `S2M DRS`) carry a header plus implicit data
slots. Header-only messages (`M2S Req`, `S2M NDR`) complete as soon as their
header is packed into a flit.

### 7.2 Data-slot accounting

The model uses 16 B chunks as the internal data-slot unit:

```text
data_slots(pkt) = max(1, ceil(pkt_size / 16 B))
```

Thus, a 64 B line transfer occupies 4 data slots. Masked writes may carry one
additional trailer slot in the current first-pass implementation.

### 7.3 Reserved-flit estimate

Admission control requires a conservative estimate of how many flits a message
might consume. The current estimate is:

- non-data-bearing message -> 1 flit,
- data-bearing message with at most 14 follow-on slots -> 1 flit,
- otherwise:

```text
reserved_flits = 1 + ceil((follow_slots - 14) / 14)
```

The first flit can hold one data header plus up to 14 follow-on slots
after the header position. Each subsequent flit contributes 14 continuation
positions because slot 0 cannot be used for continuation data.

This estimate is intentionally simple: it is tight for the supported message
classes but does not attempt full slot-format optimality.

### 7.4 Supported packing rules

The current implementation enforces a narrow subset of the 256 B packing rules
needed for the active benchmark path:

- one active data-header start per emitted flit,
- continuation of an already-started data-bearing message uses slots 1-14 of
  subsequent flits,
- slot 0 is never used to continue an already-active data message,
- a data header may be started in slot 0 only when the remaining data plus
  trailer demand is at most 16 follow-on slots,
- header-only messages may be packed alongside others as long as simplified
  per-group message-count limits are respected,
- data-bearing messages roll over into subsequent flits until all data and
  trailer slots are consumed.

### 7.5 Group-based message-count limits

The implementation tracks simplified rolling group counts using four slot
groups: slots 0-3, 4-7, 8-11, and 12-14. The current per-group limits are:

- `M2S Req`: 4
- `M2S RwD` header: 2
- `S2M NDR`: 6
- `S2M DRS` header: 3

These limits are used to block illegal over-packing and to approximate the
rolling 128 B constraints relevant to the supported subset. They are not yet a
complete implementation of all packing corner cases from the CXL 3.2 text.

### 7.6 Direction-specific behavior

For `M2S`:

- ordinary reads become header-only `M2S Req` messages,
- writes become `M2S RwD` messages with data slots and optional trailer.

For `S2M`:

- responses with data become `S2M DRS`,
- responses without data become `S2M NDR`,
- multiple `S2M NDR` headers can be packed into one slot according to the
  current slot-capacity approximation,
- data-bearing responses use the same rollover mechanism as writes.

## 8. Forward Progress and Port Integration

The link integrates with gem5 timing ports through per-port deferred-send
queues. A packet is not sent immediately upon message completion; instead, the
link schedules a port-local send event at the computed ready tick.

Two implementation details are important for reproducibility:

1. The deferred-send path now tolerates an event firing before the packet's
   target send tick by simply returning and waiting until the tick is mature.
2. The vectors of CPU-side and mem-side ports are explicitly reserved before
   `emplace_back()` construction so that event lambdas capturing `this` do not
   become stale after `std::vector` reallocation.

The second point was not just a cleanup. During post-ROI debugging, `gdb`
showed that the first node1 read after the KVM-to-Timing switch could reach
the `CxlMemLink`, be serialized into an `M2S` flit, and then crash when the
queued mem-side send event fired on a moved `CxlRequestPort` object. The fix
was committed in gem5 as `01143e5842`.

## 9. Validation Status

The current implementation has been validated at three levels.

### 9.1 Build and configuration

- `build/X86/gem5.opt` builds cleanly.
- Step 12 config generation succeeds.
- `check_bwlat_config.py` passes on the standard config-generation smoke.

### 9.2 Topology validation

Generated configurations show:

- exactly one `CxlMemLink` object,
- both node1 Ruby directory paths traverse that shared object,
- both node1 backing controllers remain present behind the shared link.

### 9.3 Runtime validation

Short full-system smokes boot under KVM, switch to Timing at the Step 12 ROI,
and advance beyond the old immediate post-ROI failure point. The previously
observed stale-port-event crash has therefore been addressed. However, the
current validation should still be described as partial rather than final:
the first-pass packer does not yet have the dedicated micro-tests needed for
strong flit-accounting claims.

## 10. Limitations

The current model still omits several pieces that would be required for a more
complete CXL study:

- full slot-format coverage for all supported messages,
- complete trailer semantics for all corner cases,
- latency-optimized 256 B half-flit behavior,
- BISnp/BIRsp traffic,
- unified retry-buffer and replay correctness behavior,
- CRC/FEC effects,
- DevLoad/QoS telemetry and host throttling,
- guest-visible CXL enumeration and software management.

Accordingly, the current implementation should be characterized as a
first-pass shared-link CXL.mem timing model with explicit 256 B flit packing,
not a complete protocol-accurate CXL 3.2 device model.

## 11. Summary

The current implementation replaces an earlier packet-level approximation with
a more realistic, but still intentionally scoped, CXL.mem timing model. The
main contributions of the live code are:

- one shared host-side CXL bottleneck for the remote NUMA tier,
- explicit internal `M2S`/`S2M` message typing,
- flit-level queueing and serialization,
- rollover of data-bearing messages across flits,
- coupled reverse-path reservation for responses,
- integration into a Linux-visible ordinary NUMA memory system in gem5.

For the current project, this is the right abstraction level: it captures the
host-visible contention and first-order packing behavior needed for Step 12
without expanding into a full guest-visible CXL software stack.
