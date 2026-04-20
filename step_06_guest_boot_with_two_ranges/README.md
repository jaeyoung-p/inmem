# Step 6: Guest Boot with Multiple RAM Ranges

## Purpose

Validate that the x86 guest boots with the sparse large-memory E820 map and
sees all RAM ranges as ordinary system RAM.

Node1 is still ordinary Linux RAM in this model. It is not DAX, pmem, devdax,
or guest-visible CXL device memory.

## Files

- `scripts/x86_two_tier_e820_boot.py`
- `scripts/check_e820_boot.py`
- `patches/step_06_guest_boot_with_two_ranges.patch`

## Current E820 Shape

- conventional low usable RAM below 640KiB;
- reserved legacy low-memory gap;
- usable node0 RAM from 1MiB to 3GiB;
- reserved PCI/platform hole from 3GiB to 4GiB;
- usable node0 high RAM from 4GiB to 65GiB;
- usable node1 RAM from 65GiB to 129GiB.

## Run

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_06_guest_boot_with_two_ranges/artifacts/m5out \
  step_06_guest_boot_with_two_ranges/scripts/x86_two_tier_e820_boot.py
```

## Validate

```sh
python3 step_06_guest_boot_with_two_ranges/scripts/check_e820_boot.py \
  step_06_guest_boot_with_two_ranges/artifacts/m5out
```
