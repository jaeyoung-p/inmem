# Step 11 Notes

- `mbind` and `numactl` are normal Linux NUMA mechanisms.
- Default node1 fixed CXL base latency is zero.
- `--cxl-base-latency` exists only for explicit calibration sweeps.
- `chase` is the latency probe; streaming probes are for bandwidth and
  queue-pressure trends.
- Increase benchmark size if tiny runs hide the qualitative node difference.
