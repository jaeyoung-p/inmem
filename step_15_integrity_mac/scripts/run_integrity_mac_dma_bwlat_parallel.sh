#!/bin/bash
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export INTEGRITY_MAC_ENABLE=1
export CXL_EXTRA_DATA_SLOTS=0
export OUTDIR="${OUTDIR:-${REPO_ROOT}/step_15_integrity_mac/artifacts/m5out_dma_integrity_mac_16x4_ddr5_4400_64k}"

exec "${REPO_ROOT}/step_12_bw_latency_curve/scripts/run_dma_bwlat_parallel.sh"
