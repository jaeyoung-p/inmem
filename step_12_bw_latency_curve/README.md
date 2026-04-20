# Step 12: NUMA Bandwidth vs Loaded Latency

## Purpose

Intel MLC is not installed in this workspace and the host is AMD EPYC, so this
step provides a small in-tree MLC-style benchmark. It measures injected read
bandwidth versus dependent-load latency for guest NUMA memory nodes 0 and 1.

All benchmark threads execute on CPU node 0. Memory allocation is swept between
node 0 and the memory-only CXL-like node 1.

## Expected Shape

- Node0 should have the lowest unloaded latency and higher sustainable
  bandwidth because it is local 8-channel DDR5.
- Node1 should show higher loaded latency and lower sustainable bandwidth when
  CXL flit serialization or queueing becomes visible.
- CXL link bandwidth, flit size, queue depth, and optional base latency should
  move node1 while leaving node0 effectively unchanged.
- `workers=0` reports zero injected bandwidth; compare `latency_ns`.

Do not use old Step 12 results that used:

- `clock_gettime()` timing, because the guest fell back to `refined-jiffies`;
- 4 MiB latency buffers, because zero-worker pointer chasing fit in cache;
- `clflush`, because it triggered a gem5 x86 page-walker assertion.

Current benchmark timing uses gem5 x86 `rdtsc` cycles. `clock_seconds` is only
diagnostic.

## Files

- `scripts/numa_bwlat.c`: pthread benchmark with `mbind`, CPU affinity,
  streaming read workers, and dependent pointer chase.
- `scripts/guest_numa_bwlat.sh`: guest compile/run wrapper.
- `scripts/x86_two_tier_numa_bwlat.py`: KVM boot, Timing ROI, two NUMA nodes.
- `scripts/run_16core_curve.sh`: recommended first full curve.
- `scripts/run_32core_curve.sh`: higher-pressure curve.
- `scripts/check_bwlat_config.py`: packaging/config checker.
- `scripts/visualize_bwlat.py`: CSV/SVG generator from serial `BWL_RESULT`
  lines.

## Defaults

- generic config: 8 guest cores;
- 16-core helper: workers `0,2,4,6,8,10,12,14,15`;
- 32-core helper: workers `0,4,8,12,16,20,24,28,31`;
- `BWL_WORKER_MIB=16`;
- `BWL_LATENCY_MIB=64`;
- `BWL_LATENCY_ITERS=65536`;
- `BWL_CPU_MHZ=3000`.

The 64 MiB latency buffer is intentional. It keeps the zero-worker latency
probe larger than the aggregate Ruby L2 footprint used by the 16-core and
32-core runs.

## Run

Host compile smoke:

```sh
cd /home/cc/inmem
cc -O2 -Wall -Wextra -pthread \
  -o /tmp/numa_bwlat_host_smoke \
  step_12_bw_latency_curve/scripts/numa_bwlat.c
```

Config-generation smoke:

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_12_bw_latency_curve/artifacts/m5out \
  step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py \
  --max-ticks 1
```

Recommended first full run:

```sh
cd /home/cc/inmem
step_12_bw_latency_curve/scripts/run_16core_curve.sh
```

Higher bandwidth-pressure run:

```sh
cd /home/cc/inmem
step_12_bw_latency_curve/scripts/run_32core_curve.sh
```

Useful override example:

```sh
OUTDIR=step_12_bw_latency_curve/artifacts/m5out_16c_trial \
BWL_LATENCY_ITERS=32768 \
TIMEOUT_SECONDS=7200 \
step_12_bw_latency_curve/scripts/run_16core_curve.sh
```

## Validate and Plot

```sh
cd /home/cc/inmem
python3 step_12_bw_latency_curve/scripts/check_bwlat_config.py \
  step_12_bw_latency_curve/artifacts/m5out

python3 step_12_bw_latency_curve/scripts/visualize_bwlat.py \
  step_12_bw_latency_curve/artifacts/m5out
```

The visualizer writes `bw_latency_results.csv` and `bw_latency_results.svg`.

Expected serial rows:

```text
BWL_RESULT node=0 workers=0 ... bandwidth_mib_s=0.000 latency_ns=...
BWL_RESULT node=0 workers=N ... bandwidth_mib_s=... latency_ns=...
BWL_RESULT node=1 workers=0 ... bandwidth_mib_s=0.000 latency_ns=...
BWL_RESULT node=1 workers=N ... bandwidth_mib_s=... latency_ns=...
```
