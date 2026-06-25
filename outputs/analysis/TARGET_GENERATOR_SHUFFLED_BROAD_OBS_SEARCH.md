# Target Generator Search

status: `PASS_TARGET_SEARCH_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `40`

## Top Primitive Candidates

| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| p0p85_hrb0p04_hb0p06_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927 | 2 | 0 | 2 | 0.0119 | 0.0131 |
| p1_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p024_ph1p5708 | 2 | 0 | 2 | 0.0113 | 0.0124 |
| p0p85_hrbm0p04_hb0p06_h0p07_kb0_k0p04_ab0p08_am0p021_ph0p7854 | 2 | 0 | 2 | 0.0110 | 0.0130 |
| p0p85_hrb0_hb0p06_h0p07_kb0p06_k0p04_ab0p04_am0p035_ph1p1781 | 2 | 0 | 2 | 0.0102 | 0.0109 |
| p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0 | 2 | 0 | 2 | 0.0100 | 0.0108 |
| p0p55_hrbm0p12_hb0p06_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p3927 | 2 | 0 | 2 | 0.0099 | 0.0130 |
| p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p015_ph1p1781 | 2 | 0 | 2 | 0.0098 | 0.0111 |
| p0p55_hrb0p04_hb0p04_h0p03_kb0_k0p08_ab0p08_am0p024_ph1p5708 | 2 | 0 | 2 | 0.0096 | 0.0112 |
| p0p7_hrb0p04_hb0p04_h0p05_kb0_k0p04_ab0p08_am0p015_ph0p7854 | 2 | 0 | 2 | 0.0095 | 0.0109 |
| p1_hrb0_hb0p04_h0p03_kb0p03_k0p04_ab0p08_am0p015_ph1p1781 | 2 | 0 | 2 | 0.0094 | 0.0107 |
| p0p85_hrb0_hb0p04_h0p03_kb0_k0p04_ab0p08_am0p024_ph0 | 2 | 0 | 2 | 0.0093 | 0.0109 |
| p0p85_hrbm0p16_hb0p08_h0p03_kb0p06_k0p04_ab0p04_am0p009_ph0 | 2 | 0 | 2 | 0.0080 | 0.0106 |
| p0p55_hrbm0p12_hb0p04_h0p07_kb0p06_k0p04_ab0p04_am0p056_ph1p5708 | 2 | 0 | 2 | 0.0079 | 0.0110 |
| p0p85_hrb0p04_hb0p04_h0p05_kb0_k0p04_ab0p04_am0p025_ph0 | 2 | 0 | 2 | 0.0071 | 0.0083 |
| p0p55_hrb0_hb0p04_h0p05_kb0_k0p12_ab0p04_am0p015_ph0p3927 | 2 | 0 | 2 | 0.0066 | 0.0080 |
| p0p7_hrbm0p08_hb0p06_h0p07_kb0p06_k0p08_ab0_am0p035_ph1p1781 | 2 | 0 | 2 | 0.0065 | 0.0082 |
| p0p55_hrb0_hb0p08_h0p03_kb0p03_k0p04_ab0p04_am0p009_ph0 | 2 | 0 | 2 | 0.0064 | 0.0078 |
| p0p7_hrb0_hb0p04_h0p03_kb0_k0p12_ab0p04_am0p015_ph0p7854 | 2 | 0 | 2 | 0.0062 | 0.0072 |
| p0p55_hrbm0p12_hb0p06_h0p03_kb0p03_k0p08_ab0p04_am0p009_ph0p7854 | 2 | 0 | 2 | 0.0056 | 0.0087 |
| p0p85_hrbm0p08_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p015_ph1p1781 | 2 | 0 | 2 | 0.0052 | 0.0067 |

## Interpretation

- This is a target-window generator search, not policy training.
- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.
- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.
