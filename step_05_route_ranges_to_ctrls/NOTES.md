# Step 5 Notes

## Assumptions

- Step 4's `TwoTierMemory` patch is already applied and built.
- Synthetic traffic is acceptable for routing validation because this step is about Ruby address decoding and controller reachability, not guest Linux behavior.
- Read-only linear traffic is enough to prove routing because a miss to either fixed address range must traverse the owning Ruby directory and backing `MemCtrl`.

## Open Questions

- None for this step.

## Uncertainties

- The exact read count differs between fast and slow runs because the CXL link changes completion timing and the generator stops through normal simulation exit behavior. The validation only requires active-side traffic to be positive and inactive-side traffic to be zero.
- This step proves routing through Ruby and `MemCtrl` stats. It does not prove Linux can allocate from the slow range; that is Step 6 and later.

## Out Of Scope

- E820 changes
- ACPI SRAT/SLIT
- Linux NUMA visibility
- NUMA allocation policy
- performance interpretation of the fast/slow read-count difference
