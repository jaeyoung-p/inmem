#!/bin/bash
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUTDIR="${OUTDIR:-${REPO_ROOT}/step_12_bw_latency_curve/artifacts/m5out_dma_bwlat}"
NODES="${NODES:-0 1}"
DMA_RATES="${DMA_RATES:-0 4GiB/s 8GiB/s 12GiB/s 16GiB/s 20GiB/s 24GiB/s 28GiB/s 32GiB/s}"
DMA_DURATION="${DMA_DURATION:-1s}"
DMA_BLOCK_SIZE="${DMA_BLOCK_SIZE:-64}"
DMA_INJECTORS="${DMA_INJECTORS:-1}"
LATENCY_MIB="${LATENCY_MIB:-64}"
LATENCY_ITERS="${LATENCY_ITERS:-65536}"
CPU_MHZ="${CPU_MHZ:-2100}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-0}"

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
rm -rf "${OUTDIR}"/node*_rate_*

echo "Running Step 12 DMA bandwidth/latency curve"
echo "outdir=${OUTDIR}"
echo "nodes=${NODES}"
echo "dma_rates=${DMA_RATES}"
echo "dma_duration=${DMA_DURATION}"
echo "dma_block_size=${DMA_BLOCK_SIZE}"
echo "dma_injectors=${DMA_INJECTORS}"
echo "latency_mib=${LATENCY_MIB}"
echo "latency_iters=${LATENCY_ITERS}"
echo "cpu_mhz=${CPU_MHZ}"

for node in ${NODES}; do
    for rate in ${DMA_RATES}; do
        safe_rate="$(sanitize_rate "${rate}")"
        point_outdir="${OUTDIR}/node${node}_rate_${safe_rate}"
        mkdir -p "${point_outdir}"
        printf '%s\n' "${node}" >"${point_outdir}/node.txt"
        printf '%s\n' "${rate}" >"${point_outdir}/rate.txt"

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

        if [[ "${TIMEOUT_SECONDS}" == "0" ]]; then
            "${run_cmd[@]}" >"${point_outdir}/host.log" 2>&1
        else
            timeout "${TIMEOUT_SECONDS}s" "${run_cmd[@]}" >"${point_outdir}/host.log" 2>&1
        fi

        min_dma_injectors=0
        if [[ "${rate}" != "0" && "${rate}" != "0B/s" && "${rate}" != "0GiB/s" ]]; then
            min_dma_injectors="${DMA_INJECTORS}"
        fi
        python3 "${CHECKER}" \
            --expected-node "${node}" \
            --min-dma-injectors "${min_dma_injectors}" \
            "${point_outdir}" >>"${point_outdir}/host.log" 2>&1
    done
done

python3 "${VISUALIZER}" "${OUTDIR}"

echo "CSV: ${OUTDIR}/dma_bwlat_results.csv"
echo "SVG: ${OUTDIR}/dma_bwlat_results.svg"
