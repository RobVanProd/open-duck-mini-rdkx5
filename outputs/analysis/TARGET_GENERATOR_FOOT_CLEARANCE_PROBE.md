# Target Generator Search

status: `PASS_TARGET_SEARCH_RAN`
command_x: `0.04`
duration_s: `4.0`
seeds: `[0, 2]`
candidate_count: `48`

## Top Primitive Candidates

| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls0p65 | 2 | 0 | 2 | 0.0130 | 0.0138 |
| p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p00525_ph0p3927_ld0p16_ls1 | 2 | 0 | 2 | 0.0121 | 0.0131 |
| p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p00525_ph0p32_ld0p22_ls1 | 2 | 0 | 2 | 0.0120 | 0.0130 |
| p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1 | 2 | 0 | 2 | 0.0119 | 0.0130 |
| p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p00525_ph0p47_ld0p16_ls1 | 2 | 0 | 2 | 0.0119 | 0.0130 |
| p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p0105_ph0p47_ld0p22_ls0p65 | 2 | 0 | 2 | 0.0116 | 0.0125 |
| p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0p0075_ph0p47_ld0p3_ls0p65 | 2 | 0 | 2 | 0.0115 | 0.0123 |
| p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65 | 2 | 0 | 2 | 0.0115 | 0.0124 |
| p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p3_ls0p65 | 2 | 0 | 2 | 0.0115 | 0.0122 |
| p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p00375_ph0p3927_ld0p3_ls0p65 | 2 | 0 | 2 | 0.0115 | 0.0122 |
| p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p16_ls1 | 2 | 0 | 2 | 0.0113 | 0.0123 |
| p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0_ph0p3927_ld0p16_ls0p65 | 2 | 0 | 2 | 0.0112 | 0.0121 |
| p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p00375_ph0p47_ld0p16_ls1 | 2 | 0 | 2 | 0.0111 | 0.0121 |
| p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls0p65 | 2 | 0 | 2 | 0.0110 | 0.0119 |
| p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p0105_ph0p3927_ld0p16_ls0p65 | 2 | 0 | 2 | 0.0107 | 0.0116 |
| p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p16_ls0p65 | 2 | 0 | 2 | 0.0105 | 0.0115 |
| p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65 | 2 | 0 | 2 | 0.0101 | 0.0109 |
| p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p0105_ph0p47_ld0p3_ls1 | 2 | 0 | 2 | 0.0098 | 0.0107 |
| p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65 | 2 | 0 | 2 | 0.0097 | 0.0106 |
| p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p22_ls0p65 | 2 | 0 | 2 | 0.0097 | 0.0104 |

## Interpretation

- This is a target-window generator search, not policy training.
- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.
- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.
