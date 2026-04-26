# Step 15: Fake Integrity MAC Timing

Step 15 models the timing impact of an integrity guarantee where every 64B
data cache line has an associated 8B MAC. The MAC contents are fake. This mode
only adds internal memory traffic and gates visible completion so the same guest
image and Step 12 benchmark flow can compare baseline and integrity-enabled
timing.

Baseline behavior is the default. Integrity MAC timing is enabled only with
`--integrity-mac-enable` or by using the Step 15 wrapper script.

## Implemented Model

The implementation adds `IntegrityMemLink`, a host-side pairing layer below the
guest-visible cache hierarchy and above the memory targets. When enabled, each
read or write request in a protected visible range is paired with one internal
MAC request:

- node0 data reads/writes produce one normal node0 data request plus one
  internal node0 MAC request;
- node1 data reads/writes produce one normal node1 data request plus one
  internal node1 MAC request;
- for node1, both requests enter the shared `CxlMemLink`, so CXL request
  queueing, response queueing, serialization, and downstream memory contention
  see two request streams.

Reads complete upstream only after both the data response and the MAC response
have returned. Writes preserve gem5's existing write-ack semantics: the visible
write response is released only after both the data write and MAC write have
been accepted by the normal memory path, not after both writes drain to media.

MAC requests are generated below the CPU cache interface, so they are not CPU
loads/stores, do not allocate in the guest data cache, and do not require guest
TLB or software-visible coherence behavior.

## Current Capacity Approximation

This first implementation is a timing-only model. MAC packets use
`Request::NO_ACCESS` and the data packet's address as a local timing surrogate.
`MemCtrl` was updated so `NO_ACCESS` packets consume the normal controller/DRAM
queue and burst timing path but do not read or write backing bytes.

That means:

- MAC traffic contends with the same node memory model as the data;
- node1 MAC traffic crosses the same shared CXL link as node1 data traffic;
- guest-visible memory contents and cache state are not polluted or corrupted;
- no hidden physical MAC address space is reserved yet;
- Linux-visible E820/SRAT/sysfs memory capacity is unchanged.

If exact hidden-capacity modeling is needed later, add a hidden address mapping
behind the same node controllers. That should still avoid a separate MAC-only
memory device; the hidden MAC range should contend with the same `MemCtrl` and
DRAM objects as normal data.

An 8B MAC request may still consume a full DRAM burst in the current memory
controller model. This is acceptable for the first timing pass, but it is not an
exact 1/8 media-byte model.

## Parameters

The Step 12 config script accepts:

- `--integrity-mac-enable` / `--no-integrity-mac-enable`
- `--integrity-mac-line-bytes=64`
- `--integrity-mac-bytes-per-line=8`

The shell sweep helper accepts matching environment variables:

- `INTEGRITY_MAC_ENABLE=0`
- `INTEGRITY_MAC_LINE_BYTES=64`
- `INTEGRITY_MAC_BYTES_PER_LINE=8`

Do not combine Step 15 with Step 14's `--cxl-extra-data-slots` or
`CXL_EXTRA_DATA_SLOTS`. These are alternative models. The config script rejects
`--integrity-mac-enable` when `--cxl-extra-data-slots` is nonzero.

## Files

gem5:

- `gem5/src/mem/IntegrityMemLink.py`
- `gem5/src/mem/integrity_mem_link.hh`
- `gem5/src/mem/integrity_mem_link.cc`
- `gem5/src/mem/mem_ctrl.cc`
- `gem5/src/python/gem5/components/memory/tiered.py`

Outer repo:

- `step_12_bw_latency_curve/scripts/x86_two_tier_dma_bwlat.py`
- `step_12_bw_latency_curve/scripts/check_dma_bwlat_config.py`
- `step_12_bw_latency_curve/scripts/run_dma_bwlat_parallel.sh`
- `step_15_integrity_mac/scripts/run_integrity_mac_dma_bwlat_parallel.sh`

## Run

Canonical Step 15 sweep wrapper:

```sh
cd /home/cc/inmem
step_15_integrity_mac/scripts/run_integrity_mac_dma_bwlat_parallel.sh
```

Equivalent direct Step 12 helper invocation:

```sh
cd /home/cc/inmem
INTEGRITY_MAC_ENABLE=1 \
CXL_EXTRA_DATA_SLOTS=0 \
OUTDIR=step_15_integrity_mac/artifacts/m5out_dma_integrity_mac_16x4_ddr5_4400_64k \
step_12_bw_latency_curve/scripts/run_dma_bwlat_parallel.sh
```

Single config-generation smoke:

```sh
cd /home/cc/inmem
timeout 25s gem5/build/X86/gem5.opt \
  --outdir=/tmp/inmem_step15_integrity_smoke \
  step_12_bw_latency_curve/scripts/x86_two_tier_dma_bwlat.py \
  --node 1 \
  --dma-total-rate 0 \
  --max-ticks 1 \
  --integrity-mac-enable
```

## Validate

Build:

```sh
cd /home/cc/inmem/gem5
scons build/X86/gem5.opt -j$(nproc)
```

Baseline config check:

```sh
cd /home/cc/inmem
python3 step_12_bw_latency_curve/scripts/check_dma_bwlat_config.py \
  --expected-node 1 \
  --expected-aes-latency-text 0ns \
  --expected-cxl-extra-data-slots 0 \
  --expected-integrity-mac-enable 0 \
  /tmp/inmem_step15_baseline_smoke
```

Integrity config check:

```sh
cd /home/cc/inmem
python3 step_12_bw_latency_curve/scripts/check_dma_bwlat_config.py \
  --expected-node 1 \
  --expected-aes-latency-text 0ns \
  --expected-cxl-extra-data-slots 0 \
  --expected-integrity-mac-enable 1 \
  /tmp/inmem_step15_integrity_smoke
```

The checker verifies the point metadata and expects 36 `IntegrityMemLink`
objects when integrity is enabled: 16 node0-low wrappers, 16 node0-high
wrappers, and 4 node1 wrappers.

## Stats

`IntegrityMemLink` exposes:

- `integrityMacReadReqs`
- `integrityMacWriteReqs`
- `integrityMacReadBytes`
- `integrityMacWriteBytes`
- `integrityMacPairedReads`
- `integrityMacPairedWrites`
- `integrityMacRejectedReqs`

For Step 12 cache-line traffic, MAC bytes should be approximately data bytes
divided by 8 before DRAM burst granularity.

Step 12 `PyTrafficGen` DMA injection also incurs MAC requests in this model.
The plotted DMA bandwidth remains the original data bandwidth unless the
visualizer is explicitly changed to report effective data-plus-MAC pressure.
