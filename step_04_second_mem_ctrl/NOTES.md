# Step 4 Notes

## Assumptions

- Each tier initially has one controller/channel, so the component is named `TwoTierMemory`.
- `DDR5_6400_4x8_32GiB` is available in this gem5 tree and is used for both tiers.
- The slow tier difference is intentionally kept outside the DDR5 media and modeled by the CXL link.
- A short `--max-ticks 1` run is sufficient for this step because validation is based on generated gem5 config output, not guest boot behavior.
- `DDR5_6400_4x8_32GiB` is a Python DRAM-interface subclass and appears in `config.ini` as the C++ base type `DRAMInterface`; validation checks the DDR5-derived timing and geometry fields instead.

## Open Questions

- None for this step.

## Uncertainties

- DDR5 advanced feature coverage is not evaluated here. This step only checks that the chosen DDR5 interface instantiates, has matching fast/slow timing fields, and that the slow path includes CXL link latency.
- E820 still needs Step 6 before Linux can see the slow range as System RAM.
- NUMA still needs Step 8 before Linux can expose separate nodes.

## Out Of Scope

- E820 multi-range guest exposure
- SRAT/SLIT
- guest NUMA validation
- traffic-level routing validation beyond config-level directory/controller mapping
- multi-channel tier support
