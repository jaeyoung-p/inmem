# Step 16 Notes

- `numactl --interleave=0,1` controls in-memory graph placement. File
  location alone does not determine NUMA placement.
- The guest wrapper uses `OMP_NUM_THREADS=1` by default so IPC is easier to
  interpret.
- The final IPC path uses `X86O3CPU`. `TimingSimpleCPU` is available only as
  a plumbing fallback through `--roi-cpu timing`.
- Step 16 uses Ruby `MESI_Three_Level`, not `MESI_Two_Level`, because the IPC
  experiment needs a shared L3.
- The default cache geometry is 32KiB L1I, 48KiB L1D, 2MiB private L2, and
  60MiB shared L3.
- `ROI_MAX_INSTS` can stop long runs by committed ROI instructions. This is
  scheduled after the ROI CPU switch and stats reset, so it does not count KVM
  graph construction.
- MAC timing and extra CXL data slots are mutually exclusive.
- Generated `artifacts/` contents are not source material.
- The first pass builds in the guest. If setup time dominates repeated sweeps,
  add deliberate image payload tooling later.
