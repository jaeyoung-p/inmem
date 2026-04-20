# Step 11: Microbenchmark Validation

## Goal

Add a tiny workload suite that can compare allocation on the fast and slow NUMA
nodes using ordinary Linux NUMA mechanisms. This is only for validation; it is
not a required application change for real workloads.

The expected qualitative result is:

- node `0` allocation uses fast RAM and should have lower modeled latency or higher bandwidth;
- node `1` allocation uses slow RAM and should have higher modeled latency or
  lower bandwidth because traffic crosses CXL.mem flit queues/serialization
  before reaching matching DDR5 media.

No CXL, DAX, pmem, devdax, guest driver, or guest kernel patch is used.

The default node `1` CXL path has no fixed base latency. Extra delay is modeled
by FIFO queue wait and flit serialization only. `--cxl-base-latency` remains
available for explicit calibration/discrepancy sweeps.

## Files Touched

Step-local files:

- `scripts/numa_touch.c`
- `scripts/guest_numa_microbench.sh`
- `scripts/x86_two_tier_numa_microbench.py`
- `scripts/check_microbench_config.py`
- `scripts/check_cxl_latency_model.py`
- `scripts/visualize_microbench.py`
- `scripts/run_latency_sweep.sh`
- `artifacts/numa_touch_host_smoke`
- `artifacts/m5out/`
- `artifacts/validation_summary.txt`

Related gem5 defaults:

- `gem5/src/python/gem5/components/memory/tiered.py` defaults
  `cxl_base_latency` to `0ns`;
- `gem5/src/mem/CxlMemLink.py` defaults `m2s_latency` and `s2m_latency` to
  `0ns`.

## Exact Code Changes

`numa_touch.c` is a small benchmark that:

- allocates anonymous memory with `mmap`;
- binds the allocation to a requested NUMA node with the Linux `mbind` syscall;
- first-touches the pages after binding;
- runs one of five probes: `read_seq`, `write_seq`, `readwrite_seq`,
  `read_stride`, or `chase`;
- prints `MB_RESULT` lines with elapsed time, MiB/s, and ns/op.

`guest_numa_microbench.sh` compiles the benchmark in the guest if a compiler
exists, then runs every probe on nodes `0` and `1` through normal
`numactl --cpunodebind=0 --membind=N` commands.

`x86_two_tier_numa_microbench.py` embeds both files into the readfile and uses `/home/cc/.cache/gem5/x86-ubuntu-24.04-numactl.img` as the guest disk. It keeps KVM active for boot and guest compilation, then the guest calls `gem5-bridge hypercall 4` immediately before the benchmark. The hypercall handler switches to Timing CPU and resets stats. Hypercall `3` dumps stats and exits after the readfile script finishes.

## How to Run

Host-side compile smoke test for the benchmark suite:

```sh
cd /home/cc/inmem
cc -O2 -Wall -Wextra \
  -o step_11_microbench_validation/artifacts/numa_touch_host_smoke \
  step_11_microbench_validation/scripts/numa_touch.c
```

Config-generation smoke run:

```sh
cd /home/cc/inmem
rm -rf step_11_microbench_validation/artifacts/m5out
gem5/build/X86/gem5.opt \
  --outdir=step_11_microbench_validation/artifacts/m5out \
  step_11_microbench_validation/scripts/x86_two_tier_numa_microbench.py \
  --max-ticks 1
```

Full guest microbenchmark run:

```sh
cd /home/cc/inmem
rm -rf step_11_microbench_validation/artifacts/m5out
gem5/build/X86/gem5.opt \
  --outdir=step_11_microbench_validation/artifacts/m5out \
  step_11_microbench_validation/scripts/x86_two_tier_numa_microbench.py
```

Use the X86 build target for this project:

```sh
gem5/build/X86/gem5.opt
```

The full run may be slow after the ROI switch because the benchmark runs under
Timing CPU. The default benchmark size is intentionally smoke-sized: `1 MiB`,
`1` pass per node for streaming/stride probes and `1` pass for pointer chase.
Override the guest defaults with `MB_MIB`, `MB_PASSES`, `MB_CHASE_PASSES`, and
`MB_STRIDE` in `guest_numa_microbench.sh` for longer measurements.

Optional CXL slow-path knobs are available for sweeps: `--cxl-flit-size`, `--cxl-link-bandwidth`, `--cxl-base-latency`, and `--cxl-queue-depth-flits`.

To directly compare the intended zero-fixed-latency model with an explicit
fixed-latency calibration run:

```sh
cd /home/cc/inmem
step_11_microbench_validation/scripts/run_latency_sweep.sh
```

The sweep writes `microbench_results.csv` and `microbench_results.svg` under
`step_11_microbench_validation/artifacts/latency_sweep/`.

## How to Validate

For packaging and config validation:

```sh
cd /home/cc/inmem
python3 step_11_microbench_validation/scripts/check_microbench_config.py \
  step_11_microbench_validation/artifacts/m5out \
  | tee step_11_microbench_validation/artifacts/validation_summary.txt
```

For the node `1` latency-model invariant:

```sh
cd /home/cc/inmem
python3 step_11_microbench_validation/scripts/check_cxl_latency_model.py \
  step_11_microbench_validation/artifacts/m5out
```

For visualization after a full run:

```sh
cd /home/cc/inmem
python3 step_11_microbench_validation/scripts/visualize_microbench.py \
  step_11_microbench_validation/artifacts/m5out
```

Expected result:

```text
Step 11 microbenchmark packaging validation passed
- FS script uses LargeMemoryX86Board
- config contains KVM start and Timing switch cores
- config preserves eighteen DDR5-derived memory interfaces/controllers
- config includes direct node 0 controllers and slow CxlMemLinks
- default CXL fixed base latency is zero for both directions
- config contains SRAT/SLIT NUMA tables
- readfile embeds the mbind-based benchmark suite
- readfile uses the numactl command path from the customized guest image
- readfile switches to Timing at the benchmark ROI boundary
```

For a full guest run, inspect serial output for lines like:

```text
MB_RESULT node=0 bench=chase mib=64 passes=2 ... ns_per_op=...
MB_RESULT node=1 bench=chase mib=64 passes=2 ... ns_per_op=...
```

The node `1` line should show worse qualitative performance than node `0`.

## What Remains

`step_00_design_and_usage` packages the final patch order, run commands, validation checklist, and modeling limitations.
