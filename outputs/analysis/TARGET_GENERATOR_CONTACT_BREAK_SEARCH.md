# Target Generator Search

status: `PASS_TARGET_SEARCH_RAN`
command_x: `0.04`
duration_s: `4.0`
seeds: `[0, 2]`
candidate_count: `96`

## Top Primitive Candidates

| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p014_ph0p36 | 2 | 0 | 2 | 0.0129 | 0.0135 |
| p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p52 | 2 | 0 | 2 | 0.0126 | 0.0134 |
| p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p47 | 2 | 0 | 2 | 0.0125 | 0.0132 |
| p0p62_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p52 | 2 | 0 | 2 | 0.0121 | 0.0127 |
| p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_a0_ph0p47 | 2 | 0 | 2 | 0.0119 | 0.0127 |
| p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p47 | 2 | 0 | 2 | 0.0118 | 0.0124 |
| p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927 | 2 | 0 | 2 | 0.0118 | 0.0126 |
| p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p36 | 2 | 0 | 2 | 0.0117 | 0.0123 |
| p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p52 | 2 | 0 | 2 | 0.0117 | 0.0125 |
| p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p47 | 2 | 0 | 2 | 0.0116 | 0.0123 |
| p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p47 | 2 | 0 | 2 | 0.0116 | 0.0123 |
| p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p005_ph0p36 | 2 | 0 | 2 | 0.0116 | 0.0124 |
| p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p3927 | 2 | 0 | 2 | 0.0116 | 0.0124 |
| p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43 | 2 | 0 | 2 | 0.0116 | 0.0123 |
| p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p43 | 2 | 0 | 2 | 0.0115 | 0.0122 |
| p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p006_ph0p36 | 2 | 0 | 2 | 0.0111 | 0.0119 |
| p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p005_ph0p3927 | 2 | 0 | 2 | 0.0110 | 0.0118 |
| p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p32 | 2 | 0 | 2 | 0.0110 | 0.0118 |
| p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p009_ph0p3927 | 2 | 0 | 2 | 0.0109 | 0.0118 |
| p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927 | 2 | 0 | 2 | 0.0097 | 0.0102 |

## Interpretation

- This is a target-window generator search, not policy training.
- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.
- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.
