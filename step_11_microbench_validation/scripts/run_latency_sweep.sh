#!/bin/bash
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
GEM5_BIN="${GEM5_BIN:-${ROOT}/gem5/build/X86/gem5.opt}"
OUTROOT="${OUTROOT:-${ROOT}/step_11_microbench_validation/artifacts/latency_sweep}"
CONFIG="${ROOT}/step_11_microbench_validation/scripts/x86_two_tier_numa_microbench.py"

mkdir -p "${OUTROOT}"

run_case() {
    local name="$1"
    local base_latency="$2"
    local outdir="${OUTROOT}/${name}"

    rm -rf "${outdir}"
    "${GEM5_BIN}" --outdir="${outdir}" "${CONFIG}" \
        --cxl-base-latency="${base_latency}"
}

run_case no_fixed_base 0ns
run_case fixed_80ns 80ns

python3 "${ROOT}/step_11_microbench_validation/scripts/check_cxl_latency_model.py" \
    "${OUTROOT}/no_fixed_base"
python3 "${ROOT}/step_11_microbench_validation/scripts/check_cxl_latency_model.py" \
    --allow-fixed-base "${OUTROOT}/fixed_80ns"
python3 "${ROOT}/step_11_microbench_validation/scripts/visualize_microbench.py" \
    --csv "${OUTROOT}/microbench_results.csv" \
    --svg "${OUTROOT}/microbench_results.svg" \
    "${OUTROOT}/no_fixed_base" "${OUTROOT}/fixed_80ns"
