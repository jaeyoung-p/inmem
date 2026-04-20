#!/bin/sh
set -eu

cd /home/cc/inmem/gem5

git apply ../step_04_second_mem_ctrl/patches/step_04_second_mem_ctrl.patch
git apply ../step_06_guest_boot_with_two_ranges/patches/step_06_guest_boot_with_two_ranges.patch
git apply ../step_08_expose_fast_slow_as_numa_nodes/patches/step_08_expose_fast_slow_as_numa_nodes.patch

scons build/ALL/gem5.opt -j"$(nproc)"
