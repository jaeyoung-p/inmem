#!/bin/bash
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
NUM_CORES="${NUM_CORES:-16}"
OUTDIR="${OUTDIR:-${REPO_ROOT}/step_12_bw_latency_curve/artifacts/m5out_${NUM_CORES}c}"
BWL_WORKER_STEP="${BWL_WORKER_STEP:-2}"
BWL_LATENCY_ITERS="${BWL_LATENCY_ITERS:-65536}"
BWL_WORKER_MIB="${BWL_WORKER_MIB:-16}"
BWL_LATENCY_MIB="${BWL_LATENCY_MIB:-64}"
BWL_CPU_MHZ="${BWL_CPU_MHZ:-3000}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-0}"

GEM5="${REPO_ROOT}/gem5/build/X86/gem5.opt"
CONFIG="${REPO_ROOT}/step_12_bw_latency_curve/scripts/x86_two_tier_numa_bwlat.py"
CHECKER="${REPO_ROOT}/step_12_bw_latency_curve/scripts/check_bwlat_config.py"
VISUALIZER="${REPO_ROOT}/step_12_bw_latency_curve/scripts/visualize_bwlat.py"

run_cmd=(
    "${GEM5}"
    "--outdir=${OUTDIR}"
    "${CONFIG}"
    "--num-cores" "${NUM_CORES}"
    "--bwl-worker-step" "${BWL_WORKER_STEP}"
    "--bwl-latency-iters" "${BWL_LATENCY_ITERS}"
    "--bwl-worker-mib" "${BWL_WORKER_MIB}"
    "--bwl-latency-mib" "${BWL_LATENCY_MIB}"
    "--bwl-cpu-mhz" "${BWL_CPU_MHZ}"
)

rm -rf "${OUTDIR}"
mkdir -p "$(dirname "${OUTDIR}")"

echo "Running ${NUM_CORES}-core bandwidth/latency curve"
echo "outdir=${OUTDIR}"
echo "num_cores=${NUM_CORES}"
echo "worker_step=${BWL_WORKER_STEP}"
echo "latency_iters=${BWL_LATENCY_ITERS}"
echo "worker_mib=${BWL_WORKER_MIB}"
echo "latency_mib=${BWL_LATENCY_MIB}"
echo "cpu_mhz=${BWL_CPU_MHZ}"

if [[ "${TIMEOUT_SECONDS}" == "0" ]]; then
    "${run_cmd[@]}"
else
    timeout "${TIMEOUT_SECONDS}s" "${run_cmd[@]}"
fi

python3 "${CHECKER}" --min-cores "${NUM_CORES}" "${OUTDIR}"
python3 "${VISUALIZER}" "${OUTDIR}"

echo "CSV: ${OUTDIR}/bw_latency_results.csv"
echo "SVG: ${OUTDIR}/bw_latency_results.svg"
