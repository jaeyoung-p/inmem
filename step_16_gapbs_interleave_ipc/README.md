# Step 16: GAPBS Interleave IPC

Step 16 measures O3 IPC for a graph kernel whose data pages are interleaved
across local DDR node0 and CXL-like memory node1 while execution remains bound
to node0.

The cache hierarchy is Ruby `MESI_Three_Level` with these defaults:

- private L1I: `32KiB`, 8-way
- private L1D: `48KiB`, 12-way
- private L2: `2MiB`, 16-way
- shared L3: `60MiB`, 20-way, one bank

`build/X86/gem5.opt` must be built with `RUBY_PROTOCOL_MESI_Three_Level=y`.
The local `gem5/build_opts/X86` file enables that protocol; rebuild with:

```sh
cd /home/cc/inmem/gem5
scons defconfig build/X86 build_opts/X86
scons build/X86/gem5.opt -j$(nproc)
```

The default benchmark is PageRank SpMV with a GAPBS-style command line. Graph
generation and allocation happen before the ROI under KVM. Only the selected
graph kernel trial runs after the ROI hypercall switches gem5 to `X86O3CPU`
and resets stats.

Available `GAPBS_KERNEL` values:

- `pr_spmv`: current PageRank SpMV-style pull kernel
- `pr`: PageRank pull kernel without the precomputed contribution array
- `bc`: single-source betweenness-centrality-style traversal
- `sssp`: SSSP-style iterative relaxation
- `cc`: connected-components-style label propagation
- `tc`: triangle-counting-style adjacency intersection

Generated graphs are the default. A guest-visible GAPBS `.sg` file can be used
with `GAPBS_FILE=/path/in/guest/graph.sg`; it is still loaded under
`numactl --interleave=0,1`.

## Build Smoke

```sh
cd /home/cc/inmem
c++ -O3 -std=c++11 -fopenmp \
  -o /tmp/gapbs_kernel_roi \
  step_16_gapbs_interleave_ipc/scripts/gapbs_pr_spmv_roi.cc
```

Host run smoke:

```sh
cd /home/cc/inmem
OMP_NUM_THREADS=1 numactl --cpunodebind=0 --interleave=0,1 \
  /tmp/gapbs_kernel_roi -g 16 -n 1 --no-roi
```

## Config Smoke

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=/tmp/inmem_step16_gapbs_smoke \
  step_16_gapbs_interleave_ipc/scripts/x86_gapbs_interleave_ipc.py \
  --variant baseline \
  --gapbs-scale 16 \
  --gapbs-trials 1 \
  --max-ticks 1
```

## Tiny Run

```sh
cd /home/cc/inmem
GAPBS_SCALE=14 GAPBS_TRIALS=1 VARIANTS=baseline \
  step_16_gapbs_interleave_ipc/scripts/run_gapbs_ipc_variants.sh
```

To select another kernel:

```sh
cd /home/cc/inmem
GAPBS_KERNEL=bc GAPBS_SCALE=14 GAPBS_TRIALS=1 VARIANTS=baseline \
  step_16_gapbs_interleave_ipc/scripts/run_gapbs_ipc_variants.sh
```

## Variant Sweep

```sh
cd /home/cc/inmem
GAPBS_SCALE=16 GAPBS_TRIALS=1 \
  step_16_gapbs_interleave_ipc/scripts/run_gapbs_ipc_variants.sh
```

Parsed CSV output is written to:

```text
artifacts/figures/gapbs_interleave_ipc/gapbs_ipc_results.csv
```

The parser reports IPC plus derived shared-L3 metrics. For Ruby
`MESI_Three_Level`, stdlib's shared L3 is named `L2Cache_Controller` in the
SLICC protocol counters. `llc_mpki`, `llc_hit_rate`, and
`llc_fetched_bytes_per_inst` are derived from L3 `L1_GETS/L1_GETX` requests and
the `NP.*` subset that fetched a line from memory.

To run four OpenMP threads on four simulated cores with an 8MiB shared L3:

```sh
cd /home/cc/inmem
NUM_CORES=4 OMP_THREADS=4 L3_SIZE=8MiB L3_ASSOC=16 \
  GAPBS_SCALE=27 GAPBS_TRIALS=1 VARIANTS="baseline" \
  ROI_WARMUP_INSTS=100000000 ROI_MAX_INSTS=100000000 \
  step_16_gapbs_interleave_ipc/scripts/run_gapbs_ipc_variants.sh
```

After the first complete point, inspect `simInsts`. If it is below 10M, raise
`GAPBS_SCALE` or `GAPBS_TRIALS`. If it is above 100M and too slow, reduce one
of them.

To warm up and then cap the measured ROI by committed instructions, set
`ROI_WARMUP_INSTS` and `ROI_MAX_INSTS`. The warmup limit is scheduled after
switching from KVM to the ROI CPU. When the warmup limit fires, stats are reset
again, then the measured limit is scheduled:

```sh
cd /home/cc/inmem
GAPBS_SCALE=27 GAPBS_TRIALS=1 VARIANTS=baseline \
  ROI_WARMUP_INSTS=100000000 ROI_MAX_INSTS=100000000 \
  step_16_gapbs_interleave_ipc/scripts/run_gapbs_ipc_variants.sh
```

With `ROI_WARMUP_INSTS=0`, `ROI_MAX_INSTS` is scheduled immediately after the
ROI CPU switch and initial stats reset. With `ROI_MAX_INSTS=0`, no measured
instruction cap is used.
