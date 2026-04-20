# Step 4: Second Memory Controller

## Goal

Instantiate the two-tier memory component while reusing the same DDR5 media model for both tiers.

This step introduces `TwoTierMemory` and validates that gem5 config output contains:

- three ordinary RAM ranges: fast low, fast high, and slow
- four DDR5 interfaces
- four `MemCtrl` instances
- CXL-link latency differences only
- four Ruby directories, one per exposed tier channel

Large x86 full-system setup is handled by `LargeMemoryX86Board`, not by
weakening stock `X86Board`'s documented 3GiB path.

## Files Touched

Created under the project root:

- `step_04_second_mem_ctrl/README.md`
- `step_04_second_mem_ctrl/NOTES.md`
- `step_04_second_mem_ctrl/artifacts/`
- `step_04_second_mem_ctrl/patches/`
- `step_04_second_mem_ctrl/scripts/x86_two_tier_kvm_timing.py`
- `step_04_second_mem_ctrl/scripts/check_two_tier_config.py`

Patched gem5 source:

- `/home/cc/inmem/gem5/src/python/gem5/components/memory/tiered.py`
- `/home/cc/inmem/gem5/src/python/gem5/components/memory/split_range.py`
- `/home/cc/inmem/gem5/src/python/gem5/components/memory/__init__.py`
- `/home/cc/inmem/gem5/src/python/SConscript`
- `/home/cc/inmem/gem5/src/python/gem5/components/boards/large_mem_x86.py`
- `/home/cc/inmem/gem5/src/python/gem5/components/boards/x86_board.py`

Generated patch:

- `step_04_second_mem_ctrl/patches/step_04_second_mem_ctrl.patch`

## Exact Code Changes

### `TwoTierMemory`

Added `TwoTierMemory` under `gem5.components.memory`.

Fixed ranges:

```python
fast_ranges = [
    AddrRange(start=0, size="3GiB"),
    AddrRange(start=0x100000000, size="61GiB"),
]
slow_ranges = [AddrRange(start=0x1040000000, size="64GiB")]
```

Both tiers use two `DDR5_6400_4x8_32GiB` subchannels.

Controller latency:

```python
fast_ctrl.static_frontend_latency = "10ns"
fast_ctrl.static_backend_latency = "10ns"
slow_ctrl.static_frontend_latency = "10ns"
slow_ctrl.static_backend_latency = "10ns"
```

No low-level DDR5 timing parameters are modified.

`TwoTierMemory` exposes:

- `fast_ranges`
- `slow_ranges`
- `fast_ctrls`
- `slow_ctrls`
- `fast_addr_mappers`
- `slow_cxl_links`
- `get_default_memory_ranges()` as a project-local large-board range hook
- `get_numa_memory_ranges()` as project-local SRAT/SLIT metadata
- `get_mem_ports()`
- `get_memory_controllers()`
- `get_mem_interfaces()`
- `get_uninterleaved_range()`

### Large x86 full-system board

Stock `X86Board` remains limited to 3GiB, matching upstream documentation.
Large two-tier runs use `LargeMemoryX86Board`.

`LargeMemoryX86Board` checks whether the memory component provides
`get_default_memory_ranges()`. If present, the board uses those explicit ranges
and passes them to `memory.set_memory_range(...)`.

If absent and memory is larger than 3GiB, the board splits ordinary RAM into
`[0, 3GiB)` and `[4GiB, 4GiB + excess)`. Stock single-range memory wrappers
must be replaced with `SplitRangeChanneledMemory` for that ordinary large-RAM
case.

## How To Apply

The source tree is already patched in this workspace. To apply this step elsewhere:

```sh
cd /home/cc/inmem/gem5
git apply ../step_04_second_mem_ctrl/patches/step_04_second_mem_ctrl.patch
```

## How To Build

```sh
cd /home/cc/inmem/gem5
scons build/ALL/gem5.opt -j$(nproc)
```

## How To Run

Use a short run to instantiate and dump config files:

```sh
cd /home/cc/inmem
rm -rf step_04_second_mem_ctrl/artifacts/m5out
gem5/build/ALL/gem5.opt \
  --outdir=step_04_second_mem_ctrl/artifacts/m5out \
  step_04_second_mem_ctrl/scripts/x86_two_tier_kvm_timing.py \
  --max-ticks 1
```

Validate config output:

```sh
python3 step_04_second_mem_ctrl/scripts/check_two_tier_config.py \
  step_04_second_mem_ctrl/artifacts/m5out/config.ini
```

## How To Validate

Expected checker output:

```text
two-tier config validation passed
- node 0 totals 64GiB across low/high fast RAM ranges
- node 1 exposes one 64GiB slow RAM range
- node 0 low/high RAM is aggregated through two fast RangeAddrMappers
- each NUMA node has two DDR5_6400_4x8_32GiB subchannels
- node 1 traffic crosses two CxlMemLink flit queues
- slow controllers match fast DDR5 latency; CXL delay is in CxlMemLink
- four Ruby directories exist, one per exposed tier channel
```

Expected `config.ini` facts:

- `board.mem_ranges=0:3221225472 4294967296:69793218560 69793218560:138512695296 3221225472:3222274048`
- `board.memory.fast_ctrls0.type=MemCtrl`
- `board.memory.fast_ctrls1.type=MemCtrl`
- `board.memory.slow_ctrls0.type=MemCtrl`
- `board.memory.slow_ctrls1.type=MemCtrl`
- all four DRAM interfaces show matching DDR5-derived timing and geometry fields, including `tCK=312`, `burst_length=16`, `device_bus_width=8`, `device_size=4294967296`, `devices_per_rank=4`, `ranks_per_channel=2`, and `bank_groups_per_rank=8`
- all four controllers use static frontend/backend latency of `10000` ticks
- slow CXL links show `flit_size_bytes=256`, `m2s_latency=80000`, `s2m_latency=80000`, and 256-flit queue depths

The Python `DDR5_6400_4x8_32GiB` class serializes as the C++ base `DRAMInterface` in `config.ini`. The checker therefore validates stable DDR5 timing and geometry fields instead of expecting the Python class name as the serialized type.

## Expected Result

The gem5 configuration contains conventional x86 ordinary RAM ranges backed by four DDR5 `MemCtrl` instances. Ruby creates one directory per exposed tier channel; node `1` directories route through `CxlMemLink` before the slow DDR5 controllers.

Linux guest visibility is not validated in this step. Before Step 6, the guest memory map is not expected to expose the slow range as System RAM.
