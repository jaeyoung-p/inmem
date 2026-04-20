# Step 5: Route Ranges To Controllers

## Goal

Validate that Ruby routes the fixed fast and slow RAM ranges to the intended directories and memory controllers using address-range ownership, not object existence alone.

This step does not patch gem5 source. It adds scripts that inspect `config.ini`, inspect `config.json`, and run synthetic Ruby traffic against each range.

## Files Touched

Created under the project root:

- `step_05_route_ranges_to_ctrls/README.md`
- `step_05_route_ranges_to_ctrls/NOTES.md`
- `step_05_route_ranges_to_ctrls/artifacts/`
- `step_05_route_ranges_to_ctrls/patches/`
- `step_05_route_ranges_to_ctrls/scripts/two_tier_ruby_traffic.py`
- `step_05_route_ranges_to_ctrls/scripts/check_route_ranges.py`

Patched gem5 source:

- None.

## Exact Code Changes

`two_tier_ruby_traffic.py` defines a step-local `TwoTierTrafficBoard`, a tiny subclass of gem5's `TestBoard`, only to preserve `TwoTierMemory.get_default_memory_ranges()` instead of collapsing memory to one contiguous range.

The script uses:

- `TwoTierMemory`
- `MESITwoLevelCacheHierarchy`
- one `LinearGenerator`
- fast traffic range `[0x0, 0x10000)`
- slow traffic range `[0x1040000000, 0x1040010000)`

`check_route_ranges.py` validates:

- each RAM range maps to exactly one Ruby directory
- each directory owns exactly one RAM range
- `config.ini` shows the directory `memory_out_port` connected to the correct `MemCtrl.port`
- `config.ini` shows the controller `port` connected back to the correct directory
- `config.json` shows the same directory range and port peer mapping
- fast-only traffic increments `board.memory.fast_ctrl.readReqs` and the fast directory `requestToMemory` count only
- slow-only traffic increments `board.memory.slow_ctrl.readReqs` and the slow directory `requestToMemory` count only

## How To Run

Run fast-range synthetic traffic:

```sh
cd /home/cc/inmem
rm -rf step_05_route_ranges_to_ctrls/artifacts/fast_m5out
gem5/build/ALL/gem5.opt \
  --outdir=step_05_route_ranges_to_ctrls/artifacts/fast_m5out \
  step_05_route_ranges_to_ctrls/scripts/two_tier_ruby_traffic.py \
  --tier fast \
  --bytes 65536
```

Run slow-range synthetic traffic:

```sh
cd /home/cc/inmem
rm -rf step_05_route_ranges_to_ctrls/artifacts/slow_m5out
gem5/build/ALL/gem5.opt \
  --outdir=step_05_route_ranges_to_ctrls/artifacts/slow_m5out \
  step_05_route_ranges_to_ctrls/scripts/two_tier_ruby_traffic.py \
  --tier slow \
  --bytes 65536
```

Validate routing:

```sh
python3 step_05_route_ranges_to_ctrls/scripts/check_route_ranges.py \
  --fast-outdir step_05_route_ranges_to_ctrls/artifacts/fast_m5out \
  --slow-outdir step_05_route_ranges_to_ctrls/artifacts/slow_m5out
```

## How To Validate

Expected checker output:

```text
route validation passed
- config.ini has exactly one Ruby directory for the fast range
- config.ini has exactly one Ruby directory for the slow range
- config.json directory port peers match the fast/slow MemCtrls
- fast-only traffic increments fast_ctrl and fast directory stats only
- slow-only traffic increments slow_ctrl and slow directory stats only
```

Expected key stats:

```text
fast run:
  board.memory.fast_ctrl.readReqs > 0
  board.memory.slow_ctrl.readReqs = 0
  board.cache_hierarchy.ruby_system.directory_controllers0.requestToMemory.m_msg_count > 0

slow run:
  board.memory.fast_ctrl.readReqs = 0
  board.memory.slow_ctrl.readReqs > 0
  board.cache_hierarchy.ruby_system.directory_controllers1.requestToMemory.m_msg_count > 0
```

Observed in this workspace with `--bytes 65536`:

```text
fast run:
  board.memory.fast_ctrl.readReqs = 586
  board.memory.slow_ctrl.readReqs = 0
  directory_controllers0.requestToMemory.m_msg_count = 586

slow run:
  board.memory.fast_ctrl.readReqs = 0
  board.memory.slow_ctrl.readReqs = 435
  directory_controllers1.requestToMemory.m_msg_count = 435
```

## Expected Result

Ruby keeps its existing address-range based routing. The fast range is owned by the fast directory and reaches `fast_ctrl`; the slow range is owned by the slow directory and reaches `slow_ctrl`.

Guest-visible memory remains unchanged in this step. Step 6 patches E820 so Linux sees both RAM ranges.
