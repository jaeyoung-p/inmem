# Step 16 Notes

- `numactl --interleave=0,1` controls in-memory graph placement. File
  location alone does not determine NUMA placement.
- The guest wrapper uses `OMP_NUM_THREADS=1` by default so IPC is easier to
  interpret.
- `GAPBS_KERNEL` selects one embedded C++ source per kernel. Current values are
  `pr_spmv`, `pr`, `bc`, `sssp`, `cc`, and `tc`.
- The final IPC path uses `X86O3CPU`. `TimingSimpleCPU` is available only as
  a plumbing fallback through `--roi-cpu timing`.
- Step 16 uses Ruby `MESI_Three_Level`, not `MESI_Two_Level`, because the IPC
  experiment needs a shared L3.
- The default cache geometry is 32KiB L1I, 48KiB L1D, 2MiB private L2, and
  60MiB shared L3.
- `ROI_WARMUP_INSTS` can run an unmeasured O3 warmup before the measured
  window. Stats are reset after warmup, then `ROI_MAX_INSTS` can stop the
  measured window by committed ROI instructions.
- The normal ROI end marker is inside the benchmark process, immediately after
  the measured trial loop, so uncapped runs do not depend on shell or OpenMP
  teardown reaching the wrapper's final marker under O3.
- MAC timing and extra CXL data slots are mutually exclusive.
- Generated `artifacts/` contents are not source material.
- The first pass builds in the guest. If setup time dominates repeated sweeps,
  add deliberate image payload tooling later.
