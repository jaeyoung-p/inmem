#!/bin/bash
set -eux

echo "=== STEP12 BUILD ==="
if ! command -v cc >/dev/null 2>&1; then
    echo "No C compiler found in the guest. Install a compiler or copy in a prebuilt numa_bwlat binary."
    exit 0
fi

cc -O2 -Wall -Wextra -pthread -o /tmp/numa_bwlat /tmp/numa_bwlat.c

BWL_GUEST_CPUS="$(nproc)"
BWL_DEFAULT_MAX_WORKERS="$((BWL_GUEST_CPUS > 1 ? BWL_GUEST_CPUS - 1 : 0))"
BWL_MAX_WORKERS="${BWL_MAX_WORKERS:-${BWL_DEFAULT_MAX_WORKERS}}"
BWL_WORKER_STEP="${BWL_WORKER_STEP:-1}"
BWL_WORKER_MIB="${BWL_WORKER_MIB:-16}"
BWL_LATENCY_MIB="${BWL_LATENCY_MIB:-64}"
BWL_LATENCY_ITERS="${BWL_LATENCY_ITERS:-65536}"
BWL_CPU_MHZ="${BWL_CPU_MHZ:-3000}"

BWL_RECOMMENDED_LATENCY_MIB="$((BWL_GUEST_CPUS * 2))"
if (( BWL_LATENCY_MIB < BWL_RECOMMENDED_LATENCY_MIB )); then
    echo "BWL_WARN latency_mib=${BWL_LATENCY_MIB} is below recommended ${BWL_RECOMMENDED_LATENCY_MIB} MiB for ${BWL_GUEST_CPUS} cores; workers=0 may measure cached latency"
fi

echo "=== STEP12 ROI SWITCH ==="
gem5-bridge hypercall 4

echo "=== STEP12 NODE ONLINE ==="
cat /sys/devices/system/node/online

echo "=== STEP12 CPU COUNT ==="
nproc

echo "=== STEP12 NUMA BW/LAT COMMANDS ==="
for node in 0 1; do
    numactl --cpunodebind=0 --membind="${node}" \
        /tmp/numa_bwlat "${node}" "${BWL_MAX_WORKERS}" \
        "${BWL_WORKER_MIB}" "${BWL_LATENCY_MIB}" \
        "${BWL_LATENCY_ITERS}" "${BWL_WORKER_STEP}" "${BWL_CPU_MHZ}"
done

echo "=== STEP12 COMPLETE ==="
