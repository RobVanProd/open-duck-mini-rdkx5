# B0C LK097 Seed 4 Push / Tracking Correlation

status: `INFO_TRACE_LOCALIZATION`

records: `250`
left_knee_abs_error_p95_rad: `0.2013`
left_knee_abs_error_max_rad: `0.2234`
push_windows_ticks: `[(57, 57), (115, 115), (173, 173), (231, 231)]`
high_error_near_push: `13/13` (100.0%)

## Top Left-Knee Error Ticks

| tick | time_s | err | push_mag | contacts | body_pitch | base_height | vx |
|---:|---:|---:|---:|---|---:|---:|---:|
| 131 | 2.62 | 0.2234 | 0.0000 | `[1, 0]` | 0.0876 | 0.1625 | -0.0454 |
| 163 | 3.26 | 0.2166 | 0.0000 | `[1, 0]` | 0.0719 | 0.1622 | -0.0172 |
| 68 | 1.36 | 0.2129 | 0.0000 | `[1, 1]` | -0.0041 | 0.1624 | -0.0219 |
| 132 | 2.64 | 0.2102 | 0.0000 | `[1, 0]` | 0.0747 | 0.1630 | -0.0201 |
| 226 | 4.52 | 0.2095 | 0.0000 | `[1, 0]` | 0.0244 | 0.1659 | 0.0198 |
| 99 | 1.98 | 0.2095 | 0.0000 | `[1, 0]` | 0.0221 | 0.1647 | -0.0220 |
| 67 | 1.34 | 0.2074 | 0.0000 | `[1, 1]` | -0.0098 | 0.1631 | -0.0284 |
| 100 | 2.00 | 0.2071 | 0.0000 | `[1, 0]` | 0.0181 | 0.1644 | 0.0058 |
| 35 | 0.70 | 0.2064 | 0.0000 | `[1, 1]` | 0.0156 | 0.1597 | -0.0332 |
| 36 | 0.72 | 0.2062 | 0.0000 | `[1, 1]` | 0.0193 | 0.1600 | -0.0188 |
| 130 | 2.60 | 0.2041 | 0.0000 | `[1, 0]` | 0.0993 | 0.1626 | -0.0915 |
| 164 | 3.28 | 0.2026 | 0.0000 | `[1, 1]` | 0.0686 | 0.1617 | 0.0091 |

## Interpretation

The candidate gate hold is driven by the left knee p95 tracking margin. This correlation file checks whether the worst left-knee tracking ticks are localized around push impulses.
