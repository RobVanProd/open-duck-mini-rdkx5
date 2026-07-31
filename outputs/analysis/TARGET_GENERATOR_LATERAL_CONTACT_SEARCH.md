# Target Generator Search

status: `PASS_TARGET_SEARCH_RAN`
command_x: `0.04`
duration_s: `4.0`
seeds: `[0, 2]`
candidate_count: `48`

## Top Primitive Candidates

| primitive | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927 | 2 | 0 | 2 | 0.0112 | 0.0120 |
| p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854 | 2 | 0 | 2 | 0.0103 | 0.0111 |
| p0p7_hrbm0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0 | 2 | 0 | 2 | 0.0093 | 0.0128 |
| p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0 | 2 | 0 | 2 | 0.0088 | 0.0098 |
| p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p7854 | 2 | 0 | 2 | 0.0087 | 0.0120 |
| p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927 | 2 | 0 | 2 | 0.0086 | 0.0096 |
| p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927 | 2 | 0 | 2 | 0.0083 | 0.0093 |
| p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854 | 2 | 0 | 2 | 0.0080 | 0.0090 |
| p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p3927 | 2 | 0 | 2 | 0.0076 | 0.0085 |
| p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p08_a0p009_ph0 | 2 | 0 | 2 | 0.0069 | 0.0079 |
| p0p7_hrb0_hb0p06_h0p03_kb0p03_k0p12_ab0p04_am0p009_ph0p7854 | 2 | 0 | 2 | 0.0061 | 0.0070 |
| p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0 | 2 | 0 | 2 | 0.0060 | 0.0067 |
| p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p3927 | 2 | 0 | 2 | 0.0053 | 0.0062 |
| p0p55_hrbm0p02_hb0p04_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0 | 2 | 0 | 2 | 0.0053 | 0.0065 |
| p0p7_hrb0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0p009_ph0p7854 | 2 | 0 | 2 | 0.0050 | 0.0058 |
| p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p12_ab0p04_am0p015_ph0 | 2 | 0 | 2 | 0.0049 | 0.0060 |
| p0p55_hrbm0p02_hb0p04_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0 | 2 | 0 | 2 | 0.0048 | 0.0058 |
| p0p55_hrb0p02_hb0p06_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0p3927 | 2 | 0 | 2 | 0.0047 | 0.0056 |
| p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p3927 | 2 | 0 | 2 | 0.0045 | 0.0054 |
| p0p55_hrbm0p02_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0 | 2 | 0 | 2 | 0.0044 | 0.0054 |

## Interpretation

- This is a target-window generator search, not policy training.
- Raw traces are ignored by git; compact summaries and curation artifacts should be committed.
- A useful search still must pass `tools/mine_realized_target_windows.py` and `tools/curate_realized_target_windows.py`.
