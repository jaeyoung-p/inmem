# Step 5 Notes

- Synthetic traffic is enough here because the goal is Ruby routing, not Linux
  placement.
- `--tier node0` is the preferred name. `--tier fast` may remain as a
  compatibility alias in scripts.
- Read counts can differ by tier because link timing affects completion before
  simulation exit; validation checks active/inactive path separation.
