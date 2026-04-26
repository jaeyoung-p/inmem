# Step 14: Extra CXL Data Slot

Step 14 reuses the Step 12 DMA bandwidth-versus-latency flow, but changes only
the shared node1 `CxlMemLink` serialization model.

The CXL link parameter is:

- `extra_data_slots=1`

This adds one modeled 16B data slot to each data-bearing CXL.mem message:

- `S2M DRS` read responses use one additional data slot.
- `M2S RwD` write-data messages use one additional data slot.

Header-only messages (`M2S Req` and `S2M NDR`) are unchanged. Node0 memory is
unchanged.

Run the Step 14 sweep with:

```sh
step_14_extra_cxl_data_slot/scripts/run_extra_data_slot_dma_bwlat_parallel.sh
```

Generate parsed CSV/PNG output for an existing Step 14 run with:

```sh
python3 scripts/bw_vs_latency/visualize_dma_bwlat.py \
  step_14_extra_cxl_data_slot/artifacts/m5out_dma_aes_16x4_ddr5_4400_64k
```

Generate the unified Step 12/13/14 figure after the per-step parsed CSVs exist:

```sh
python3 scripts/bw_vs_latency/visualize_unified_dma_bwlat_csv.py
```

Parsed per-step outputs and the unified figure are written under top-level
`artifacts/figures/`.
