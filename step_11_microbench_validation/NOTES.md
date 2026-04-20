# Step 11 Notes

## Assumptions

- `mbind` is a normal Linux NUMA mechanism and does not require a custom guest driver.
- The benchmark suite is intentionally small and exists only to validate the modeled fast/slow tier distinction.
- A real application can use first touch, `numactl`, or existing NUMA-aware placement without source changes.
- The default node `1` CXL path has zero fixed base latency. Any default node
  `1` delta should come from queue wait and flit serialization, plus the same
  DDR5 media model used by node `0`.
- `--cxl-base-latency` is retained only for explicit calibration sweeps and for
  showing how fixed latency would distort access-latency measurements.

## Open Questions

- The current Ubuntu image has `numactl` installed. If the image lacks a compiler, either install one in the reusable guest image or copy a prebuilt `numa_touch` binary into the guest. This does not change the modeled memory system.

## Uncertain Items

- The absolute numbers from `numa_touch` are not meaningful unless the run has switched to a detailed CPU and stats are reset at the ROI boundary.
- `chase` is the best probe for access latency because it serializes dependent
  loads. The streaming probes are better for bandwidth and queue-pressure
  trends.
- With very small benchmark sizes, noise from guest execution can hide the latency gap. Increase the MiB/pass counts if the qualitative difference is not visible.
