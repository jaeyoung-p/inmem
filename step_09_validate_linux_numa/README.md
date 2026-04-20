# Step 9: Validate Linux NUMA

## Goal

Boot the x86 full-system guest with the Step 8 SRAT/SLIT patch and validate that Linux recognizes the fixed two-tier RAM topology as NUMA:

- node 0: CPUs `0-1` plus fast RAM
- node 1: slow RAM only
- online node list: `0-1`

This step does not patch gem5 source. It only adds a boot/inspection config and a host-side log checker.

## Files Touched

Step-local files:

- `scripts/x86_two_tier_numa_boot.py`
- `scripts/check_linux_numa.py`
- `artifacts/m5out/`
- `artifacts/validation_summary.txt`

No files outside this step folder were modified for Step 9.

## Exact Code Changes

`x86_two_tier_numa_boot.py` builds the same two-tier x86 FS board as Step 8 and boots Ubuntu with KVM. Unlike measurement runs, it intentionally keeps KVM active while running guest inspection commands so validation finishes quickly and does not mix topology checks with Timing CPU measurement.

The config uses `/home/cc/.cache/gem5/x86-ubuntu-24.04-numactl.img`, a local Ubuntu image with `numactl` installed, while keeping the kernel and workload wrapper from the gem5 resource.

The guest readfile runs:

```sh
dmesg | grep -i numa
dmesg | grep -i srat
dmesg | grep -i slit
journalctl -k --no-pager | grep -i numa
journalctl -k --no-pager | grep -i srat
journalctl -k --no-pager | grep -i slit
numactl --hardware
lscpu
cat /sys/devices/system/node/online
cat /sys/devices/system/node/node*/cpulist
grep -E "MemTotal|MemFree" /sys/devices/system/node/node*/meminfo
numastat
```

`check_linux_numa.py` validates the serial artifact for:

- ACPI SRAT and SLIT discovery and reservation;
- SRAT CPU affinity records mapping APIC IDs `0` and `1` to node `0`;
- SRAT memory affinity records mapping fast RAM to node `0` and slow RAM to node `1`;
- Linux NUMA distance-table initialization;
- `lscpu` reporting two NUMA nodes;
- sysfs reporting online nodes `0-1`;
- node 0 containing CPUs `0-1`;
- node 1 being memory-only;
- node memory totals near 2 GiB and 1 GiB respectively.

## How to Run

From the project root:

```sh
cd /home/cc/inmem
rm -rf step_09_validate_linux_numa/artifacts/m5out
gem5/build/ALL/gem5.opt \
  --outdir=step_09_validate_linux_numa/artifacts/m5out \
  step_09_validate_linux_numa/scripts/x86_two_tier_numa_boot.py
```

## How to Validate

```sh
cd /home/cc/inmem
python3 step_09_validate_linux_numa/scripts/check_linux_numa.py \
  step_09_validate_linux_numa/artifacts/m5out \
  | tee step_09_validate_linux_numa/artifacts/validation_summary.txt
```

Expected result:

```text
Step 9 Linux NUMA validation passed
- Kernel boot log and journal show SRAT and SLIT parsing
- Linux reports online NUMA nodes 0-1
- lscpu reports CPUs 0-1 on node 0 and no CPUs on node 1
- node0 MemTotal is about 1952736 kB
- node1 MemTotal is about 1031208 kB
```

The stock Ubuntu image used here has `kernel.dmesg_restrict=1`, so unprivileged `dmesg` commands run but are denied. The same kernel messages are available in the serial boot log and through `journalctl -k`, both captured in the artifact.

The customized image includes `numactl`, so `numactl --hardware` and `numastat` are expected to run normally. Sysfs and `lscpu` remain additional topology evidence.

## Observed Result

The current implementation builds SRAT/SLIT and Linux parses the tables, but
the real boot does not yet pass. The Ubuntu 6.8 kernel panics during early
sparsemem setup after printing:

- `ACPI: SRAT`
- `ACPI: SLIT`
- `SRAT: PXM 0 -> APIC 0x00 -> Node 0`
- `SRAT: PXM 0 -> APIC 0x01 -> Node 0`
- `ACPI: SRAT: Node 0 PXM 0 [mem 0x00000000-0xbfffffff]`
- `ACPI: SRAT: Node 0 PXM 0 [mem 0x100000000-0x103fffffff]`
- `ACPI: SRAT: Node 1 PXM 1 [mem 0x1040000000-0x203fffffff]`
- `BUG: unable to handle page fault for address: 0000000000001010`
- `subsection_map_init`

## What Remains

The next debugging step is to isolate whether this is caused by gem5's SRAT
serialization, Linux sparsemem section-zero handling, or the large sparse x86
E820/SRAT combination. Step 10 packages the KVM boot/fast-forward to Timing CPU
measurement workflow. Step 11 adds a tiny normal-NUMA validation workload. Final
patch order and usage notes are in `step_00_design_and_usage`.
