# Step 9 Notes

## Assumptions

- The Step 8 SRAT/SLIT patch is already applied and built.
- KVM is appropriate for topology validation. Timing CPU is reserved for later measurement runs.
- The fixed NUMA mapping remains: node `0` for CPUs plus fast RAM, node `1` for memory-only slow RAM.

## Open Questions

- The step uses `/home/cc/.cache/gem5/x86-ubuntu-24.04-numactl.img`, which has `numactl` installed. `lscpu`, sysfs, and `journalctl -k` remain independent validation paths.
- The guest has `kernel.dmesg_restrict=1`, so unprivileged `dmesg` is denied. `journalctl -k` and the raw serial boot log expose the same kernel NUMA/SRAT/SLIT messages.

## Uncertain Items

- The observed node memory totals are slightly below the raw 2 GiB and 1 GiB sizes because Linux reserves kernel and firmware memory. The checker uses broad bounds rather than exact byte-for-byte totals.
- `/proc/iomem` is not used in this step because this guest masks addresses for the unprivileged login. E820 visibility was validated separately in Step 6.
