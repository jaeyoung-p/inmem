# AGENTS Guide

## Purpose

This file is the stable project guide for agents working in `/home/cc/inmem`.
It explains repository structure and working rules. It is not the current
status document and not the implementation roadmap.

Use:

- `HANDOFF.md` for current state, recent decisions, and active context.
- `IMPLEMENTATION_PLAN.md` for the technical roadmap and planned changes.

## Repository Structure

Top level:

- `gem5/`: gem5 source tree as a nested git repository/submodule fork.
- `doc/spec/`: local specification material, including the CXL spec markdown.
- `step_00_design_and_usage/`: design summary and project constraints.
- `step_02_baseline_fs_config/`: single-memory baseline FS config.
- `step_04_second_mem_ctrl/`: large-memory board and memory component work.
- `step_05_route_ranges_to_ctrls/`: Ruby address-range routing validation.
- `step_06_guest_boot_with_two_ranges/`: E820 multi-range guest boot checks.
- `step_08_expose_fast_slow_as_numa_nodes/`: SRAT/SLIT NUMA exposure.
- `step_09_validate_linux_numa/`: Linux NUMA boot validation.
- `step_10_kvm_to_timing_switch/`: KVM-to-Timing ROI switch flow.
- `step_11_microbench_validation/`: small NUMA placement microbenchmarks.
- `step_12_bw_latency_curve/`: bandwidth-versus-loaded-latency benchmark.
- `HANDOFF.md`: current status and recent context.
- `IMPLEMENTATION_PLAN.md`: roadmap and planned technical changes.

Typical step folder layout:

- `README.md`: what the step does and how to run it.
- `NOTES.md`: short caveats and assumptions.
- `scripts/`: configs, checkers, wrappers, benchmark code.
- `patches/`: historical patch snapshots when needed.
- `artifacts/`: generated outputs. Do not commit generated contents.

## Important Source Locations

Large-memory / NUMA path:

- `gem5/src/python/gem5/components/boards/large_mem_x86.py`
- `gem5/src/python/gem5/components/memory/tiered.py`
- `gem5/src/python/gem5/components/memory/split_range.py`

CXL path:

- `gem5/src/mem/CxlMemLink.py`
- `gem5/src/mem/cxl_mem_link.hh`
- `gem5/src/mem/cxl_mem_link.cc`

x86 ACPI / NUMA exposure:

- `gem5/src/arch/x86/bios/ACPI.py`
- `gem5/src/arch/x86/bios/acpi.hh`
- `gem5/src/arch/x86/bios/acpi.cc`

Step 12 benchmark:

- `step_12_bw_latency_curve/scripts/numa_latency.c`
- `step_12_bw_latency_curve/scripts/guest_dma_bwlat.sh`
- `step_12_bw_latency_curve/scripts/x86_two_tier_dma_bwlat.py`
- `step_12_bw_latency_curve/scripts/check_dma_bwlat_config.py`
- `step_12_bw_latency_curve/scripts/visualize_dma_bwlat.py`

## Project Rules

### Build / Run

- This project targets gem5 X86 only.
- Build with:

```sh
cd /home/cc/inmem/gem5
scons build/X86/gem5.opt -j$(nproc)
```

- Do not switch the project docs or scripts back to `build/ALL/gem5.opt`.

### CXL Changes

- Before changing CXL behavior or topology, read:

[`doc/spec/cxl-spec-v3.2-markdown/index.md`](/home/cc/inmem/doc/spec/cxl-spec-v3.2-markdown/index.md)

- Use the local spec as the first reference for CXL protocol and modeling
  decisions.
- Keep the current modeling boundary unless the task explicitly expands it:
  node1 is ordinary Linux NUMA RAM, not guest-visible CXL enumeration, DAX,
  devdax, pmem, or a guest driver path.

### Memory / NUMA Rules

- `LargeMemoryX86Board` is the project-local large-memory x86 board.
- Stock `X86Board` stays on the upstream small-memory path.
- All guest-visible RAM ranges must stay directly backed by real
  `AbstractMemory`.
- Do not reintroduce `RangeAddrMapper` into the current KVM-safe NUMA path.
- Node0 is one logical local DDR5 node split only by the x86 PCI hole.
- Keep node0 low/high interleaving identical unless the task explicitly changes
  the architecture.

### Step 12 Rules

- Intel MLC is not available in this workspace; use the in-tree benchmark.
- Step 12 timing must use TSC-cycle timing (`rdtsc`), not `clock_gettime()`.
- Step 12 is frozen to one latency core plus DMA-side synthetic read
  injection. Do not reintroduce worker-core bandwidth generation or the old
  worker benchmark path.
- The canonical Step 12 run is
  `step_12_bw_latency_curve/scripts/run_dma_bwlat_parallel.sh` with aggregate
  DMA rates, `DMA_TARGET_PER_INJECTOR=8GiB/s`, `RUBY_DIRECTORY_TBES=4096`,
  and `LATENCY_ITERS=65536`.
- Keep the guest benchmark source used by the DMA path:
  `step_12_bw_latency_curve/scripts/numa_latency.c`. It is embedded into the
  guest readfile and built inside the guest during each point.
- Do not use `clflush` in the current X86O3CPU x86 FS benchmark path.
- Keep the latency working set large enough to avoid cache-resident
  pointer-chase measurements.

### Git / Generated Output

- `gem5/` is its own git repository. Treat gem5 commits and outer-repo commits
  deliberately.
- Do not commit generated step `artifacts/`.
- Treat `m5out*`, `artifacts/`, and `__pycache__` as generated output unless
  explicitly asked otherwise.
- Never delete, overwrite, or auto-clean generated run outputs by default.
  Sweep scripts must not run broad cleanup such as `rm -rf "${OUTDIR}"/node*_rate_*`
  or remove result CSV/PNG files unless the user explicitly asks for a clean
  rerun. Preserve expensive simulation outputs and write new runs to a fresh
  output directory when in doubt.

### Validation

- After code changes, prefer the step-local checker scripts under `scripts/`.
- For topology work, inspect generated `config.ini` and `config.json`.
- For Linux NUMA work, validate SRAT/SLIT evidence in kernel logs and sysfs.
- For Step 12, use `check_dma_bwlat_config.py` after config generation and
  `visualize_dma_bwlat.py` after a point run or a full sweep.
- For validation expected to take more than about 5 minutes, or for any gem5
  build plus full-system smoke-test sequence, make a local checkpoint commit
  before starting validation, then launch a sub-agent to run and monitor that
  validation while the main agent continues with non-overlapping work.
- Treat validation sub-agents as working in the same local workspace and under
  the same approval model; do not assume they run outside the sandbox
  automatically.
- In one shared workspace, do not edit files involved in the active build while
  compile is still in progress. If validation runs in the same workspace, wait
  until late compile/link or the smoke-test phase before resuming overlapping
  edits. A separate worktree is preferred when fast parallel iteration matters.
- Keep smoke tests absolutely minimal. Their job is only to catch immediate
  regressions, not to validate final performance.
- For the shared-node1-CXL topology work, the default smoke target is:
  - incremental `build/X86/gem5.opt`
  - config generation succeeds
  - exactly one `CxlMemLink` exists in the generated config
  - both node1 paths traverse that shared link
  - one short FS boot/ROI run completes without obvious crash
- Do not treat a full Step 12 bandwidth/latency sweep as a smoke test. Run the
  full curve only after topology or protocol changes are already stable.
