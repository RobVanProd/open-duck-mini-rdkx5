# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `320`
- mode_count: `160`
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
- `low_forward_velocity`: `153`
- `single_contact_pattern_dominates`: `138`
- `missing_seed_trace_or_window`: `7`
- `low_base_height`: `5`

### seed_002
- `low_forward_velocity`: `159`
- `single_contact_pattern_dominates`: `157`
- `too_few_contact_transitions`: `17`
- `low_base_height`: `6`
- `high_body_pitch`: `1`
- `missing_seed_trace_or_window`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65 | 0 | seed_002 | -0.2079 | -0.2051 | 0.0132 | 0.0147 | 0.0567 | 96.0000 | 7 | 0.0117 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0063_ph0p42_ld0p36_ls1 | 0 | seed_002 | -0.2159 | -0.2129 | 0.0130 | 0.0153 | 0.0768 | 96.6667 | 7 | 0.0125 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55 | 0 | seed_002 | -0.2229 | -0.2069 | 0.0143 | 0.0160 | 0.0699 | 97.3333 | 5 | 0.0134 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65 | 0 | seed_002 | -0.2247 | -0.2224 | 0.0118 | 0.0143 | 0.0612 | 96.6667 | 5 | 0.0115 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75 | 0 | seed_000 | -0.2249 | -0.2158 | 0.0128 | 0.0148 | 0.0650 | 96.0000 | 5 | 0.0121 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p47_ld0p36_ls1 | 0 | seed_002 | -0.2263 | -0.2171 | 0.0132 | 0.0156 | 0.0842 | 97.3333 | 3 | 0.0119 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75 | 0 | seed_002 | -0.2265 | -0.2220 | 0.0121 | 0.0141 | 0.0586 | 96.6667 | 7 | 0.0120 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p42_ld0p3_ls1 | 0 | seed_002 | -0.2274 | -0.2226 | 0.0114 | 0.0140 | 0.0856 | 96.6667 | 5 | 0.0118 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65 | 0 | seed_000 | -0.2282 | -0.2229 | 0.0124 | 0.0151 | 0.0761 | 96.6667 | 5 | 0.0105 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p34_ld0p36_ls0p65 | 0 | seed_002 | -0.2299 | -0.2262 | 0.0131 | 0.0152 | 0.0624 | 97.3333 | 3 | 0.0116 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55 | 0 | seed_002 | -0.2304 | -0.2278 | 0.0113 | 0.0137 | 0.0737 | 96.6667 | 7 | 0.0117 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p55 | 0 | seed_002 | -0.2313 | -0.2278 | 0.0114 | 0.0136 | 0.0677 | 96.6667 | 6 | 0.0110 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55 | 0 | seed_000 | -0.2329 | -0.2321 | 0.0097 | 0.0121 | 0.0548 | 96.0000 | 5 | 0.0099 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65 | 0 | seed_002 | -0.2350 | -0.2317 | 0.0109 | 0.0132 | 0.0574 | 96.6667 | 7 | 0.0104 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65 | 0 | seed_002 | -0.2366 | -0.2290 | 0.0110 | 0.0130 | 0.0456 | 96.6667 | 7 | 0.0117 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p34_ld0p36_ls0p65 | 0 | seed_002 | -0.2367 | -0.2267 | 0.0122 | 0.0148 | 0.0709 | 97.3333 | 5 | 0.0137 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75 | 0 | seed_002 | -0.2368 | -0.2362 | 0.0101 | 0.0129 | 0.0607 | 96.6667 | 5 | 0.0106 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p36_ls0p55 | 0 | seed_002 | -0.2381 | -0.2357 | 0.0104 | 0.0128 | 0.0599 | 96.6667 | 5 | 0.0109 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75 | 0 | seed_000 | -0.2385 | -0.2261 | 0.0128 | 0.0155 | 0.0661 | 96.6667 | 5 | 0.0120 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65 | 0 | seed_000 | -0.2392 | -0.2293 | 0.0097 | 0.0119 | 0.0696 | 95.3333 | 7 | 0.0110 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p34_ld0p24_ls0p55 | 0 | seed_000 | -0.2395 | -0.2303 | 0.0112 | 0.0132 | 0.0764 | 96.0000 | 7 | 0.0117 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65 | 0 | seed_002 | -0.2397 | -0.2337 | 0.0103 | 0.0126 | 0.0571 | 96.6667 | 5 | 0.0108 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p3_ls0p75 | 0 | seed_000 | -0.2399 | -0.2358 | 0.0126 | 0.0150 | 0.0668 | 97.3333 | 5 | 0.0113 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p048_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p37_ld0p36_ls0p75 | 0 | seed_002 | -0.2403 | -0.2284 | 0.0115 | 0.0140 | 0.0724 | 97.3333 | 5 | 0.0107 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55 | 0 | seed_000 | -0.2408 | -0.2361 | 0.0119 | 0.0140 | 0.0679 | 96.6667 | 7 | 0.0125 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
