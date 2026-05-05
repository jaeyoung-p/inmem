#!/bin/bash
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

set -eux

: "${GAPBS_SCALE:=16}"
: "${GAPBS_TRIALS:=1}"
: "${GAPBS_MAX_ITERS:=20}"
: "${GAPBS_FILE:=}"
: "${GAPBS_KERNEL:=pr_spmv}"
: "${OMP_NUM_THREADS:=1}"

echo "=== STEP16 BUILD ==="
c++ -O3 -std=c++11 -fopenmp \
  -o /tmp/gapbs_kernel_roi \
  /tmp/gapbs_kernel_roi.cc

echo "=== STEP16 NODE ONLINE ==="
cat /sys/devices/system/node/online

echo "=== STEP16 RUN ==="
export OMP_NUM_THREADS
run_args=(
  -g "${GAPBS_SCALE}" \
  -n "${GAPBS_TRIALS}" \
  -i "${GAPBS_MAX_ITERS}"
)
if [[ -n "${GAPBS_FILE}" ]]; then
  run_args+=(-f "${GAPBS_FILE}")
fi

numactl --cpunodebind=0 --interleave=0,1 \
  /tmp/gapbs_kernel_roi \
  "${run_args[@]}"

echo "=== STEP16 COMPLETE ==="
gem5-bridge hypercall 3
