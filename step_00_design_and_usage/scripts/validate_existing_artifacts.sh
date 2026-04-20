#!/bin/sh
set -eu

cd /home/cc/inmem

python3 step_04_second_mem_ctrl/scripts/check_two_tier_config.py \
  step_04_second_mem_ctrl/artifacts/m5out/config.ini

python3 step_05_route_ranges_to_ctrls/scripts/check_route_ranges.py \
  --fast-outdir step_05_route_ranges_to_ctrls/artifacts/fast_m5out \
  --slow-outdir step_05_route_ranges_to_ctrls/artifacts/slow_m5out

python3 step_06_guest_boot_with_two_ranges/scripts/check_e820_boot.py \
  step_06_guest_boot_with_two_ranges/artifacts/m5out

python3 step_08_expose_fast_slow_as_numa_nodes/scripts/check_acpi_numa_config.py \
  step_08_expose_fast_slow_as_numa_nodes/artifacts/m5out

python3 step_09_validate_linux_numa/scripts/check_linux_numa.py \
  step_09_validate_linux_numa/artifacts/m5out

python3 step_10_kvm_to_timing_switch/scripts/check_kvm_timing_config.py \
  step_10_kvm_to_timing_switch/artifacts/m5out

python3 step_11_microbench_validation/scripts/check_microbench_config.py \
  step_11_microbench_validation/artifacts/m5out

echo "All existing step artifacts validated."
