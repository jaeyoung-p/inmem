# Step 16 Plan: GAPBS Interleave IPC

Measure the raw detailed-CPU IPC impact of mixed node0/node1 placement for a
memory-pressure graph kernel.

The first implementation uses an Option A flow:

1. boot Linux under KVM;
2. embed and compile a small PageRank SpMV ROI benchmark in the guest;
3. allocate and build graph data under
   `numactl --cpunodebind=0 --interleave=0,1`;
4. enter ROI with `gem5-bridge hypercall 4`;
5. switch to `X86O3CPU`, reset stats, and run only the PageRank SpMV trial
   behind Ruby `MESI_Three_Level` with 48KiB L1D, 2MiB L2, and 60MiB shared
   L3;
6. exit with `gem5-bridge hypercall 3` and dump ROI stats.

Variants:

| Variant | AES latency | Integrity MAC | Extra CXL data slots |
| --- | ---: | ---: | ---: |
| `baseline` | `0ns` | disabled | `0` |
| `aes` | `40ns` | disabled | `0` |
| `aes_mac` | `40ns` | enabled | `0` |
| `aes_extra_slot` | `40ns` | disabled | `1` |

`aes_mac` and `aes_extra_slot` remain mutually exclusive experiments.
