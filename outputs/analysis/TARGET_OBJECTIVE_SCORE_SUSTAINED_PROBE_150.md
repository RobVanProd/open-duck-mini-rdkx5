# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `360`
- mode_count: `180`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `150`

## Criteria

- min_mean_vx: `0.04`
- max_vy_abs_p95: `0.12`
- max_contact_dominance_pct: `95.0`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.12`
- min_done_margin: `50`
- min_contact_transitions: `3`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `low_forward_velocity`: `150`
- `single_contact_pattern_dominates`: `111`
- `low_base_height`: `74`
- `missing_seed_trace_or_window`: `30`
- `high_body_pitch`: `20`

### seed_002
- `low_forward_velocity`: `151`
- `single_contact_pattern_dominates`: `145`
- `low_base_height`: `72`
- `missing_seed_trace_or_window`: `29`
- `too_few_contact_transitions`: `18`
- `high_body_pitch`: `14`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p042_kb0p06_k0p2_ab0p04_a0p00336_ph0p42_ld0p36_ls0p65 | 0 | seed_000 | -0.2139 | -0.2109 | 0.0145 | 0.0169 | 0.0723 | 96.6667 | 7 | 0.0129 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p052_hrphm1p05_hb0p08_h0p048_kb0p06_k0p22_ab0p04_a0p00384_ph0p37_ld0p36_ls0p75 | 0 | seed_002 | -0.2157 | -0.2127 | 0.0131 | 0.0155 | 0.0744 | 96.6667 | 5 | 0.0123 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p052_hrph0_hb0p08_h0p048_kb0p06_k0p2_ab0p04_a0_ph0p47_ld0p3_ls0p65 | 0 | seed_000 | -0.2176 | -0.2079 | 0.0121 | 0.0143 | 0.0598 | 95.3333 | 7 | 0.0118 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p044_hrphm0p52_hb0p08_h0p054_kb0p06_k0p18_ab0p04_a0p00432_ph0p34_ld0p36_ls0p75 | 0 | seed_002 | -0.2192 | -0.2142 | 0.0123 | 0.0149 | 0.0638 | 96.6667 | 7 | 0.0118 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p46_hrb0_hra0p044_hrph0p7854_hb0p08_h0p042_kb0p06_k0p22_ab0p04_a0_ph0p42_ld0p24_ls0p75 | 0 | seed_002 | -0.2199 | -0.2105 | 0.0140 | 0.0151 | 0.0673 | 96.6667 | 7 | 0.0146 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p052_hrphm0p52_hb0p08_h0p042_kb0p06_k0p2_ab0p04_a0p00336_ph0p34_ld0p36_ls0p75 | 0 | seed_002 | -0.2207 | -0.2161 | 0.0129 | 0.0147 | 0.0648 | 96.6667 | 5 | 0.0117 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p46_hrb0_hra0p036_hrphm1p05_hb0p08_h0p054_kb0p06_k0p22_ab0p04_a0p00648_ph0p47_ld0p36_ls0p75 | 0 | seed_000 | -0.2221 | -0.2212 | 0.0131 | 0.0154 | 0.0902 | 96.6667 | 7 | 0.0134 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p052_hrphm0p52_hb0p08_h0p054_kb0p06_k0p22_ab0p04_a0p00432_ph0p37_ld0p24_ls0p65 | 0 | seed_002 | -0.2232 | -0.2196 | 0.0124 | 0.0145 | 0.0625 | 96.6667 | 7 | 0.0112 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p048_kb0p06_k0p2_ab0p04_a0_ph0p34_ld0p3_ls0p55 | 0 | seed_000 | -0.2241 | -0.2135 | 0.0139 | 0.0162 | 0.0718 | 96.0000 | 7 | 0.0133 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p052_hrphm0p52_hb0p08_h0p054_kb0p06_k0p18_ab0p04_a0p00432_ph0p47_ld0p36_ls0p75 | 0 | seed_002 | -0.2249 | -0.2229 | 0.0119 | 0.0143 | 0.0602 | 96.6667 | 7 | 0.0114 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p044_hrphm0p52_hb0p08_h0p048_kb0p06_k0p22_ab0p04_a0p00384_ph0p42_ld0p24_ls0p75 | 0 | seed_000 | -0.2259 | -0.2131 | 0.0112 | 0.0137 | 0.0778 | 94.6667 | 7 | 0.0138 | `low_base_height, low_forward_velocity` |
| primitive_p0p48_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p048_kb0p06_k0p18_ab0p04_a0p00384_ph0p47_ld0p36_ls0p65 | 0 | seed_000 | -0.2263 | -0.2150 | 0.0104 | 0.0129 | 0.0689 | 94.6667 | 8 | 0.0124 | `low_forward_velocity` |
| primitive_p0p5_hrb0_hra0p044_hrphm1p05_hb0p08_h0p048_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p36_ls0p75 | 0 | seed_000 | -0.2267 | -0.2215 | 0.0130 | 0.0155 | 0.0862 | 96.6667 | 7 | 0.0124 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p46_hrb0_hra0p052_hrph0p7854_hb0p08_h0p054_kb0p06_k0p2_ab0p04_a0p00432_ph0p34_ld0p3_ls0p75 | 0 | seed_002 | -0.2297 | -0.2243 | 0.0118 | 0.0155 | 0.0746 | 97.3333 | 3 | 0.0148 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p052_hrphm1p05_hb0p08_h0p048_kb0p06_k0p22_ab0p04_a0_ph0p37_ld0p24_ls0p75 | 0 | seed_000 | -0.2303 | -0.2149 | 0.0107 | 0.0140 | 0.0972 | 94.6667 | 9 | 0.0134 | `low_base_height, low_forward_velocity` |
| primitive_p0p52_hrb0_hra0p044_hrph0_hb0p08_h0p048_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p36_ls0p75 | 0 | seed_000 | -0.2307 | -0.2284 | 0.0138 | 0.0156 | 0.0595 | 97.3333 | 5 | 0.0123 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p052_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p2_ab0p04_a0_ph0p42_ld0p36_ls0p75 | 0 | seed_002 | -0.2308 | -0.2294 | 0.0129 | 0.0151 | 0.0838 | 97.3333 | 5 | 0.0116 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p042_kb0p06_k0p2_ab0p04_a0p00336_ph0p34_ld0p3_ls0p75 | 0 | seed_002 | -0.2318 | -0.2085 | 0.0150 | 0.0168 | 0.0635 | 98.0000 | 3 | 0.0147 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p22_ab0p04_a0p00336_ph0p47_ld0p24_ls0p65 | 0 | seed_000 | -0.2321 | -0.2207 | 0.0135 | 0.0161 | 0.0688 | 96.6667 | 5 | 0.0130 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p46_hrb0_hra0p052_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p00336_ph0p47_ld0p36_ls0p65 | 0 | seed_002 | -0.2322 | -0.2308 | 0.0108 | 0.0135 | 0.0843 | 96.6667 | 7 | 0.0121 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p048_kb0p06_k0p22_ab0p04_a0p00576_ph0p37_ld0p3_ls0p65 | 0 | seed_002 | -0.2322 | -0.2215 | 0.0144 | 0.0164 | 0.0680 | 98.0000 | 3 | 0.0123 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p46_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p3_ls0p55 | 0 | seed_002 | -0.2324 | -0.2297 | 0.0111 | 0.0135 | 0.0698 | 96.6667 | 5 | 0.0125 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p044_hrph0_hb0p08_h0p042_kb0p06_k0p2_ab0p04_a0p00336_ph0p42_ld0p24_ls0p75 | 0 | seed_002 | -0.2327 | -0.2201 | 0.0125 | 0.0149 | 0.0590 | 97.3333 | 5 | 0.0119 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p054_kb0p06_k0p2_ab0p04_a0_ph0p47_ld0p36_ls0p65 | 0 | seed_002 | -0.2332 | -0.2197 | 0.0150 | 0.0172 | 0.0785 | 98.0000 | 3 | 0.0135 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p054_kb0p06_k0p2_ab0p04_a0p00432_ph0p37_ld0p24_ls0p55 | 0 | seed_002 | -0.2340 | -0.2244 | 0.0139 | 0.0162 | 0.0826 | 97.3333 | 5 | 0.0145 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
