# Step 11: NUMA Microbenchmark Validation

## Purpose

Validate that ordinary Linux NUMA placement can direct traffic to node0 or
node1 before running the larger Step 12 curve.

Node1 is ordinary NUMA RAM in the guest. No CXL driver, DAX, pmem, devdax, or
guest kernel patch is used.

## Files

- `scripts/numa_touch.c`
- `scripts/guest_numa_microbench.sh`
- `scripts/x86_two_tier_numa_microbench.py`
- `scripts/check_microbench_config.py`
- `scripts/check_cxl_latency_model.py`
- `scripts/visualize_microbench.py`
- `scripts/run_latency_sweep.sh`

## Probes

`numa_touch.c` supports:

- `read_seq`;
- `write_seq`;
- `readwrite_seq`;
- `read_stride`;
- dependent-load `chase`.

The guest wrapper uses `numactl --cpunodebind=0 --membind=N` and `mbind` to
allocate on the requested node.

## Run

Host compile smoke:

```sh
cd /home/cc/inmem
cc -O2 -Wall -Wextra \
  -o /tmp/numa_touch_host_smoke \
  step_11_microbench_validation/scripts/numa_touch.c
```

Config-generation smoke:

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_11_microbench_validation/artifacts/m5out_zero_base_smoke \
  step_11_microbench_validation/scripts/x86_two_tier_numa_microbench.py \
  --max-ticks 1
```

Latency calibration sweep:

```sh
cd /home/cc/inmem
step_11_microbench_validation/scripts/run_latency_sweep.sh
```

## Validate

```sh
python3 step_11_microbench_validation/scripts/check_microbench_config.py \
  step_11_microbench_validation/artifacts/m5out_zero_base_smoke

python3 step_11_microbench_validation/scripts/check_cxl_latency_model.py \
  step_11_microbench_validation/artifacts/m5out_zero_base_smoke
```

## Interpret

- Node0 should generally be lower latency or higher bandwidth.
- Node1 should show the cost of the CXL-like path under queueing and
  serialization.
- Absolute numbers are not final performance claims unless the run uses a
  meaningful CPU model and clean ROI stats.
