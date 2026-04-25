# Step 13: AES Memory-Controller Latency

Step 13 reuses the Step 12 DMA bandwidth-versus-latency flow with fixed AES
processing latency enabled at every memory controller in node 0 and node 1.

The AES model is controlled by `MemCtrl.aes_latency`:

- `0ns` disables the extra processing delay and preserves Step 12 behavior.
- `40ns` models the encrypted-memory mode for this step.

The model adds this latency when the memory controller responds upstream. This
keeps the Step 13 study simple: CPU-observed memory responses move by the
configured fixed delay, without changing DRAM scheduling internals.

Run the encrypted Step 12-style sweep with:

```sh
step_13_aes_bw_latency_curve/scripts/run_aes_dma_bwlat_parallel.sh
```

Override the AES latency when needed:

```sh
AES_LATENCY=0ns step_13_aes_bw_latency_curve/scripts/run_aes_dma_bwlat_parallel.sh
AES_LATENCY=40ns step_13_aes_bw_latency_curve/scripts/run_aes_dma_bwlat_parallel.sh
```
