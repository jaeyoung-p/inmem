# Step 0 Notes

- The implementation follows stdlib x86 board structure.
- Large-memory runs use `LargeMemoryX86Board`; stock `X86Board` is unchanged
  for small-memory configs.
- Linux is unmodified. NUMA visibility comes from SRAT/SLIT.
- The current guest image is
  `/home/cc/.cache/gem5/x86-ubuntu-24.04-numactl.img`.
- `numactl` is installed in that image.
- Timing-mode shell work is slow; keep ROI scripts small.
