#!/bin/bash
set -eux

echo "=== STEP11 BUILD ==="
if ! command -v cc >/dev/null 2>&1; then
    echo "No C compiler found in the guest. Install a compiler or copy in a prebuilt numa_touch binary."
    exit 0
fi

cc -O2 -Wall -Wextra -o /tmp/numa_touch /tmp/numa_touch.c

MB_MIB="${MB_MIB:-1}"
MB_PASSES="${MB_PASSES:-1}"
MB_CHASE_PASSES="${MB_CHASE_PASSES:-1}"
MB_STRIDE="${MB_STRIDE:-4096}"

echo "=== STEP11 ROI SWITCH ==="
gem5-bridge hypercall 4

echo "=== STEP11 NODE ONLINE ==="
cat /sys/devices/system/node/online

echo "=== STEP11 NUMACTL COMMANDS ==="
for bench in read_seq write_seq readwrite_seq read_stride chase; do
    for node in 0 1; do
        case "${bench}" in
            read_stride)
                numactl --cpunodebind=0 --membind="${node}" \
                    /tmp/numa_touch "${node}" "${MB_MIB}" "${MB_PASSES}" \
                    "${bench}" "${MB_STRIDE}"
                ;;
            chase)
                numactl --cpunodebind=0 --membind="${node}" \
                    /tmp/numa_touch "${node}" "${MB_MIB}" \
                    "${MB_CHASE_PASSES}" "${bench}"
                ;;
            *)
                numactl --cpunodebind=0 --membind="${node}" \
                    /tmp/numa_touch "${node}" "${MB_MIB}" "${MB_PASSES}" \
                    "${bench}"
                ;;
        esac
    done
done

echo "=== STEP11 COMPLETE ==="
