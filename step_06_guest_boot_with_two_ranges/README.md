# Step 6: Guest Boot With Two Ranges

## Goal

Boot the x86 full-system guest with the fixed two-tier RAM layout and expose both RAM ranges through the guest E820 map.

Expected E820 behavior:

- Linux sees both ranges as ordinary `System RAM`.
- The slow range is still normal Linux-visible RAM; CXL is modeled only as the host-to-memory timing path, not as DAX, pmem, devdax, or guest-visible device memory.

## Files Touched

Gem5 source patched:

- `gem5/src/python/gem5/components/boards/large_mem_x86.py`

Step-local files:

- `scripts/x86_two_tier_e820_boot.py`
- `scripts/check_e820_boot.py`
- `patches/step_06_guest_boot_with_two_ranges.patch`
- `artifacts/m5out/`
- `artifacts/validation_summary.txt`

## Exact Code Changes

`LargeMemoryX86Board` replaces stock `X86Board`'s single-range E820 table with
one that advertises every real data range returned by `TwoTierMemory`.

The replacement logic:

- preserves the conventional low usable region `[0, 639KiB)`;
- preserves the reserved low-memory region `[0x9fc00, 1MiB)`;
- iterates over `self.mem_ranges`;
- skips the board's internal I/O marker range at `[0xc0000000, 0xc0100000)`;
- trims the first MiB from any RAM range starting at zero;
- emits each remaining RAM range as E820 type `1`, usable RAM;
- emits the rest of the 3-4GiB PCI hole as E820 type `2`, reserved;
- reserves `[0xffff0000, 0x100000000)` for m5ops.

With `TwoTierMemory`, the E820 RAM entries become:

- fast low RAM: `[0x00100000, 0x00c0000000)`, the usable part of `[0, 3GiB)`;
- fast high RAM: `[0x0100000000, 0x1040000000)`;
- slow RAM: `[0x1040000000, 0x2040000000)`, fixed `[65GiB, 129GiB)`.

## How to Apply

From the project root:

```sh
cd /home/cc/inmem/gem5
git apply ../step_06_guest_boot_with_two_ranges/patches/step_06_guest_boot_with_two_ranges.patch
```

This patch is meant to be applied after Step 4, which adds `TwoTierMemory` and
the large-memory board path.

## How to Build

```sh
cd /home/cc/inmem/gem5
scons build/ALL/gem5.opt -j$(nproc)
```

## How to Run

```sh
cd /home/cc/inmem
rm -rf step_06_guest_boot_with_two_ranges/artifacts/m5out
gem5/build/ALL/gem5.opt \
  --outdir=step_06_guest_boot_with_two_ranges/artifacts/m5out \
  step_06_guest_boot_with_two_ranges/scripts/x86_two_tier_e820_boot.py
```

The config includes readfile commands for later manual/interactive guest inspection:

```sh
cat /proc/iomem
cat /proc/meminfo
cat /sys/devices/system/node/online || true
ls -d /sys/devices/system/node/node* || true
dmesg | grep -Ei "e820|BIOS-e820|System RAM|numa|srat|slit" || true
```

In the automated run, the Step 6 validation uses `config.ini` and the kernel boot log because the Ubuntu after-boot helper reaches the automatic-login boundary before echoing the readfile payload to serial.

## How to Validate

```sh
cd /home/cc/inmem
python3 step_06_guest_boot_with_two_ranges/scripts/check_e820_boot.py \
  step_06_guest_boot_with_two_ranges/artifacts/m5out
```

Expected result:

```text
Step 6 E820 boot validation passed
- config.ini exposes fast RAM as E820 usable after the low 1MiB
- config.ini exposes slow RAM as E820 usable at 65GiB-129GiB
- Linux boot log reports both ranges as BIOS-e820 usable
```

Useful direct checks:

```sh
rg -n "BIOS-e820|No NUMA|Faking a node|0000000100000000" \
  step_06_guest_boot_with_two_ranges/artifacts/m5out/board.pc.com_1.device

rg -n "\[board.workload.e820_table.entries|^addr=|^size=|^range_type=" \
  step_06_guest_boot_with_two_ranges/artifacts/m5out/config.ini
```

Expected evidence:

- E820 usable fast RAM entry ending at `0x000000007fffffff`;
- E820 usable slow RAM entry from `0x0000001040000000` to `0x000000203fffffff`;
