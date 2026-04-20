# Step 0 Notes

## Assumptions

- The implementation follows stdlib `X86Board` structure for baseline runs and
  uses `LargeMemoryX86Board` for project-local large-memory x86 FS runs.
- Ruby MESI Two Level remains the cache hierarchy for the x86 FS KVM-to-Timing path.
- `TwoTierMemory` remains a fixed two-tier component, not an N-tier heterogeneous memory framework.
- Linux is unmodified. NUMA visibility comes from ACPI SRAT/SLIT, not from a guest driver or kernel patch.
- The current gem5 tree includes the Step 4, Step 6, and Step 8 source patches.
- The step artifacts under `/home/cc/inmem` are kept as reviewable evidence rather than generated build products to discard.

## Guest Image Notes

- The current experiment image is `/home/cc/.cache/gem5/x86-ubuntu-24.04-numactl.img`, which includes `numactl`.
- The `numactl` image was successfully customized with `sudo virt-customize --upload /tmp/debs/numactl_2.0.18-1ubuntu0.24.04.1_amd64.deb:/tmp/ --run-command "dpkg -i /tmp/numactl_2.0.18-1ubuntu0.24.04.1_amd64.deb"`.
- Passing `/tmp/debs/numactl_*.deb:/tmp/` to `virt-customize --upload` did not work because `virt-customize` treated the wildcard path literally.
- A compiler or prebuilt tiny benchmark may still be useful for longer-running experiments.

## Uncertainties

- Absolute performance from the Step 11 tiny benchmark is not a final metric. It is only a sanity check that node placement can drive traffic into the fast or slow tier.
- Linux's reported node memory totals are not exact raw tier sizes because firmware, kernel, and page allocator reservations consume memory.
- Running shell commands under Timing CPU can be slow. Keep the post-switch ROI wrapper small for real experiments.

## Out Of Scope

- guest-visible CXL enumeration, PCIe-attached memory enumeration, DAX, devdax, pmem, NVMInterface, HeteroMemCtrl, or guest device-backed memory.
- N-tier generalization.
- Broad stdlib memory refactoring.
- Guest kernel changes.
- Guest drivers.
- Application source changes.
