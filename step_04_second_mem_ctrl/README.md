# Step 4: Large-Memory Board and Memory Component

## Purpose

Introduce the project-local large-memory x86 board path and `TwoTierMemory`.
The current implementation models node0 as local DDR5 and node1 as CXL-like
memory-only RAM.

## Files

- `scripts/x86_two_tier_kvm_timing.py`
- `scripts/check_two_tier_config.py`
- `scripts/check_large_mem_board_smoke.py`
- `patches/step_04_second_mem_ctrl.patch`

The live source is in the gem5 submodule, especially:

- `gem5/src/python/gem5/components/boards/large_mem_x86.py`
- `gem5/src/python/gem5/components/memory/tiered.py`
- `gem5/src/python/gem5/components/memory/split_range.py`

## Current Expected Config

- node0 ranges: `[0, 3GiB)` and `[4GiB, 65GiB)`;
- node1 range: `[65GiB, 129GiB)`;
- 16 node0 DDR5 controllers/directories;
- 2 node1 DDR5 controllers/directories behind `CxlMemLink`;
- 18 total `MemCtrl` objects;
- no `RangeAddrMapper`.

## Run

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_04_second_mem_ctrl/artifacts/m5out_x86_node0_8ch \
  step_04_second_mem_ctrl/scripts/x86_two_tier_kvm_timing.py \
  --max-ticks 1
```

## Validate

```sh
python3 step_04_second_mem_ctrl/scripts/check_two_tier_config.py \
  step_04_second_mem_ctrl/artifacts/m5out_x86_node0_8ch/config.ini
```
