# Bandwidth-Versus-Latency Visualization

This directory contains plotting helpers for generated Step 12/13/14 DMA
bandwidth-versus-latency outputs.

The scripts are intentionally outside the `step_*` directories because they
are shared by Step 12, Step 13, and Step 14.

Generate an individual parsed CSV/PNG from a run directory:

```sh
python3 scripts/bw_vs_latency/visualize_dma_bwlat.py \
  step_12_bw_latency_curve/artifacts/m5out_dma_16x4_ddr5_4400_64k
```

Generate the unified CSV/PNG from the parsed per-step CSVs:

```sh
python3 scripts/bw_vs_latency/visualize_unified_dma_bwlat_csv.py
```

All generated figures and parsed CSVs are written under top-level
`artifacts/figures/`, not under a `step_*` directory.

The unified script uses the editable mapping at the top of
`visualize_unified_dma_bwlat_csv.py`:

```python
NAME_MAPPING = {
    12: {0: "Local", 1: "CXL"},
    13: {0: "Local+AES", 1: "CXL+AES"},
    14: {1: "CXL+AES+ExtraSlot"},
}
```
