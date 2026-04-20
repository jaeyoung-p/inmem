# Step 8 Notes

## Assumptions

- `TwoTierMemory.get_numa_memory_ranges()` returns `{0: fast_ranges, 1: slow_ranges}`.
- The fixed project scope is exactly two nodes, so the board raises if the NUMA range map has anything other than nodes `0` and `1`.
- SRAT memory affinity covers node `0` as `[0, 0xc0000000)` and
  `[0x100000000, 0x1040000000)`. E820 keeps the conventional low
  usable/reserved split.
- SRAT memory affinity flags use `1`, meaning enabled.
- SLIT distances are simple and symmetric: local `10`, remote `20`.

## Open Questions

- Step 9 currently exposes an early Linux sparsemem panic after SRAT parsing.
  The config-level SRAT/SLIT objects validate, but real boot acceptance remains
  open.
- The large-memory Step 9 boot exposed a repeatable Linux sparsemem crash while
  processing section 0 after SRAT parsing. The board anchors the low SRAT
  affinity at zero so conventional low usable RAM belongs to node `0`, but this
  does not yet resolve the kernel panic.

## Uncertain Items

- This step validates ACPI object construction through `config.ini` and `config.json`; kernel parsing is validated in Step 9.
- The implementation follows gem5's existing ACPI serialization style and does not add explicit byte-order conversion beyond the local packed-struct approach already used by MADT.
