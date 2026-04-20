# Step 8: Expose RAM as NUMA Nodes

## Purpose

Add minimal ACPI SRAT/SLIT tables so Linux sees:

- node0: all CPUs plus local DDR5 RAM;
- node1: memory-only CXL-like RAM;
- SLIT local distance 10 and remote distance 20.

This step does not add guest-visible CXL enumeration or a guest driver.

## Files

- `scripts/x86_two_tier_numa_config.py`
- `scripts/check_acpi_numa_config.py`
- `patches/step_08_expose_fast_slow_as_numa_nodes.patch`

Relevant gem5 source:

- `gem5/src/arch/x86/bios/ACPI.py`
- `gem5/src/arch/x86/bios/acpi.hh`
- `gem5/src/arch/x86/bios/acpi.cc`
- `gem5/src/python/gem5/components/boards/large_mem_x86.py`

## Current ACPI Policy

- all exposed APIC IDs map to proximity domain 0;
- node0 memory affinity covers local low and high RAM around the PCI hole;
- node1 memory affinity covers `[65GiB, 129GiB)`;
- RSDT/XSDT include MADT, SRAT, and SLIT.

## Run

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out_x86_node0_8ch \
  step_08_expose_fast_slow_as_numa_nodes/scripts/x86_two_tier_numa_config.py \
  --max-ticks 1
```

## Validate

```sh
python3 step_08_expose_fast_slow_as_numa_nodes/scripts/check_acpi_numa_config.py \
  step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out_x86_node0_8ch
```
