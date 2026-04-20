# Step 0: Design and Usage

## Goal

Collect the non-execution parts of the project in one place:

- repository survey;
- fixed physical memory layout;
- minimal ACPI NUMA design;
- patch order and run order;
- final modeling statement and limitations.

This step does not patch gem5 source and does not run a guest image. The remaining step folders are implementation, boot, or validation steps.

## Fixed Architecture

The current milestone is:

```text
conventional x86 RAM layout -> shared DDR5 subchannels -> CXL slow path -> boots -> NUMA visible
```

The current physical layout is:

| Region | Start | End Exclusive | Size | Meaning |
| --- | ---: | ---: | ---: | --- |
| Fast low RAM | `0x0000000000` | `0x00c0000000` | 3GiB | ordinary system RAM below the x86 PCI hole |
| Reserved/hole | `0x00c0000000` | `0x0100000000` | 1GiB | unmapped x86 platform hole |
| Fast high RAM | `0x0100000000` | `0x1040000000` | 61GiB | ordinary system RAM remapped above the hole |
| Slow RAM | `0x1040000000` | `0x2040000000` | 64GiB | ordinary NUMA RAM reached through the CXL Type 3-like slow path |

The project uses `LargeMemoryX86Board` for large x86 full-system runs and
keeps stock `X86Board` on its documented 3GiB path. The CXL/two-tier memory
component is `TwoTierMemory`.

It exposes:

- `fast_ranges` and `slow_ranges`;
- two fast DDR5 controllers and two slow DDR5 controllers;
- two fast `RangeAddrMapper` objects and two slow `CxlMemLink` objects;
- `get_default_memory_ranges()` for project-local large-board setup;
- `get_mem_ports()` for Ruby directory routing;
- `get_memory_controllers()`;
- `get_uninterleaved_range()`;
- `get_numa_memory_ranges()` returning `{0: fast_ranges, 1: slow_ranges}` as
  project-local SRAT/SLIT metadata.

Both tiers use the same DDR5 model and the same controller static latency. The tier distinction is the CXL link on node `1`:

- fast and slow controllers: `static_frontend_latency="10ns"`, `static_backend_latency="10ns"`;
- slow only: `CxlMemLink` adds CXL.mem base latency, flit serialization, and queue residence time.

DDR timing parameters, burst timing, bank geometry, and address mapping are not changed.

## Survey Summary

The implementation follows stdlib `X86Board`, not legacy `configs/common/FSConfig.py`.

Important files:

- `/home/cc/inmem/gem5/src/python/gem5/components/boards/x86_board.py`
- `/home/cc/inmem/gem5/src/python/gem5/components/boards/large_mem_x86.py`
- `/home/cc/inmem/gem5/src/python/gem5/components/memory/`
- `/home/cc/inmem/gem5/src/python/gem5/components/cachehierarchies/ruby/mesi_two_level_cache_hierarchy.py`
- `/home/cc/inmem/gem5/src/python/gem5/components/cachehierarchies/ruby/caches/mesi_two_level/directory.py`
- `/home/cc/inmem/gem5/src/arch/x86/bios/ACPI.py`
- `/home/cc/inmem/gem5/src/arch/x86/bios/acpi.hh`
- `/home/cc/inmem/gem5/src/arch/x86/bios/acpi.cc`
- `/home/cc/inmem/gem5/src/arch/x86/fs_workload.cc`
- `/home/cc/inmem/gem5/src/arch/x86/linux/fs_workload.cc`

Ruby routing did not need a source refactor. `MESITwoLevelCacheHierarchy` creates one `Directory` per `(range, port)` pair returned by `board.get_mem_ports()`, and each directory owns one address range and forwards to the corresponding memory port.

## ACPI NUMA Design

Before SRAT/SLIT, Step 6 exposes both RAM ranges through E820 so Linux sees both as ordinary `System RAM`.

`LargeMemoryX86Board` adds minimal ACPI NUMA support:

- SRAT table serialization;
- SRAT processor local APIC affinity records;
- SRAT memory affinity records;
- SLIT table serialization;
- RSDT/XSDT entries for SRAT and SLIT.

The fixed NUMA map is:

- all CPUs/APIC IDs -> node `0`;
- fast memory -> node `0`;
- slow memory -> node `1`;
- node `1` is memory-only;
- SLIT local distance `10`, remote distance `20`.

The fast memory affinity covers the full low node range and is split around the
x86 PCI hole. E820 still carries the conventional low usable/reserved split:

- `[0x000000, 0xc0000000)` on node `0`;
- `[0x100000000, 0x1040000000)` on node `0`;
- `[0x1040000000, 0x2040000000)` on node `1`.

`LargeMemoryX86Board` keeps the SRAT low affinity anchored at zero so the
conventional sub-1MiB usable RAM remains covered by node `0`.

## Current Steps

The condensed workflow is:

1. `step_00_design_and_usage`: design, survey, patch order, usage, limitations.
2. `step_02_baseline_fs_config`: runnable single-memory x86 FS baseline.
3. `step_04_second_mem_ctrl`: add `TwoTierMemory` and validate two controllers/ranges.
4. `step_05_route_ranges_to_ctrls`: validate Ruby range-to-controller routing.
5. `step_06_guest_boot_with_two_ranges`: E820 exposes both RAM ranges to Linux.
6. `step_08_expose_fast_slow_as_numa_nodes`: add minimal SRAT/SLIT.
7. `step_09_validate_linux_numa`: boot Linux and validate guest NUMA with `numactl`, `lscpu`, sysfs, journal, and `numastat`.
8. `step_10_kvm_to_timing_switch`: package the KVM boot to Timing ROI workflow.
9. `step_11_microbench_validation`: run the tiny NUMA placement workload packaging path.

The former documentation-only survey, design, ACPI-plumbing, and cleanup/usage material was merged here.

## Patch Order

Apply source patches in this order from a clean gem5 tree:

```sh
cd /home/cc/inmem/gem5
git apply ../step_04_second_mem_ctrl/patches/step_04_second_mem_ctrl.patch
scons build/ALL/gem5.opt -j$(nproc)

git apply ../step_06_guest_boot_with_two_ranges/patches/step_06_guest_boot_with_two_ranges.patch
scons build/ALL/gem5.opt -j$(nproc)

git apply ../step_08_expose_fast_slow_as_numa_nodes/patches/step_08_expose_fast_slow_as_numa_nodes.patch
scons build/ALL/gem5.opt -j$(nproc)
```

Or use:

```sh
cd /home/cc/inmem
step_00_design_and_usage/scripts/apply_source_patches.sh
```

To check that the patch files match the current tree:

```sh
cd /home/cc/inmem
step_00_design_and_usage/scripts/check_patch_stack_current_tree.sh \
  | tee step_00_design_and_usage/artifacts/patch_stack_check.txt
```

Expected result:

```text
Patch stack matches the current gem5 source tree.
```

## Run Order

Use these validation stages after applying the patches:

```sh
cd /home/cc/inmem

gem5/build/ALL/gem5.opt \
  --outdir=step_04_second_mem_ctrl/artifacts/m5out \
  step_04_second_mem_ctrl/scripts/x86_two_tier_kvm_timing.py \
  --max-ticks 1
python3 step_04_second_mem_ctrl/scripts/check_two_tier_config.py \
  step_04_second_mem_ctrl/artifacts/m5out/config.ini

gem5/build/ALL/gem5.opt \
  --outdir=step_05_route_ranges_to_ctrls/artifacts/fast_m5out \
  step_05_route_ranges_to_ctrls/scripts/two_tier_ruby_traffic.py \
  --tier fast --bytes 65536
gem5/build/ALL/gem5.opt \
  --outdir=step_05_route_ranges_to_ctrls/artifacts/slow_m5out \
  step_05_route_ranges_to_ctrls/scripts/two_tier_ruby_traffic.py \
  --tier slow --bytes 65536
python3 step_05_route_ranges_to_ctrls/scripts/check_route_ranges.py \
  --fast-outdir step_05_route_ranges_to_ctrls/artifacts/fast_m5out \
  --slow-outdir step_05_route_ranges_to_ctrls/artifacts/slow_m5out

gem5/build/ALL/gem5.opt \
  --outdir=step_06_guest_boot_with_two_ranges/artifacts/m5out \
  step_06_guest_boot_with_two_ranges/scripts/x86_two_tier_e820_boot.py
python3 step_06_guest_boot_with_two_ranges/scripts/check_e820_boot.py \
  step_06_guest_boot_with_two_ranges/artifacts/m5out

gem5/build/ALL/gem5.opt \
  --outdir=step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out \
  step_08_expose_fast_slow_as_numa_nodes/scripts/x86_two_tier_numa_config.py \
  --max-ticks 1
python3 step_08_expose_fast_slow_as_numa_nodes/scripts/check_acpi_numa_config.py \
  step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out

gem5/build/ALL/gem5.opt \
  --outdir=step_09_validate_linux_numa/artifacts/m5out \
  step_09_validate_linux_numa/scripts/x86_two_tier_numa_boot.py
python3 step_09_validate_linux_numa/scripts/check_linux_numa.py \
  step_09_validate_linux_numa/artifacts/m5out
```

To re-check existing artifacts:

```sh
cd /home/cc/inmem
step_00_design_and_usage/scripts/validate_existing_artifacts.sh \
  | tee step_00_design_and_usage/artifacts/final_validation_summary.txt
```

## Guest Image

The current local guest image is:

```sh
/home/cc/.cache/gem5/x86-ubuntu-24.04-numactl.img
```

It was created from the Ubuntu 24.04 gem5 image and customized with the `numactl` package. The configs keep using the gem5 workload resource for the kernel and boot wrapper, then replace only the `disk_image` parameter with this local `DiskImageResource`.

The working offline install command on `parla-march` used an explicit `.deb` filename:

```sh
sudo virt-customize \
  -a ~/.cache/gem5/x86-ubuntu-24.04-numactl.img \
  --upload /tmp/debs/numactl_2.0.18-1ubuntu0.24.04.1_amd64.deb:/tmp/ \
  --run-command "dpkg -i /tmp/numactl_2.0.18-1ubuntu0.24.04.1_amd64.deb"
```

Avoid passing an unexpanded wildcard to `--upload`. This failed:

```sh
sudo virt-customize \
  -a ~/.cache/gem5/x86-ubuntu-24.04-numactl.img \
  --upload /tmp/debs/numactl_*.deb:/tmp/ \
  --run-command "dpkg -i /tmp/numactl_*.deb"
```

`virt-customize` tried to open the literal path `/tmp/debs/numactl_*.deb` and reported `No such file or directory`.

## Modeling Statement

This models ordinary Linux-visible system RAM on two NUMA nodes. Node `1` traffic crosses an abstract CXL Type 3 HDM-H-like CXL.mem link before reaching DDR5-backed media. It does not model guest CXL enumeration, CXL.io timing, CXL.cache, pmem, DAX, devdax, `/dev/dax`, a custom guest driver, or a guest kernel patch.

## Limitations

- This is fixed to two tiers and two NUMA nodes.
- Node `1` is memory-only; all CPUs/APIC IDs map to node `0`.
- SRAT/SLIT support is intentionally minimal.
- The slow tier extra latency is modeled in `CxlMemLink`, not by inflating slow `MemCtrl.static_frontend_latency` or `MemCtrl.static_backend_latency`.
- DDR5 advanced features are not expanded or modified.
- The Ubuntu image blocks unprivileged `dmesg`; Step 9 uses serial and `journalctl -k` for kernel NUMA evidence.
- Linux AutoNUMA is enabled by default in the observed guest. Disable it with `numa_balancing=0` or `echo 0 > /proc/sys/kernel/numa_balancing` for experiments that require fixed placement.

## What Remains

The first NUMA milestone is complete. Future work can add experiment-specific CPU models, checkpointing, larger workloads, or additional guest image packages.
