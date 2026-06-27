# Target Generator Search

status: `PASS_TARGET_SEARCH_RAN`
command_x: `0.04`
duration_s: `4.0`
seeds: `[0, 2]`
candidate_count: `96`

## Top Primitive Candidates

| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p54_ld0p22_ls0p65 | 2 | 0 | 2 | 0.0133 | 0.0141 |
| p0p6_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p00625_ph0p32_ld0p22_ls0p65 | 2 | 0 | 2 | 0.0130 | 0.0138 |
| p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p47_ld0p22_ls0p65 | 2 | 0 | 2 | 0.0130 | 0.0139 |
| p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p47_ld0p38_ls0p65 | 2 | 0 | 2 | 0.0128 | 0.0136 |
| p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p012_ph0p3927_ld0p22_ls0p65 | 2 | 0 | 2 | 0.0127 | 0.0136 |
| p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_a0_ph0p3927_ld0p22_ls0p65 | 2 | 0 | 2 | 0.0126 | 0.0136 |
| p0p56_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p3927_ld0p38_ls0p65 | 2 | 0 | 2 | 0.0120 | 0.0129 |
| p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p0075_ph0p3927_ld0p22_ls0p65 | 2 | 0 | 2 | 0.0118 | 0.0126 |
| p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p54_ld0p22_ls0p35 | 2 | 0 | 2 | 0.0118 | 0.0126 |
| p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p0075_ph0p32_ld0p22_ls1 | 2 | 0 | 2 | 0.0118 | 0.0128 |
| p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p0075_ph0p54_ld0p22_ls1 | 2 | 0 | 2 | 0.0117 | 0.0128 |
| p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p54_ld0p38_ls0p35 | 2 | 0 | 2 | 0.0116 | 0.0124 |
| p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_a0_ph0p3927_ld0p22_ls1 | 2 | 0 | 2 | 0.0115 | 0.0124 |
| p0p68_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35 | 2 | 0 | 2 | 0.0113 | 0.0121 |
| p0p68_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65 | 2 | 0 | 2 | 0.0112 | 0.0119 |
| p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35 | 2 | 0 | 2 | 0.0111 | 0.0120 |
| p0p64_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_a0_ph0p54_ld0p22_ls1 | 2 | 0 | 2 | 0.0111 | 0.0121 |
| p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p47_ld0p22_ls0p35 | 2 | 0 | 2 | 0.0111 | 0.0120 |
| p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p00625_ph0p3927_ld0p38_ls0p35 | 2 | 0 | 2 | 0.0110 | 0.0119 |
| p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p0035_ph0p54_ld0p38_ls0p35 | 2 | 0 | 2 | 0.0109 | 0.0118 |

## Interpretation

- This is a target-window generator search, not policy training.
- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.
- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.
