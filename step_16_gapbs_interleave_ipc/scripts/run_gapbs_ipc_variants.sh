#!/bin/bash
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUTDIR="${OUTDIR:-${REPO_ROOT}/step_16_gapbs_interleave_ipc/artifacts/m5out_gapbs_interleave_ipc}"
VARIANTS="${VARIANTS:-baseline aes aes_mac aes_extra_slot}"
GAPBS_SCALE="${GAPBS_SCALE:-16}"
GAPBS_TRIALS="${GAPBS_TRIALS:-1}"
GAPBS_MAX_ITERS="${GAPBS_MAX_ITERS:-20}"
GAPBS_FILE="${GAPBS_FILE:-}"
CPU_MHZ="${CPU_MHZ:-2100}"
NUM_CORES="${NUM_CORES:-1}"
OMP_THREADS="${OMP_THREADS:-${NUM_CORES}}"
ROI_CPU="${ROI_CPU:-o3}"
RUBY_DIRECTORY_TBES="${RUBY_DIRECTORY_TBES:-4096}"
L1I_SIZE="${L1I_SIZE:-32KiB}"
L1I_ASSOC="${L1I_ASSOC:-8}"
L1D_SIZE="${L1D_SIZE:-48KiB}"
L1D_ASSOC="${L1D_ASSOC:-12}"
L2_SIZE="${L2_SIZE:-2MiB}"
L2_ASSOC="${L2_ASSOC:-16}"
L3_SIZE="${L3_SIZE:-60MiB}"
L3_ASSOC="${L3_ASSOC:-20}"
NUM_L3_BANKS="${NUM_L3_BANKS:-1}"
JOBS="${JOBS:-1}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-999999}"
EXTRA_ARGS="${EXTRA_ARGS:-}"
MAX_TICKS="${MAX_TICKS:-}"
ROI_MAX_INSTS="${ROI_MAX_INSTS:-0}"
CLEAN_OUTDIR="${CLEAN_OUTDIR:-0}"
OVERWRITE_POINTS="${OVERWRITE_POINTS:-0}"
RUN_PARSER="${RUN_PARSER:-1}"

GEM5="${REPO_ROOT}/gem5/build/X86/gem5.opt"
CONFIG="${REPO_ROOT}/step_16_gapbs_interleave_ipc/scripts/x86_gapbs_interleave_ipc.py"
PARSER="${REPO_ROOT}/step_16_gapbs_interleave_ipc/scripts/parse_gapbs_ipc_stats.py"
FIGURE_OUTPUT_ROOT="${FIGURE_OUTPUT_ROOT:-${REPO_ROOT}/artifacts/figures/gapbs_interleave_ipc}"

mkdir -p "${OUTDIR}"
if [[ "${CLEAN_OUTDIR}" == "1" ]]; then
    rm -rf "${OUTDIR}"/*_g*_n*
fi

job_file="$(mktemp)"
trap 'rm -f "${job_file}"' EXIT

export OUTDIR
export GEM5
export CONFIG
export PARSER
export FIGURE_OUTPUT_ROOT
export GAPBS_SCALE
export GAPBS_TRIALS
export GAPBS_MAX_ITERS
export GAPBS_FILE
export CPU_MHZ
export NUM_CORES
export OMP_THREADS
export ROI_CPU
export RUBY_DIRECTORY_TBES
export L1I_SIZE
export L1I_ASSOC
export L1D_SIZE
export L1D_ASSOC
export L2_SIZE
export L2_ASSOC
export L3_SIZE
export L3_ASSOC
export NUM_L3_BANKS
export TIMEOUT_SECONDS
export EXTRA_ARGS
export MAX_TICKS
export ROI_MAX_INSTS
export OVERWRITE_POINTS

for variant_group in ${VARIANTS}; do
    variant_group="${variant_group//,/ }"
    for variant in ${variant_group}; do
        printf '%s\0' "${variant}" >>"${job_file}"
    done
done

echo "Running Step 16 GAPBS interleave IPC variants"
echo "outdir=${OUTDIR}"
echo "variants=${VARIANTS}"
echo "gapbs_scale=${GAPBS_SCALE}"
echo "gapbs_trials=${GAPBS_TRIALS}"
echo "gapbs_max_iters=${GAPBS_MAX_ITERS}"
echo "gapbs_file=${GAPBS_FILE}"
echo "roi_cpu=${ROI_CPU}"
echo "cpu_mhz=${CPU_MHZ}"
echo "num_cores=${NUM_CORES}"
echo "omp_threads=${OMP_THREADS}"
echo "ruby_directory_tbes=${RUBY_DIRECTORY_TBES}"
echo "roi_max_insts=${ROI_MAX_INSTS}"
echo "cache_hierarchy=MESI_Three_Level"
echo "l1i=${L1I_SIZE}/${L1I_ASSOC}"
echo "l1d=${L1D_SIZE}/${L1D_ASSOC}"
echo "l2=${L2_SIZE}/${L2_ASSOC}"
echo "l3=${L3_SIZE}/${L3_ASSOC} banks=${NUM_L3_BANKS}"
echo "jobs=${JOBS}"
echo "timeout_seconds=${TIMEOUT_SECONDS}"
echo "clean_outdir=${CLEAN_OUTDIR}"
echo "overwrite_points=${OVERWRITE_POINTS}"
echo "figure_output_root=${FIGURE_OUTPUT_ROOT}"

xargs -0 -r -n 1 -P "${JOBS}" bash -lc '
set -euo pipefail

variant="$1"
point_outdir="${OUTDIR}/${variant}_g${GAPBS_SCALE}_n${GAPBS_TRIALS}"
if [[ -e "${point_outdir}" ]]; then
    if [[ "${OVERWRITE_POINTS}" == "1" ]]; then
        rm -rf "${point_outdir}"
    else
        echo "Refusing to overwrite existing point directory: ${point_outdir}" >&2
        echo "Set OVERWRITE_POINTS=1 for per-point overwrite or CLEAN_OUTDIR=1 for a full clean rerun." >&2
        exit 2
    fi
fi
mkdir -p "${point_outdir}"
printf "%s\n" "${variant}" >"${point_outdir}/variant.txt"
date +%s >"${point_outdir}/start_time_epoch.txt"

run_cmd=(
    "${GEM5}"
    "--outdir=${point_outdir}"
    "${CONFIG}"
    "--variant" "${variant}"
    "--gapbs-scale" "${GAPBS_SCALE}"
    "--gapbs-trials" "${GAPBS_TRIALS}"
    "--gapbs-max-iters" "${GAPBS_MAX_ITERS}"
    "--cpu-mhz" "${CPU_MHZ}"
    "--num-cores" "${NUM_CORES}"
    "--omp-threads" "${OMP_THREADS}"
    "--roi-cpu" "${ROI_CPU}"
    "--roi-max-insts" "${ROI_MAX_INSTS}"
    "--ruby-directory-tbes" "${RUBY_DIRECTORY_TBES}"
    "--l1i-size" "${L1I_SIZE}"
    "--l1i-assoc" "${L1I_ASSOC}"
    "--l1d-size" "${L1D_SIZE}"
    "--l1d-assoc" "${L1D_ASSOC}"
    "--l2-size" "${L2_SIZE}"
    "--l2-assoc" "${L2_ASSOC}"
    "--l3-size" "${L3_SIZE}"
    "--l3-assoc" "${L3_ASSOC}"
    "--num-l3-banks" "${NUM_L3_BANKS}"
)

if [[ -n "${GAPBS_FILE}" ]]; then
    run_cmd+=("--gapbs-file" "${GAPBS_FILE}")
fi

if [[ -n "${MAX_TICKS}" ]]; then
    run_cmd+=("--max-ticks" "${MAX_TICKS}")
fi

if [[ -n "${EXTRA_ARGS}" ]]; then
    # shellcheck disable=SC2206
    extra_parts=(${EXTRA_ARGS})
    run_cmd+=("${extra_parts[@]}")
fi

{
    echo "variant=${variant}"
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

if [[ "${status}" == "0" ]]; then
    echo "status=ok" >>"${point_outdir}/host.log"
else
    echo "status=failed exit_code=${status}" >>"${point_outdir}/host.log"
fi
date +%s >"${point_outdir}/end_time_epoch.txt"
printf "%s\n" "${status}" >"${point_outdir}/status.txt"
' _ <"${job_file}"

if [[ "${RUN_PARSER}" == "1" ]]; then
    python3 "${PARSER}" --output-root "${FIGURE_OUTPUT_ROOT}" "${OUTDIR}"
    echo "Parsed CSV output is under: ${FIGURE_OUTPUT_ROOT}"
fi

failed_count="$(
    find "${OUTDIR}" -name status.txt -print0 \
        | xargs -0 cat 2>/dev/null \
        | awk '$1 != 0 {count++} END {print count+0}'
)"

if [[ "${failed_count}" != "0" ]]; then
    echo "failed_points=${failed_count}"
    exit 1
fi
