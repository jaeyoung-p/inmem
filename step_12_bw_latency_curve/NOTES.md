# Step 12 Notes

- Intel MLC is unavailable in this workspace; the host is AMD EPYC.
- Step 12 was hard-reset from worker-core injection to DMA-side synthetic read
  injection plus one latency probe core.
- Step 12 is now frozen to the DMA-only path driven by
  `scripts/run_dma_bwlat_parallel.sh`. Do not revive the removed serial runner
  or worker-core benchmark path.
- The curve now targets pure memory/CXL loading behavior, not CPU-worker cache
  interaction.
- Timing must stay on `rdtsc`; do not switch back to `clock_gettime()`.
- Keep the latency working set large enough to avoid cache-resident pointer
  chasing.
- Use `DDR5_4400_4x8` as a 32-bit DDR5 subchannel model. The experiment's
  "DDR5 channel" language refers to a logical 64-bit channel, so node0's
  intended 8x DDR5-4400 setup requires 16 x32 gem5 interfaces and node1's
  intended 2x DDR5-4400 setup requires 4 x32 gem5 interfaces.
- The expected saturation regions are approximately 218 GB/s for node0 and
  52 GB/s for node1. If node1 plateaus around the old roughly 30 GiB/s result,
  first check that the generated config has four node1 DDR5 subchannels behind
  the shared `CxlMemLink`, not two.
- The generated 16x4 topology should contain 36 `MemCtrl` and 36
  `DRAMInterface` objects: 16 node0 low-range controllers, 16 node0 high-range
  controllers, and 4 node1 controllers.
- Node0 DMA injection uses the contiguous high local range, not the low 3GiB
  region below the PCI hole.
- Use aggregate DMA pressure injection with `DMA_TOTAL_RATES` or
  `--dma-total-rate`; this is the only supported Step 12 rate interface.
- The canonical sweep is
  `8GiB/s 16GiB/s 32GiB/s 64GiB/s 128GiB/s 192GiB/s 224GiB/s 256GiB/s`
  with `DMA_TARGET_PER_INJECTOR=8GiB/s`, `RUBY_DIRECTORY_TBES=4096`, and
  `LATENCY_ITERS=65536`.
- Keep `numa_latency.c`; it is the benchmark code embedded into the guest and
  built inside the image during each point.
- The default user-facing DMA block size is 256B, but `PyTrafficGen` requests
  are clamped to 64B cache-line transfers internally while preserving the same
  offered byte rate.
- Ignore old worker-core Step 12 results when comparing against the new DMA
  path.
