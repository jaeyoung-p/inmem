#!/bin/bash
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

export NUM_CORES="${NUM_CORES:-32}"
export BWL_WORKER_STEP="${BWL_WORKER_STEP:-4}"
export OUTDIR="${OUTDIR:-${REPO_ROOT}/step_12_bw_latency_curve/artifacts/m5out_32c}"

exec "${SCRIPT_DIR}/run_16core_curve.sh"
