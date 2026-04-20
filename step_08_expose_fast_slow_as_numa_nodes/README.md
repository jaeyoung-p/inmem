# Step 8: Expose Fast/Slow RAM as NUMA Nodes

## Goal

Add minimal ACPI NUMA exposure for the fixed two-tier RAM layout.

Target topology:

- node 0: all CPUs/APIC IDs plus fast RAM
- node 1: slow RAM only
- SLIT local distance: `10`
- SLIT remote distance: `20`

This step implements only SRAT and SLIT. It does not refactor the ACPI framework and does not introduce guest-visible CXL enumeration, DAX, pmem, devdax, PCIe memory, or a guest driver.

## Files Touched

Gem5 source patched:

- `gem5/src/arch/x86/bios/ACPI.py`
- `gem5/src/arch/x86/bios/SConscript`
- `gem5/src/arch/x86/bios/acpi.hh`
- `gem5/src/arch/x86/bios/acpi.cc`
- `gem5/src/python/gem5/components/boards/large_mem_x86.py`

Step-local files:

- `scripts/x86_two_tier_numa_config.py`
- `scripts/check_acpi_numa_config.py`
- `patches/step_08_expose_fast_slow_as_numa_nodes.patch`
- `artifacts/m5out/`
- `artifacts/validation_summary.txt`

## Exact Code Changes

`ACPI.py` adds these SimObjects:

- `X86ACPISratRecord`
- `X86ACPISrat`
- `X86ACPISratProcessorLocalApic`
- `X86ACPISratMemoryAffinity`
- `X86ACPISlit`

`SConscript` registers those SimObjects for x86 ISA builds.

`acpi.hh` and `acpi.cc` implement:

- SRAT table serialization with a table revision field and variable-length records;
- SRAT processor local APIC affinity records, type `0`, length `16`;
- SRAT memory affinity records, type `1`, length `40`;
- SLIT serialization with a flattened distance matrix.

`LargeMemoryX86Board` calls `_setup_numa_acpi_tables()` after stock x86 board setup. If the memory component provides the project-local `get_numa_memory_ranges()` hook, the board creates:

- one SRAT processor affinity record per APIC ID, all mapped to proximity domain `0`;
- two SRAT memory affinity records for fast RAM, mapped to node `0`;
- one SRAT memory affinity record for slow RAM, mapped to node `1`;
- one SLIT table with distances `[10, 20, 20, 10]`;
- RSDT and XSDT entries for both SRAT and SLIT.

The fast memory affinity covers the full low node range and is split around the
x86 PCI hole. E820 still carries the conventional low usable/reserved split:

- `[0x000000, 0xc0000000)` on node `0`;
- `[0x100000000, 0x1040000000)` on node `0`;
- `[0x1040000000, 0x2040000000)` on node `1`.

`LargeMemoryX86Board` keeps the SRAT low affinity anchored at zero so the
conventional sub-1MiB usable RAM remains covered by node `0`.

## How to Apply

From the project root:

```sh
cd /home/cc/inmem/gem5
git apply ../step_08_expose_fast_slow_as_numa_nodes/patches/step_08_expose_fast_slow_as_numa_nodes.patch
```

This patch is intended to be applied after Steps 4 and 6.

## How to Build

```sh
cd /home/cc/inmem/gem5
scons build/ALL/gem5.opt -j$(nproc)
```

Observed result: build completed successfully.

## How to Run

Generate a config-only smoke run:

```sh
cd /home/cc/inmem
rm -rf step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out
gem5/build/ALL/gem5.opt \
  --outdir=step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out \
  step_08_expose_fast_slow_as_numa_nodes/scripts/x86_two_tier_numa_config.py \
  --max-ticks 1
```

## How to Validate

```sh
cd /home/cc/inmem
python3 step_08_expose_fast_slow_as_numa_nodes/scripts/check_acpi_numa_config.py \
  step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out
```

Expected result:

```text
Step 8 ACPI NUMA config validation passed
- RSDT/XSDT contain MADT, SRAT, and SLIT
- SRAT maps APIC IDs 0 and 1 to node 0
- SRAT maps low and high fast RAM to node 0
- SRAT maps slow RAM at 65GiB-129GiB to node 1
- SLIT distance matrix is local=10, remote=20
```

Useful direct inspection:

```sh
rg -n "X86ACPISrat|X86ACPISlit|proximity_domain|base_address|address_length|distances|locality_count" \
  step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out/config.ini
```

## What Remains

Step 9 must boot Linux far enough to prove ACPI parsing and guest-visible NUMA topology with `dmesg`, `numactl --hardware`, `lscpu`, sysfs node state, and `numastat`.
