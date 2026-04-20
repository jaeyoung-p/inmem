# Step 9 Notes

- KVM is appropriate for topology validation; Timing CPU is reserved for
  measurement.
- The guest image includes `numactl`.
- `dmesg` may be restricted in the guest; `journalctl -k` and raw serial output
  provide kernel NUMA evidence.
- Node memory totals are below raw 64GiB because Linux reserves memory.
