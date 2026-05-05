# Implementation Plan

This file is now an archived roadmap snapshot placeholder.

Most of the original implementation plan has landed, and stale roadmap details
were removed so future work does not accidentally follow obsolete instructions.
Use these files instead:

- `AGENTS.md`: stable repository guide, architecture constraints, and working
  rules.
- `HANDOFF.md`: current state, recent commits, live Step 12 settings, and
  active caveats.
- `step_12_bw_latency_curve/README.md`: canonical frozen Step 12 DMA
  bandwidth/latency workflow.

Current project state in one sentence:

```text
x86 sparse RAM map -> local DDR5 node0 -> shared CXL-like node1 -> frozen Step 12 DMA pressure sweep
```

Do not use this file as an active roadmap unless a future session explicitly
rebuilds it from the current code and handoff.
