#!/bin/bash
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUTDIR="${OUTDIR:-${REPO_ROOT}/step_12_bw_latency_curve/artifacts/m5out_dma_parallel}"
NODES="${NODES:-0 1}"
DMA_RATES="${DMA_RATES:-0 8GiB/s 16GiB/s 24GiB/s 32GiB/s 64GiB/s 96GiB/s}"
DMA_DURATION="${DMA_DURATION:-1s}"
DMA_BLOCK_SIZE="${DMA_BLOCK_SIZE:-64}"
DMA_INJECTORS="${DMA_INJECTORS:-1}"
LATENCY_MIB="${LATENCY_MIB:-64}"
LATENCY_ITERS="${LATENCY_ITERS:-16384}"
CPU_MHZ="${CPU_MHZ:-2100}"
JOBS="${JOBS:-8}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-2700}"
RUN_CHECKER="${RUN_CHECKER:-1}"
EXTRA_ARGS="${EXTRA_ARGS:-}"
MAX_TICKS="${MAX_TICKS:-}"

GEM5="${REPO_ROOT}/gem5/build/X86/gem5.opt"
CONFIG="${REPO_ROOT}/step_12_bw_latency_curve/scripts/x86_two_tier_dma_bwlat.py"
CHECKER="${REPO_ROOT}/step_12_bw_latency_curve/scripts/check_dma_bwlat_config.py"
VISUALIZER="${REPO_ROOT}/step_12_bw_latency_curve/scripts/visualize_dma_bwlat.py"

sanitize_rate() {
    local text="$1"
    text="${text//\//_}"
    text="${text// /_}"
    printf '%s' "${text}"
}

mkdir -p "${OUTDIR}"

job_file="$(mktemp)"
trap 'rm -f "${job_file}"' EXIT

export OUTDIR
export GEM5
export CONFIG
export CHECKER
export VISUALIZER
export DMA_DURATION
export DMA_BLOCK_SIZE
export DMA_INJECTORS
export LATENCY_MIB
export LATENCY_ITERS
export CPU_MHZ
export TIMEOUT_SECONDS
export RUN_CHECKER
export EXTRA_ARGS
export MAX_TICKS

for node in ${NODES}; do
    for rate in ${DMA_RATES}; do
        printf '%s\0%s\0' "${node}" "${rate}" >>"${job_file}"
    done
done

echo "Running parallel Step 12 DMA sweep"
echo "outdir=${OUTDIR}"
echo "nodes=${NODES}"
echo "dma_rates=${DMA_RATES}"
echo "dma_duration=${DMA_DURATION}"
echo "dma_block_size=${DMA_BLOCK_SIZE}"
echo "dma_injectors=${DMA_INJECTORS}"
echo "latency_mib=${LATENCY_MIB}"
echo "latency_iters=${LATENCY_ITERS}"
echo "cpu_mhz=${CPU_MHZ}"
echo "jobs=${JOBS}"
echo "timeout_seconds=${TIMEOUT_SECONDS}"

xargs -0 -r -n 2 -P "${JOBS}" bash -lc '
set -euo pipefail

node="$1"
rate="$2"

sanitize_rate() {
    local text="$1"
    text="${text//\//_}"
    text="${text// /_}"
    printf "%s" "${text}"
}

safe_rate="$(sanitize_rate "${rate}")"
point_outdir="${OUTDIR}/node${node}_rate_${safe_rate}"
mkdir -p "${point_outdir}"
printf "%s\n" "${node}" >"${point_outdir}/node.txt"
printf "%s\n" "${rate}" >"${point_outdir}/rate.txt"
date +%s >"${point_outdir}/start_time_epoch.txt"

run_cmd=(
    "${GEM5}"
    "--outdir=${point_outdir}"
    "${CONFIG}"
    "--node" "${node}"
    "--latency-mib" "${LATENCY_MIB}"
    "--latency-iters" "${LATENCY_ITERS}"
    "--cpu-mhz" "${CPU_MHZ}"
    "--dma-rate" "${rate}"
    "--dma-duration" "${DMA_DURATION}"
    "--dma-block-size" "${DMA_BLOCK_SIZE}"
    "--dma-injectors" "${DMA_INJECTORS}"
)

if [[ -n "${MAX_TICKS}" ]]; then
    run_cmd+=("--max-ticks" "${MAX_TICKS}")
fi

if [[ -n "${EXTRA_ARGS}" ]]; then
    # shellcheck disable=SC2206
    extra_parts=(${EXTRA_ARGS})
    run_cmd+=("${extra_parts[@]}")
fi

{
    echo "node=${node} rate=${rate}"
    printf "cmd="
    printf "%q " "${run_cmd[@]}"
    echo
} >"${point_outdir}/host.log"

status=0
if [[ "${TIMEOUT_SECONDS}" == "0" ]]; then
    "${run_cmd[@]}" >>"${point_outdir}/host.log" 2>&1 || status=$?
else
    timeout "${TIMEOUT_SECONDS}s" "${run_cmd[@]}" >>"${point_outdir}/host.log" 2>&1 || status=$?
fi

if [[ "${status}" == "0" && "${RUN_CHECKER}" == "1" ]]; then
    min_dma_injectors=0
    case "${rate,,}" in
        0|0b/s|0kib/s|0mib/s|0gib/s)
            min_dma_injectors=0
            ;;
        *)
            min_dma_injectors="${DMA_INJECTORS}"
            ;;
    esac

    python3 "${CHECKER}" \
        --expected-node "${node}" \
        --min-dma-injectors "${min_dma_injectors}" \
        "${point_outdir}" >>"${point_outdir}/host.log" 2>&1 || status=$?
fi

if [[ "${status}" == "0" ]]; then
    echo "status=ok" >>"${point_outdir}/host.log"
else
    echo "status=failed exit_code=${status}" >>"${point_outdir}/host.log"
fi
date +%s >"${point_outdir}/end_time_epoch.txt"
printf "%s\n" "${status}" >"${point_outdir}/status.txt"
' _ <"${job_file}"

python3 "${VISUALIZER}" "${OUTDIR}"

failed_count="$(
    find "${OUTDIR}" -name status.txt -print0 \
        | xargs -0 cat 2>/dev/null \
        | awk '$1 != 0 {count++} END {print count+0}'
)"

echo "CSV: ${OUTDIR}/dma_bwlat_results.csv"
echo "SVG: ${OUTDIR}/dma_bwlat_results.svg"

if [[ "${failed_count}" != "0" ]]; then
    echo "failed_points=${failed_count}"
    exit 1
fi
