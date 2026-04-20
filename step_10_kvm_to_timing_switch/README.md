# Step 10: KVM to Timing Switch

## Goal

Document and package the exact control flow for the intended measurement workflow:

- boot Linux with KVM for fast-forward;
- switch to Timing CPU only after the guest reaches `after_boot.sh`;
- reset stats at the region-of-interest boundary;
- run the normal Linux workload;
- dump stats when the readfile script finishes.

No gem5 source is patched in this step.

## Files Touched

Step-local files:

- `scripts/x86_two_tier_kvm_to_timing_roi.py`
- `scripts/check_kvm_timing_config.py`
- `artifacts/m5out/`
- `artifacts/validation_summary.txt`

## Exact Code Changes

`x86_two_tier_kvm_to_timing_roi.py` creates the same fixed two-tier x86 FS machine used in Steps 8 and 9:

- `TwoTierMemory`;
- Ruby `MESITwoLevelCacheHierarchy`;
- two starting `X86KvmCPU` cores;
- two switched `BaseTimingSimpleCPU` cores;
- Ubuntu 24.04 FS workload with readfile contents.

The exit handlers implement the control flow:

- hypercall `1`: kernel booted under KVM; continue;
- hypercall `2`: `after_boot.sh` starts; call `simulator.switch_processor()` and `m5.stats.reset()`;
- hypercall `3`: readfile script finished; call `m5.stats.dump()` and exit.

The readfile body is a placeholder ROI. It currently prints the NUMA node state and then exits. Replace the placeholder block with the measurement command, keeping the same hypercall-driven boundaries.

## How to Run

Config-generation smoke run:

```sh
cd /home/cc/inmem
rm -rf step_10_kvm_to_timing_switch/artifacts/m5out
gem5/build/ALL/gem5.opt \
  --outdir=step_10_kvm_to_timing_switch/artifacts/m5out \
  step_10_kvm_to_timing_switch/scripts/x86_two_tier_kvm_to_timing_roi.py \
  --max-ticks 1
```

Full KVM-to-Timing ROI run:

```sh
cd /home/cc/inmem
rm -rf step_10_kvm_to_timing_switch/artifacts/m5out
gem5/build/ALL/gem5.opt \
  --outdir=step_10_kvm_to_timing_switch/artifacts/m5out \
  step_10_kvm_to_timing_switch/scripts/x86_two_tier_kvm_to_timing_roi.py
```

The full run is expected to boot quickly under KVM, then slow down after the Timing switch. That is intentional; only the post-switch ROI should be used for measurement.

Optional CXL slow-path knobs are available for sweeps: `--cxl-flit-size`, `--cxl-link-bandwidth`, `--cxl-base-latency`, and `--cxl-queue-depth-flits`.

## How to Validate

For the smoke run:

```sh
cd /home/cc/inmem
python3 step_10_kvm_to_timing_switch/scripts/check_kvm_timing_config.py \
  step_10_kvm_to_timing_switch/artifacts/m5out \
  | tee step_10_kvm_to_timing_switch/artifacts/validation_summary.txt
```

Expected result:

```text
Step 10 KVM-to-Timing config validation passed
- two KVM start cores are present
- two Timing switch cores are present and initially switched out
- two DDR5-derived DRAM interfaces are present
- SRAT/SLIT NUMA tables are present
- fast/slow DDR5 controller latency matches and CXL link latency parameters are preserved
```

For a full run, also check gem5 stdout for:

```text
First exit: kernel booted under KVM
Second exit: after_boot.sh started
Switching from KVM to Timing CPU
Resetting stats at ROI boundary
Third exit: after_boot.sh finished ROI script
Dumping stats at ROI boundary
```

## Checkpoint Option

A checkpoint can be added at the second hypercall before `simulator.switch_processor()` if repeated ROI runs need to avoid booting. Keep the checkpoint before the Timing switch, restore with the same memory/cache topology, then switch and reset stats at ROI start. This step documents that option but does not add checkpointing code, to keep the first milestone minimal.

## What Remains

Step 11 adds a tiny normal-NUMA workload to exercise node `0` versus node `1` allocation after the Timing switch.
