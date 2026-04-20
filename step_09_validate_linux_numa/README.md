# Step 9: Validate Linux NUMA

## Purpose

Boot Linux and validate that SRAT/SLIT produce the intended NUMA topology:

- node0: CPUs plus local DDR5 RAM;
- node1: memory-only CXL-like RAM;
- online nodes: `0-1`.

This step adds no gem5 source patches.

## Files

- `scripts/x86_two_tier_numa_boot.py`
- `scripts/check_linux_numa.py`

## Run

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_09_validate_linux_numa/artifacts/m5out_x86_node0_8ch \
  step_09_validate_linux_numa/scripts/x86_two_tier_numa_boot.py
```

## Validate

```sh
python3 step_09_validate_linux_numa/scripts/check_linux_numa.py \
  step_09_validate_linux_numa/artifacts/m5out_x86_node0_8ch
```

The checker looks for SRAT/SLIT kernel evidence, online nodes `0-1`, CPUs on
node0, no CPUs on node1, and node memory totals near the expected 64GiB per
node after firmware/kernel reservations.
