# Step 10 Notes

## Assumptions

- The full measurement workflow should not collect KVM boot statistics.
- Resetting stats immediately after `simulator.switch_processor()` gives a clean ROI window for Timing CPU measurements.
- The guest workload should use ordinary Linux mechanisms, such as `numactl` or first touch, not a custom driver.

## Open Questions

- The exact detailed CPU model for final experiments may need to change from `BaseTimingSimpleCPU` to an O3 or other detailed CPU. The control-flow boundary remains the same.
- Checkpointing is useful for repeated measurements but is intentionally not part of the first milestone.

## Uncertain Items

- Running shell commands under Timing CPU can be slow. For real experiments, keep the post-switch shell wrapper tiny and launch the ROI directly.
- The current guest image includes `numactl`, so measurement readfiles can use explicit `numactl --membind` commands. First-touch placement and sysfs-based validation remain useful alternatives.
