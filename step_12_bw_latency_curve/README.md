# Step 12: DMA-Injected Bandwidth vs Latency

## Purpose

Intel MLC is not available in this workspace and the host is AMD EPYC. Step 12
therefore uses an in-tree replacement built around:

- one guest latency probe core;
- DMA-side synthetic read injection;
- the existing node0/node1 Ruby/CXL/memory path.

The goal is a cleaner bandwidth-versus-latency curve than the older
worker-core design. Injected traffic no longer depends on adding many O3 cores.

## Model

- KVM boot phase, then `TimingSimpleCPU` at the ROI.
- Ruby `MESI_Two_Level`.
- `L1I=32KiB`, `L1D=32KiB`, shared banked `L2=512KiB`.
- board clock `2.1GHz`.
- one guest-dependent pointer-chase latency probe using `rdtsc`.
- host-side `PyTrafficGen` DMA injectors started at the ROI.
- the latency benchmark allocates and prepares its working set under KVM, then
  requests the ROI switch itself so only the measured loop runs in detailed
  mode.

The DMA injectors preserve:

- Ruby routing;
- directory contention;
- node0/node1 address selection;
- the shared node1 `CxlMemLink`;
- memory-controller and DRAM service behavior.

They intentionally do not model worker-core cache effects or CPU execution
interference.

## DDR5 Channel Convention

The experiment describes node bandwidth in logical 64-bit DDR5 channels.
gem5's `DDR5_4400_4x8` model is one 32-bit DDR5 subchannel, so the configured
topology intentionally uses twice as many gem5 DDR5 interfaces as logical
channels:

- node0: 8 logical 64-bit DDR5-4400 channels, modeled as 16 x32 subchannels;
- node1: 2 logical 64-bit DDR5-4400 channels, modeled as 4 x32 subchannels
  behind the shared `CxlMemLink`.

The intended saturation regions for Step 12 are therefore approximately
218 GB/s on node0 and 52 GB/s on node1. A generated config for this topology
should contain 36 `MemCtrl` and 36 `DRAMInterface` objects: 16 node0 low-range
controllers, 16 node0 high-range controllers, and 4 node1 controllers.

## Files

- `scripts/numa_latency.c`: guest latency-only benchmark.
- `scripts/guest_dma_bwlat.sh`: guest compile/run wrapper.
- `scripts/x86_two_tier_dma_bwlat.py`: FS config, ROI switch, DMA injector start.
- `scripts/check_dma_bwlat_config.py`: config/readfile checker for one point.
- `scripts/run_dma_bwlat_parallel.sh`: canonical frozen Step 12 sweep helper.
- `scripts/visualize_dma_bwlat.py`: aggregate CSV/PNG writer.

## Defaults

- target node selected per point with `--node {0,1}`;
- `LATENCY_MIB=64`;
- `--latency-iters=65536` in the Python config;
- `LATENCY_ITERS=65536` in the shell sweep helper unless overridden;
- `CPU_MHZ=2100`;
- aggregate sweep mode using `DMA_TOTAL_RATES`;
- helper `DMA_TOTAL_RATES="8GiB/s 16GiB/s 32GiB/s 64GiB/s 128GiB/s 192GiB/s 224GiB/s 256GiB/s"`;
- `DMA_TARGET_PER_INJECTOR=8GiB/s`;
- `DMA_BLOCK_SIZE=256`;
- `DMA_MAX_OUTSTANDING=2048`;
- `DMA_DURATION=1s`;
- `RUBY_DIRECTORY_TBES=4096`;
- default `OUTDIR=step_12_bw_latency_curve/artifacts/m5out_dma_16x4_ddr5_4400_64k`.

Node0 DMA injection uses the large local high range `[4GiB, 65GiB)` so the
injector sees one contiguous local-DDR5 span and does not need to span the x86
PCI hole.

`--dma-total-rate` is the Step 12 rate knob and means aggregate offered DMA
read rate across all injectors. The config automatically chooses enough
injectors from `--dma-target-per-injector` unless `--dma-injectors` is
explicitly set. The user-facing DMA block size is 256B for metadata and
address-range splitting, but the actual `PyTrafficGen` request size is clamped
to 64B cache-line requests while keeping the same offered byte rate.

## Run

Config-generation smoke:

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_12_bw_latency_curve/artifacts/m5out_dma_smoke \
  step_12_bw_latency_curve/scripts/x86_two_tier_dma_bwlat.py \
  --node 1 \
  --dma-total-rate 0 \
  --max-ticks 1
```

One unloaded node1 point:

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_12_bw_latency_curve/artifacts/m5out_dma_point \
  step_12_bw_latency_curve/scripts/x86_two_tier_dma_bwlat.py \
  --node 1 \
  --dma-total-rate 0
```

One loaded node1 point:

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_12_bw_latency_curve/artifacts/m5out_dma_point \
  step_12_bw_latency_curve/scripts/x86_two_tier_dma_bwlat.py \
  --node 1 \
  --dma-total-rate 48GiB/s \
  --dma-target-per-injector 8GiB/s \
  --ruby-directory-tbes 4096
```

Canonical frozen sweep:

```sh
cd /home/cc/inmem
DMA_TOTAL_RATES="8GiB/s 16GiB/s 32GiB/s 64GiB/s 128GiB/s 192GiB/s 224GiB/s 256GiB/s" \
DMA_TARGET_PER_INJECTOR="8GiB/s" \
RUBY_DIRECTORY_TBES=4096 \
LATENCY_ITERS=65536 \
OUTDIR=step_12_bw_latency_curve/artifacts/m5out_dma_16x4_ddr5_4400_64k \
step_12_bw_latency_curve/scripts/run_dma_bwlat_parallel.sh
```

## Validate and Plot

Single-point checker:

```sh
cd /home/cc/inmem
python3 step_12_bw_latency_curve/scripts/check_dma_bwlat_config.py \
  --expected-node 1 \
  --min-dma-injectors 1 \
  step_12_bw_latency_curve/artifacts/m5out_dma_point
```

Aggregate CSV/PNG:

```sh
cd /home/cc/inmem
python3 step_12_bw_latency_curve/scripts/visualize_dma_bwlat.py \
  step_12_bw_latency_curve/artifacts/m5out_dma_bwlat
```

The visualizer writes:

- `dma_bwlat_results.csv`
- `dma_bwlat_results.png`, plotting achieved injected DMA read bandwidth
  versus latency

Each CSV row includes:

- target node;
- aggregate offered DMA read rate;
- achieved injected DMA read bandwidth from DMA stats;
- per-injector offered DMA read rate;
- injector count;
- measured latency.
