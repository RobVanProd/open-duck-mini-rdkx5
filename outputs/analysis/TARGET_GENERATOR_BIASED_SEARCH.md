# Target Generator Search

status: `PASS_TARGET_SEARCH_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0]`
candidate_count: `32`

## Top Primitive Candidates

| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0096 | 0.0096 |
| p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0079 | 0.0079 |
| p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0072 | 0.0072 |
| p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 1 | 0 | 1 | 0.0068 | 0.0068 |
| p0p7_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0064 | 0.0064 |
| p0p9_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 1 | 0 | 1 | 0.0063 | 0.0063 |
| p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0 | 1 | 0 | 1 | 0.0054 | 0.0054 |
| p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0052 | 0.0052 |
| p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 1 | 0 | 1 | 0.0051 | 0.0051 |
| p0p9_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0051 | 0.0051 |
| p0p7_hbm0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0047 | 0.0047 |
| p0p9_hbm0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0 | 1 | 0 | 1 | 0.0045 | 0.0045 |
| p0p7_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 1 | 0 | 1 | 0.0044 | 0.0044 |
| p0p9_hbm0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0035 | 0.0035 |
| p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0 | 1 | 0 | 1 | 0.0030 | 0.0030 |
| p0p7_hbm0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0 | 1 | 0 | 1 | 0.0025 | 0.0025 |
| p0p9_hb0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph1p5708 | 1 | 0 | 1 | -0.0006 | -0.0006 |
| p0p9_hbm0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph1p5708 | 1 | 0 | 1 | -0.0008 | -0.0008 |
| p0p7_hbm0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph1p5708 | 1 | 0 | 1 | -0.0011 | -0.0011 |
| p0p7_hb0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph1p5708 | 1 | 0 | 1 | -0.0016 | -0.0016 |

## Interpretation

- This is a target-window generator search, not policy training.
- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.
- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.
