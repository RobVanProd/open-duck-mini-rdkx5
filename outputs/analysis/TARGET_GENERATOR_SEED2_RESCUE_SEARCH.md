# Target Generator Search

status: `PASS_TARGET_SEARCH_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[2]`
candidate_count: `50`

## Top Primitive Candidates

| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0123 | 0.0123 |
| p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781 | 1 | 0 | 1 | 0.0123 | 0.0123 |
| p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854 | 1 | 0 | 1 | 0.0119 | 0.0119 |
| p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781 | 1 | 0 | 1 | 0.0116 | 0.0116 |
| p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0116 | 0.0116 |
| p0p9_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781 | 1 | 0 | 1 | 0.0113 | 0.0113 |
| p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854 | 1 | 0 | 1 | 0.0111 | 0.0111 |
| p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854 | 1 | 0 | 1 | 0.0110 | 0.0110 |
| p0p7_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0110 | 0.0110 |
| p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781 | 1 | 0 | 1 | 0.0108 | 0.0108 |
| p0p9_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0108 | 0.0108 |
| p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0108 | 0.0108 |
| p0p9_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781 | 1 | 0 | 1 | 0.0107 | 0.0107 |
| p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927 | 1 | 0 | 1 | 0.0107 | 0.0107 |
| p0p9_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927 | 1 | 0 | 1 | 0.0107 | 0.0107 |
| p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927 | 1 | 0 | 1 | 0.0106 | 0.0106 |
| p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 1 | 0 | 1 | 0.0106 | 0.0106 |
| p0p7_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781 | 1 | 0 | 1 | 0.0105 | 0.0105 |
| p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 1 | 0 | 1 | 0.0104 | 0.0104 |
| p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927 | 1 | 0 | 1 | 0.0104 | 0.0104 |

## Interpretation

- This is a target-window generator search, not policy training.
- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.
- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.
