# Target Generator Search

status: `PASS_TARGET_SEARCH_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0]`
candidate_count: `12`

## Top Primitive Candidates

| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| p0p7_h0p03_k0p08_am0p03_ph1p5708 | 1 | 0 | 1 | 0.0018 | 0.0018 |
| p0p7_h0p03_k0p08_am0p015_ph1p5708 | 1 | 0 | 1 | 0.0016 | 0.0016 |
| p0p7_h0p05_k0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0015 | 0.0015 |
| p0p7_h0p05_k0p04_am0p05_ph1p5708 | 1 | 0 | 1 | 0.0014 | 0.0014 |
| p0p7_h0p03_k0p04_am0p03_ph1p5708 | 1 | 0 | 1 | 0.0007 | 0.0007 |
| p0p7_h0p03_k0p04_am0p015_ph1p5708 | 1 | 0 | 1 | 0.0005 | 0.0005 |
| p0p7_h0p03_k0p08_am0p015_ph0 | 1 | 0 | 1 | 0.0003 | 0.0003 |
| p0p7_h0p03_k0p08_am0p03_ph0 | 1 | 0 | 1 | 0.0002 | 0.0002 |
| p0p7_h0p03_k0p04_am0p015_ph0 | 1 | 0 | 1 | -0.0002 | -0.0002 |
| p0p7_h0p03_k0p04_am0p03_ph0 | 1 | 0 | 1 | -0.0004 | -0.0004 |
| p0p7_h0p05_k0p04_am0p025_ph0 | 1 | 0 | 1 | -0.0006 | -0.0006 |
| p0p7_h0p05_k0p04_am0p05_ph0 | 1 | 0 | 1 | -0.0009 | -0.0009 |

## Interpretation

- This is a target-window generator search, not policy training.
- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.
- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.
