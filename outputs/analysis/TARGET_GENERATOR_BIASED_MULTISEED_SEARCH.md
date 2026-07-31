# Target Generator Search

status: `PASS_TARGET_SEARCH_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 1, 2, 3]`
candidate_count: `8`

## Top Primitive Candidates

| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 4 | 1 | 3 | -0.0234 | 0.0116 |
| p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0 | 4 | 1 | 3 | -0.0273 | 0.0079 |
| p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 4 | 1 | 3 | -0.0274 | 0.0093 |
| p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 4 | 1 | 3 | -0.0281 | 0.0098 |
| p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 4 | 1 | 3 | -0.0295 | 0.0076 |
| p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 4 | 1 | 3 | -0.0302 | 0.0092 |
| p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 4 | 1 | 3 | -0.0306 | 0.0074 |
| p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0 | 4 | 1 | 3 | -0.0309 | 0.0056 |

## Interpretation

- This is a target-window generator search, not policy training.
- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.
- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.
