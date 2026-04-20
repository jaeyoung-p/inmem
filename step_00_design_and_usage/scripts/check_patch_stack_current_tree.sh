#!/bin/sh
set -eu

cd /home/cc/inmem/gem5

git apply --check --reverse ../step_04_second_mem_ctrl/patches/step_04_second_mem_ctrl.patch
git apply --check --reverse ../step_06_guest_boot_with_two_ranges/patches/step_06_guest_boot_with_two_ranges.patch
git apply --check --reverse ../step_08_expose_fast_slow_as_numa_nodes/patches/step_08_expose_fast_slow_as_numa_nodes.patch

echo "Patch stack matches the current gem5 source tree."
