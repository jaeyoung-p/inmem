#!/bin/bash
set -eux

echo "=== STEP12 BUILD ==="
if ! command -v cc >/dev/null 2>&1; then
    echo "No C compiler found in the guest."
    exit 2
fi

cc -O2 -Wall -Wextra -o /tmp/numa_latency /tmp/numa_latency.c

STEP12_NODE="${STEP12_NODE:-1}"
STEP12_LATENCY_MIB="${STEP12_LATENCY_MIB:-64}"
STEP12_LATENCY_ITERS="${STEP12_LATENCY_ITERS:-65536}"
STEP12_CPU_MHZ="${STEP12_CPU_MHZ:-2100}"

echo "=== STEP12 NODE ONLINE ==="
cat /sys/devices/system/node/online

echo "=== STEP12 CPU COUNT ==="
nproc

numactl --cpunodebind=0 --membind="${STEP12_NODE}" \
    /tmp/numa_latency \
    "${STEP12_NODE}" \
    "${STEP12_LATENCY_MIB}" \
    "${STEP12_LATENCY_ITERS}" \
    "${STEP12_CPU_MHZ}"

echo "=== STEP12 COMPLETE ==="
