# Target Generator Search

status: `PASS_TARGET_SEARCH_RAN`
command_x: `0.04`
duration_s: `4.0`
seeds: `[0, 2]`
candidate_count: `80`

## Top Primitive Candidates

| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| p0p7_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p1963 | 2 | 0 | 2 | 0.0134 | 0.0142 |
| p0p7_hrb0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p1963 | 2 | 0 | 2 | 0.0127 | 0.0134 |
| p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927 | 2 | 0 | 2 | 0.0124 | 0.0132 |
| p0p7_hrbm0p01_hb0p08_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p589 | 2 | 0 | 2 | 0.0112 | 0.0118 |
| p0p5_hrb0p01_hb0p08_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0p589 | 2 | 0 | 2 | 0.0096 | 0.0103 |
| p0p7_hrb0p01_hb0p06_h0p05_kb0p06_k0p1_ab0p04_am0p015_ph0p589 | 2 | 0 | 2 | 0.0095 | 0.0101 |
| p0p6_hrb0p01_hb0p04_h0p04_kb0p03_k0p08_ab0p08_a0_ph0 | 2 | 0 | 2 | 0.0094 | 0.0105 |
| p0p7_hrb0_hb0p06_h0p04_kb0p06_k0p12_ab0p04_a0_ph0 | 2 | 0 | 2 | 0.0093 | 0.0110 |
| p0p5_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p08_a0_ph0p3927 | 2 | 0 | 2 | 0.0089 | 0.0092 |
| p0p5_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963 | 2 | 0 | 2 | 0.0086 | 0.0095 |
| p0p6_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589 | 2 | 0 | 2 | 0.0085 | 0.0092 |
| p0p5_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p08_a0_ph0p1963 | 2 | 0 | 2 | 0.0085 | 0.0095 |
| p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589 | 2 | 0 | 2 | 0.0081 | 0.0090 |
| p0p6_hrbm0p01_hb0p04_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p3927 | 2 | 0 | 2 | 0.0078 | 0.0087 |
| p0p5_hrb0_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0_ph0p7854 | 2 | 0 | 2 | 0.0077 | 0.0089 |
| p0p6_hrb0p01_hb0p06_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p589 | 2 | 0 | 2 | 0.0075 | 0.0076 |
| p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963 | 2 | 0 | 2 | 0.0073 | 0.0081 |
| p0p7_hrbm0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p015_ph0 | 2 | 0 | 2 | 0.0072 | 0.0083 |
| p0p7_hrbm0p01_hb0p04_h0p04_kb0p06_k0p08_ab0p04_a0_ph0p7854 | 2 | 0 | 2 | 0.0072 | 0.0081 |
| p0p5_hrb0p01_hb0p06_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p1963 | 2 | 0 | 2 | 0.0071 | 0.0077 |

## Interpretation

- This is a target-window generator search, not policy training.
- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.
- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.
