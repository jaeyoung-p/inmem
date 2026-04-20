# Step 2: Baseline FS Config

## Purpose

Provide a minimal x86 full-system baseline that boots Linux with KVM and
switches to a Timing CPU after boot. This step has no NUMA changes and no gem5
source patches.

## Files

- `scripts/x86_baseline_kvm_timing.py`
- `scripts/check_baseline_config.py`
- `README.md`
- `NOTES.md`

## Run

```sh
cd /home/cc/inmem
gem5/build/X86/gem5.opt \
  --outdir=step_02_baseline_fs_config/artifacts/m5out \
  step_02_baseline_fs_config/scripts/x86_baseline_kvm_timing.py
```

## Validate

```sh
python3 step_02_baseline_fs_config/scripts/check_baseline_config.py \
  step_02_baseline_fs_config/artifacts/m5out/config.ini
```

Expected baseline:

- `X86Board`;
- `MESITwoLevelCacheHierarchy`;
- one 3GiB memory range;
- one `MemCtrl`;
- one Ruby directory;
- KVM start cores and Timing switch cores.
