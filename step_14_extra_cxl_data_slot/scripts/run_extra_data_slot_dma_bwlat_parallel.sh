#!/bin/bash
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export CXL_EXTRA_DATA_SLOTS="${CXL_EXTRA_DATA_SLOTS:-1}"
export NODES="${NODES:-1}"
export OUTDIR="${OUTDIR:-${REPO_ROOT}/step_14_extra_cxl_data_slot/artifacts/m5out_dma_extra_slot_16x4_ddr5_4400_64k}"

exec "${REPO_ROOT}/step_12_bw_latency_curve/scripts/run_dma_bwlat_parallel.sh"
