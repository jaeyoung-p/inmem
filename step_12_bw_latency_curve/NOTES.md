# Step 12 Notes

- Intel MLC is unavailable in this workspace; the host is AMD EPYC.
- The in-tree benchmark measures only the needed MLC-style curve: injected
  read bandwidth versus dependent-load latency.
- CPUs are in proximity domain 0; node1 is memory-only.
- Current timing uses `rdtsc`; `clock_seconds` is diagnostic.
- Current defaults use 16 MiB worker buffers and a 64 MiB latency buffer.
- Use `run_16core_curve.sh` first, then `run_32core_curve.sh` if more injected
  bandwidth is needed.
- Ignore old `clock_gettime()` runs, old 4 MiB zero-worker latency points, and
  the rejected `clflush` run.
