# Step 12 Notes

- Intel MLC was checked first. No `mlc` binary is present in `PATH` or under
  this workspace, and the host CPU vendor is `AuthenticAMD`.
- The replacement benchmark intentionally measures only the MLC-style curve
  needed for this project: injected read bandwidth versus dependent-load
  latency.
- Guest CPUs are all exposed in proximity domain `0`; node `1` remains
  memory-only. The benchmark therefore binds execution to CPU node `0` and
  sweeps memory allocation on node `0` and node `1`.
- The default config raises the guest CPU count to eight. Use `--num-cores` for
  wider bandwidth-pressure sweeps.
- Expected curve shape: node `0` should have the lowest unloaded latency and
  higher sustainable bandwidth because it is local eight-channel DDR5. Node `1`
  should show higher loaded latency and lower bandwidth once the CXL-like link
  serialization and FIFO queueing become visible. CXL parameter sweeps should
  move node `1` while leaving node `0` effectively unchanged.
- The first 16-core result sets named `m5out_16c_short`, `m5out_16c_long`, and
  `m5out_16c_full` are invalid for performance interpretation. They were timed
  with `clock_gettime(CLOCK_MONOTONIC)`, but the guest switched to
  `refined-jiffies`, yielding 0ms or 1ms-quantized elapsed times and impossible
  bandwidth. The benchmark now uses gem5 x86 `rdtsc` cycles for timing and
  reports the jiffy clock only as `clock_seconds`.
- A later attempt to flush latency and worker buffers with x86 `clflush`
  triggered a gem5 TimingSimpleCPU page-walker assertion:
  `DataTranslation::finish: Assertion mode == state->mode failed`. Do not use
  `clflush` in this benchmark path. Prefer larger buffers and TSC-cycle timing
  instead.
