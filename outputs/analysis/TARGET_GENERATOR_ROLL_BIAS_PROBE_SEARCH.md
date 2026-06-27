# Target Generator Search

status: `PASS_TARGET_SEARCH_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `24`

## Top Primitive Candidates

| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0108 | 0.0123 |
| p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0107 | 0.0117 |
| p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0106 | 0.0116 |
| p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0091 | 0.0108 |
| p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0091 | 0.0103 |
| p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0088 | 0.0098 |
| p0p9_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0087 | 0.0100 |
| p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 2 | 0 | 2 | 0.0086 | 0.0099 |
| p0p9_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0083 | 0.0092 |
| p0p9_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0082 | 0.0093 |
| p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 2 | 0 | 2 | 0.0080 | 0.0092 |
| p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 2 | 0 | 2 | 0.0080 | 0.0097 |
| p0p7_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0070 | 0.0080 |
| p0p7_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0069 | 0.0085 |
| p0p9_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0 | 2 | 0 | 2 | 0.0067 | 0.0079 |
| p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 2 | 0 | 2 | 0.0066 | 0.0077 |
| p0p9_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0 | 2 | 0 | 2 | 0.0066 | 0.0085 |
| p0p7_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708 | 2 | 0 | 2 | 0.0064 | 0.0076 |
| p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0 | 2 | 0 | 2 | 0.0063 | 0.0074 |
| p0p9_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0 | 2 | 0 | 2 | 0.0060 | 0.0078 |

## Interpretation

- This is a target-window generator search, not policy training.
- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.
- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.
