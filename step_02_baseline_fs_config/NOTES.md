# Step 2 Notes

## Assumptions

- The local host allows KVM through `/dev/kvm`.
- The existing `gem5/build/ALL/gem5.opt` binary includes the MESI Two Level Ruby protocol.
- The Ubuntu workload resource `x86-ubuntu-24.04-boot-with-systemd` version `5.0.0` is obtainable through gem5 resources, and the config overrides its disk with `/home/cc/.cache/gem5/x86-ubuntu-24.04-numactl.img`.
- The single-memory baseline intentionally uses DDR4 because it mirrors the existing gem5 no-perf example. DDR5 is introduced in Step 4 with `TwoTierMemory`.

## Open Questions

- None for the baseline config. Guest command injection for later validation steps should be revisited after confirming the resource runscript behavior from this baseline.

## Uncertainties

- The local full boot completed successfully in this step.
- Future full-system runs can still take several minutes depending on host KVM performance and whether gem5 resources are already cached.
- If KVM permission fails on another host, use the same command after fixing host group/device permissions; do not change the baseline config to avoid masking the intended boot flow.

## Things Deliberately Out Of Scope

- two memory ranges
- second memory controller
- DDR5 tiered memory
- guest NUMA visibility
- E820 changes
- ACPI SRAT/SLIT changes

## Validation Record

- `config.ini`, `config.json`, serial output, and `stats.txt` were generated under `step_02_baseline_fs_config/artifacts/m5out/`.
- The baseline config checker passed.
- The serial log reached `Ubuntu 24.04 LTS gem5 ttyS0`, automatic login, `In after_boot.sh...`, and `Done running script from gem5-bridge, exiting.`
- gem5 source remained unchanged.
