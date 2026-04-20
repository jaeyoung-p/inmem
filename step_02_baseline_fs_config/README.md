# Step 2: Baseline FS Config

## Goal

Create a minimal runnable x86 full-system baseline that boots Linux with KVM fast-forward and switches to a Timing CPU after boot.

This step keeps the current single-memory configuration. There are no NUMA changes and no gem5 source patches.

## Files Touched

Created under the project root:

- `IMPLEMENTATION_PLAN.md`
- `step_02_baseline_fs_config/README.md`
- `step_02_baseline_fs_config/NOTES.md`
- `step_02_baseline_fs_config/artifacts/`
- `step_02_baseline_fs_config/patches/`
- `step_02_baseline_fs_config/scripts/x86_baseline_kvm_timing.py`
- `step_02_baseline_fs_config/scripts/check_baseline_config.py`

No files under `gem5/` are modified in this step.

## Exact Code Changes

### Baseline config

`scripts/x86_baseline_kvm_timing.py` is based on gem5's existing no-perf KVM example:

- `X86Board`
- `MESITwoLevelCacheHierarchy`
- `SingleChannelDDR4_2400(size="3GiB")`
- `SimpleSwitchableProcessor(starting_core_type=KVM, switch_core_type=TIMING)`
- `proc.core.usePerf = False` on KVM cores
- Ubuntu 24.04 FS workload resource: `x86-ubuntu-24.04-boot-with-systemd`, version `5.0.0`
- local disk override: `/home/cc/.cache/gem5/x86-ubuntu-24.04-numactl.img`
- after-boot exit handler calls `simulator.switch_processor()`

### Baseline checker

`scripts/check_baseline_config.py` parses `config.ini` and checks:

- one 3GiB RAM range plus the existing x86 I/O bridge range
- one `MemCtrl`
- one Ruby directory
- the Ruby directory owns the 3GiB RAM range and connects to the single `MemCtrl`

## How To Run

From the project root:

```sh
cd /home/cc/inmem
rm -rf step_02_baseline_fs_config/artifacts/m5out
gem5/build/ALL/gem5.opt \
  --outdir=step_02_baseline_fs_config/artifacts/m5out \
  step_02_baseline_fs_config/scripts/x86_baseline_kvm_timing.py
```

Then validate the generated config:

```sh
python3 step_02_baseline_fs_config/scripts/check_baseline_config.py \
  step_02_baseline_fs_config/artifacts/m5out/config.ini
```

Useful artifacts after a successful run:

- `step_02_baseline_fs_config/artifacts/m5out/config.ini`
- `step_02_baseline_fs_config/artifacts/m5out/config.json`
- `step_02_baseline_fs_config/artifacts/m5out/stats.txt`
- `step_02_baseline_fs_config/artifacts/m5out/board.pc.com_1.device`

## How To Validate

Expected console behavior:

- gem5 starts with KVM cores.
- guest kernel boots.
- first handler prints `First exit: kernel booted`.
- after-boot handler prints `Switching from KVM to Timing CPU`.
- final handler exits after the boot script.

Expected config checker output:

```text
baseline config validation passed
- one 3GiB ordinary RAM range
- one MemCtrl
- one Ruby directory mapped to that MemCtrl
```

## Validation Performed

The baseline was run from `/home/cc/inmem` with:

```sh
gem5/build/ALL/gem5.opt \
  --outdir=step_02_baseline_fs_config/artifacts/m5out \
  step_02_baseline_fs_config/scripts/x86_baseline_kvm_timing.py
```

Observed console milestones:

```text
First exit: kernel booted
Second exit: after_boot.sh started
Switching from KVM to Timing CPU
switching cpus
Third exit: Exit Handler AfterBootScriptExitHandler called.
```

The config checker was run with:

```sh
python3 step_02_baseline_fs_config/scripts/check_baseline_config.py \
  step_02_baseline_fs_config/artifacts/m5out/config.ini
```

Observed checker output:

```text
baseline config validation passed
- one 3GiB ordinary RAM range
- one MemCtrl
- one Ruby directory mapped to that MemCtrl
```

The generated serial log confirms Ubuntu 24.04 reached multi-user mode, logged in automatically on `ttyS0`, and ran `after_boot.sh`.

## Expected Result

The baseline demonstrates that the unmodified single-memory x86 FS path works before adding two physical RAM ranges or NUMA. Later steps will compare their generated configs and guest-visible behavior against this baseline.
