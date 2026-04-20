# Step 0: Design and Usage

## Purpose

This folder records the project design constraints. It does not patch gem5 or
run a guest.

Current model:

```text
x86 sparse RAM -> local node0 DDR5 -> CXL-like memory-only node1 -> Linux NUMA
```

## Fixed Layout

| Node | Range | Meaning |
| --- | ---: | --- |
| 0 | `[0, 3GiB)` | local DDR5 below the x86 PCI hole |
| none | `[3GiB, 4GiB)` | PCI/platform hole |
| 0 | `[4GiB, 65GiB)` | same local DDR5 node above the hole |
| 1 | `[65GiB, 129GiB)` | CXL-like memory-only RAM |

Node0 is one 8-channel DDR5 memory system split only by the PCI hole. Node1
has two DDR5 channels behind two `CxlMemLink` objects.

## Design Rules

- Use `LargeMemoryX86Board` for large-memory experiments.
- Keep stock `X86Board` on the upstream small-memory path.
- Build only `build/X86/gem5.opt`.
- Expose node1 as ordinary Linux NUMA RAM, not DAX, pmem, devdax, or a
  guest-visible CXL device.
- Do not use `RangeAddrMapper` in the current KVM-safe path.
- Route Ruby traffic by address range ownership.
- Use ACPI SRAT/SLIT for NUMA exposure.

## Step Order

1. Step 2: x86 KVM-to-Timing baseline.
2. Step 4: large-memory board and `TwoTierMemory`.
3. Step 5: Ruby range routing validation.
4. Step 6: E820 multi-range boot validation.
5. Step 8: ACPI SRAT/SLIT NUMA exposure.
6. Step 9: Linux NUMA validation.
7. Step 10: KVM-to-Timing ROI boundary.
8. Step 11: small NUMA microbenchmarks.
9. Step 12: bandwidth versus loaded-latency curves.

## Out of Scope

- guest kernel patches;
- guest CXL driver work;
- DAX/devdax/pmem modeling;
- broad stdlib memory refactors;
- N-tier generalization;
- application source changes.
