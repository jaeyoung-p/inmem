# Step 10: KVM-to-Timing ROI Switch

## Purpose

Package the measurement control flow:

- boot Linux under KVM;
- switch to Timing CPU only at the ROI boundary;
- reset stats immediately after the switch;
- dump stats when the readfile script finishes.

No gem5 source is patched in this step.

## Files

- `scripts/x86_two_tier_kvm_to_timing_roi.py`
- `scripts/check_kvm_timing_config.py`

## Hypercalls

- `1`: kernel booted, continue under KVM.
- `2`: after-boot script starts, switch to Timing and reset stats.
- `3`: readfile script finished, dump stats and exit.

Step 12 uses a later ROI hypercall number for its benchmark-specific switch.

## Run

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_10_kvm_to_timing_switch/artifacts/m5out_x86_node0_8ch \
  step_10_kvm_to_timing_switch/scripts/x86_two_tier_kvm_to_timing_roi.py \
  --max-ticks 1
```

## Validate

```sh
python3 step_10_kvm_to_timing_switch/scripts/check_kvm_timing_config.py \
  step_10_kvm_to_timing_switch/artifacts/m5out_x86_node0_8ch
```
