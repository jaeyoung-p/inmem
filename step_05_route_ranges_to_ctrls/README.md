# Step 5: Route Ranges to Controllers

## Purpose

Validate that Ruby routes traffic by address range to the intended directory
and memory controller.

## Files

- `scripts/two_tier_ruby_traffic.py`
- `scripts/check_route_ranges.py`

## Run

Node0 traffic:

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_05_route_ranges_to_ctrls/artifacts/m5out_x86_node0_8ch_node0 \
  step_05_route_ranges_to_ctrls/scripts/two_tier_ruby_traffic.py \
  --tier node0
```

Node1/CXL traffic:

```sh
gem5/build/X86/gem5.opt \
  --outdir=step_05_route_ranges_to_ctrls/artifacts/m5out_x86_node0_8ch_slow \
  step_05_route_ranges_to_ctrls/scripts/two_tier_ruby_traffic.py \
  --tier slow
```

## Validate

```sh
python3 step_05_route_ranges_to_ctrls/scripts/check_route_ranges.py \
  --fast-outdir step_05_route_ranges_to_ctrls/artifacts/m5out_x86_node0_8ch_node0 \
  --slow-outdir step_05_route_ranges_to_ctrls/artifacts/m5out_x86_node0_8ch_slow
```

Expected result:

- node0 traffic reaches node0 controllers only;
- slow traffic crosses `CxlMemLink` and reaches node1 controllers only;
- each Ruby directory owns exactly one address range.
