# Step 6 Notes

## Assumptions

- Step 4 is already applied, so `LargeMemoryX86Board._setup_memory_ranges()` accepts the fixed data ranges from `TwoTierMemory`.
- The board-level `[0xc0000000, 0xc0100000)` range is an internal I/O marker and must not be advertised as guest RAM.
- E820 type `1` is sufficient for ordinary system RAM exposure at this step.
- The large-memory board keeps the conventional first-MiB E820 split, while
  SRAT covers the full low node range so sub-1MiB usable RAM is not left outside
  NUMA coverage.

## Open Questions

- The Ubuntu after-boot helper in the gem5 resource reaches the serial login boundary but did not echo the readfile payload during the automated Step 6 run. The intended guest commands are embedded in `scripts/x86_two_tier_e820_boot.py`, but the recorded validation relies on kernel E820 boot logs plus `config.ini`.
- Step 8 uses the same large-board range metadata to describe guest-visible usable subranges in SRAT.

## Uncertain Items

- Linux's boot log says `System RAM` through the E820 path indirectly; the serial evidence captured here is the earlier `BIOS-e820` parse plus the kernel's memory-node fallback messages. Direct `/proc/iomem` capture is planned as a stronger validation point once SRAT/SLIT is present and the after-boot command path is adjusted if needed.
