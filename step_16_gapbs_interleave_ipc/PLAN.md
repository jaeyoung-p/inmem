# Step 16 Plan: GAPBS Interleave IPC

Measure the raw detailed-CPU IPC impact of mixed node0/node1 placement for a
memory-pressure graph kernel.

The implementation uses an Option A flow:

1. boot Linux under KVM;
2. embed and compile the selected GAPBS-style ROI benchmark in the guest;
3. allocate and build graph data under
   `numactl --cpunodebind=0 --interleave=0,1`;
4. enter ROI with `gem5-bridge hypercall 4`;
5. switch to `X86O3CPU`, reset stats, and run only the selected graph-kernel trial
   behind Ruby `MESI_Three_Level` with 48KiB L1D, 2MiB L2, and a shared L3;
6. exit with `gem5-bridge hypercall 3` and dump ROI stats.

Variants:

| Variant | AES latency | Integrity MAC | Extra CXL data slots | Shared L3 |
| --- | ---: | ---: | ---: | ---: |
| `baseline` | `0ns` | disabled | `0` | configured default |
| `aes` | `40ns` | disabled | `0` | configured default |
| `aes_mac` | `40ns` | enabled | `0` | configured default |
| `inmem` | `40ns` | disabled | `1` | configured default |
| `inmem_low` | `40ns` | disabled | `1` | `7MiB`, 14-way |

`aes_mac` and the `inmem` variants remain mutually exclusive experiments.

Supported kernels are selected with `GAPBS_KERNEL` / `--gapbs-kernel`:
`pr_spmv`, `pr`, `bc`, `sssp`, `cc`, and `tc`.
