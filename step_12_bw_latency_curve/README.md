# Step 12: NUMA Bandwidth vs Loaded Latency Curve

## Goal

Intel MLC is not available in the current workspace, and the host is an AMD
EPYC system. This step adds an in-tree replacement for the specific MLC-style
measurement needed here: bandwidth versus loaded latency for each guest NUMA
memory node.

The benchmark runs on CPUs attached to NUMA node `0` and allocates memory on
node `0` or node `1`. For each memory node it sweeps background worker count
from `0` to `N`. One thread measures dependent pointer-chase latency while the
worker threads stream reads from buffers allocated on the same target memory
node. Each point reports injected read bandwidth and loaded latency.

## Expected Results

The expected qualitative shape is different for the two memory nodes because
all CPUs execute from node `0`, while node `1` is a memory-only CXL-like node.

For node `0`:

- `workers=0` measures unloaded local DDR5 pointer-chase latency from a node `0`
  CPU to node `0` memory. This should be the lowest latency curve point.
- As background workers increase, injected bandwidth should rise until the
  local node0 DDR5 channels, Ruby path, or CPU-side request generation saturates.
- Loaded latency should increase gradually as the workers compete with the
  pointer-chase thread for cache, Ruby, and memory-controller resources.
- Node `0` should provide the higher sustainable bandwidth curve because it has
  eight local DDR5 channels and no CXL link in the timing path.
- Changing CXL link knobs such as flit size, CXL bandwidth, queue depth, or
  optional fixed CXL base latency should not materially move the node `0` curve.

For node `1`:

- `workers=0` measures unloaded access to the CXL-like memory-only node. It
  should be higher latency than node `0` once CXL serialization, queueing, or
  any explicit base latency is large enough to be visible.
- As background workers increase, bandwidth should initially rise, then flatten
  earlier than node `0` if the two CXL links become the bottleneck.
- Loaded latency should rise more sharply than node `0` under worker pressure
  because the latency probe and bandwidth workers share the CXL request and
  response queues before reaching the backing DDR5 media.
- Node `1` should show lower sustainable bandwidth than node `0` when the CXL
  link model is bandwidth-limiting relative to the eight-channel local node.
- CXL parameter sweeps should affect node `1`: lower link bandwidth, smaller
  flits, shallower queues, or explicit base latency should worsen the node `1`
  curve while leaving node `0` effectively unchanged.

Interpret the graph as a curve comparison, not a single-point pass/fail test.
At `workers=0`, both nodes report `bandwidth_mib_s=0` because no background
traffic is injected; compare their `latency_ns`. At higher worker counts,
compare both `bandwidth_mib_s` and the resulting loaded `latency_ns`.

Do not use zero-worker latency results from the older 4 MiB latency-buffer
runs. With 16 or 32 TimingSimpleCPU cores, 4 MiB fits inside the aggregate
Ruby L2 capacity, so `workers=0` mostly measures warmed-cache pointer-chase
latency and node `0` and node `1` appear incorrectly identical. The current
default latency buffer is 64 MiB so the dependent load stream exceeds the
shared cache footprint and reaches the modeled memory path.

Do not use results from the older `clock_gettime()`-timed version of this
benchmark. In this gem5 guest Linux falls back to `refined-jiffies`, so
`CLOCK_MONOTONIC` advances in about 1ms chunks and sometimes does not advance
at all during a point. Those runs produce `seconds=0.000000000` or exact
1ms-step latencies and impossible bandwidth values. The current benchmark uses
gem5's simulated x86 TSC via `rdtsc` for `seconds`, `latency_ns`, and
`bandwidth_mib_s`, while `clock_seconds` is printed only as a diagnostic.

## Files

- `scripts/numa_bwlat.c`: pthread benchmark using `mbind`, CPU affinity,
  streaming worker threads, and a pointer-chase latency thread.
- `scripts/guest_numa_bwlat.sh`: guest build/run wrapper.
- `scripts/x86_two_tier_numa_bwlat.py`: gem5 full-system config with KVM boot,
  Timing ROI, two NUMA memory nodes, and eight guest cores by default.
- `scripts/check_bwlat_config.py`: config/readfile packaging validator.
- `scripts/visualize_bwlat.py`: parses `BWL_RESULT` lines into CSV and SVG.

## How to Run

Host compile smoke test:

```sh
cd /home/cc/inmem
cc -O2 -Wall -Wextra -pthread \
  -o step_12_bw_latency_curve/artifacts/numa_bwlat_host_smoke \
  step_12_bw_latency_curve/scripts/numa_bwlat.c
```

Config-generation smoke run:

```sh
cd /home/cc/inmem
rm -rf step_12_bw_latency_curve/artifacts/m5out
gem5/build/X86/gem5.opt \
  --outdir=step_12_bw_latency_curve/artifacts/m5out \
  step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py \
  --max-ticks 1
```

Full guest run:

```sh
cd /home/cc/inmem
rm -rf step_12_bw_latency_curve/artifacts/m5out
gem5/build/X86/gem5.opt \
  --outdir=step_12_bw_latency_curve/artifacts/m5out \
  step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py
```

The config defaults to `--num-cores 8`, so the guest has one latency thread and
up to seven bandwidth workers. Override `--num-cores` for a wider graph.

The guest workload defaults keep the latency working set larger than the
aggregate Ruby L2 footprint used by the 16-core and 32-core curve helpers:

- `BWL_WORKER_MIB=16`
- `BWL_LATENCY_MIB=64`
- `BWL_LATENCY_ITERS=65536`
- `BWL_WORKER_STEP=1`
- `BWL_MAX_WORKERS=nproc - 1`

For a faster smoke-style full run, reduce worker count directly in the config
arguments:

```sh
gem5/build/X86/gem5.opt \
  --outdir=step_12_bw_latency_curve/artifacts/m5out_short \
  step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py \
  --bwl-max-workers 2 \
  --bwl-latency-iters 16384
```

Very small latency-iteration counts are useful only for end-to-end smoke
testing. Use the default `65536` iterations or larger for quantitative curves.

The 16-core helper uses the same working-set defaults as the generic config:
`16 MiB` worker buffers and a `64 MiB` latency buffer. Do not use x86 `clflush`
for cache cleanup in this TimingSimpleCPU path; it has triggered a gem5 x86
page walker assertion in full-system Timing runs.

For a larger curve, increase guest cores and buffer sizes:

```sh
gem5/build/X86/gem5.opt \
  --outdir=step_12_bw_latency_curve/artifacts/m5out_16c \
  step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py \
  --num-cores 16 \
  --bwl-worker-mib 16 \
  --bwl-latency-mib 64
```

Recommended first saturation run:

```sh
cd /home/cc/inmem
step_12_bw_latency_curve/scripts/run_16core_curve.sh
```

This uses 16 guest cores, one latency thread, up to 15 bandwidth workers,
`BWL_WORKER_STEP=2`, `BWL_WORKER_MIB=16`, and `BWL_LATENCY_MIB=64`, producing
worker counts `0, 2, 4, 6, 8, 10, 12, 14, 15`. The script writes the run under
`step_12_bw_latency_curve/artifacts/m5out_16c`, validates the config/readfile,
and creates the CSV/SVG graph.

The previous `m5out_16c_fixed` run accidentally ignored `BWL_WORKER_STEP`
whenever `BWL_CPU_MHZ` was also passed, so it swept every worker count from
`0` through `15`. It also used a 4 MiB latency buffer, so its `workers=0`
latencies are cache-hit diagnostics rather than valid node0-versus-node1 memory
latencies. Future runs honor the requested step and use a larger latency
working set.

Useful overrides:

```sh
OUTDIR=step_12_bw_latency_curve/artifacts/m5out_16c_trial \
BWL_LATENCY_ITERS=32768 \
TIMEOUT_SECONDS=7200 \
step_12_bw_latency_curve/scripts/run_16core_curve.sh
```

Higher injected bandwidth run:

```sh
cd /home/cc/inmem
step_12_bw_latency_curve/scripts/run_32core_curve.sh
```

This uses 32 guest cores, one latency thread, up to 31 bandwidth workers, and
`BWL_WORKER_STEP=4`, producing worker counts
`0, 4, 8, 12, 16, 20, 24, 28, 31`. It inherits the 16 MiB worker buffers and
64 MiB latency buffer. Use this when the 16-core right edge is still below the
desired injected read bandwidth. With TimingSimpleCPU the benchmark is
request-generation limited by worker cores, so increasing guest core count is
the primary way to push well beyond the 16-core bandwidth.

After plotting, decide whether 16 cores are enough by checking the node `0`
right edge. If node `0` bandwidth has flattened or increases only marginally at
the highest worker counts, keep 16 cores. If node `0` is still clearly climbing
at `workers=15`, rerun with 32 cores and a larger worker step. Node `1`
flattening earlier is expected because it is behind two CXL-like links.

## How to Validate and Plot

Packaging/config validation:

```sh
cd /home/cc/inmem
python3 step_12_bw_latency_curve/scripts/check_bwlat_config.py \
  step_12_bw_latency_curve/artifacts/m5out
```

Visualization after a full run:

```sh
cd /home/cc/inmem
python3 step_12_bw_latency_curve/scripts/visualize_bwlat.py \
  step_12_bw_latency_curve/artifacts/m5out
```

The visualizer writes:

- `bw_latency_results.csv`
- `bw_latency_results.svg`

Expected serial output lines look like:

```text
BWL_RESULT node=0 workers=0 ... bandwidth_mib_s=0.000 latency_ns=...
BWL_RESULT node=0 workers=7 ... bandwidth_mib_s=... latency_ns=...
BWL_RESULT node=1 workers=0 ... bandwidth_mib_s=0.000 latency_ns=...
BWL_RESULT node=1 workers=7 ... bandwidth_mib_s=... latency_ns=...
```
