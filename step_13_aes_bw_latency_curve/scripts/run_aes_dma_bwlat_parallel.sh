#!/bin/bash
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export AES_LATENCY="${AES_LATENCY:-40ns}"
export OUTDIR="${OUTDIR:-${REPO_ROOT}/step_13_aes_bw_latency_curve/artifacts/m5out_dma_aes_16x4_ddr5_4400_64k}"

exec "${REPO_ROOT}/step_12_bw_latency_curve/scripts/run_dma_bwlat_parallel.sh"
