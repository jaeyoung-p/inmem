# Step 4 Notes

- `TwoTierMemory` is a historical name; node0 is one local DDR5 node, not two
  fast tiers.
- Node1 differences are modeled in `CxlMemLink`, not by inflating DDR5 media
  latency.
- Config-generation validation is enough for this step; guest NUMA validation
  happens later.
- gem5 may warn that DDR5 device capacity exceeds assigned interleaved ranges;
  that is expected for this model.
