# Step 6 Notes

- `LargeMemoryX86Board` owns the E820 replacement.
- The board's internal `[0xc0000000, 0xc0100000)` marker is not guest RAM.
- E820 type 1 is enough for ordinary RAM exposure; NUMA affinity starts in
  Step 8.
- The first MiB keeps the conventional x86 usable/reserved split.
