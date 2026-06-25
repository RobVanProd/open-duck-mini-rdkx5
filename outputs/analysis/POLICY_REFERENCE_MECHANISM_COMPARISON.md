# Policy vs Reference Mechanism Comparison

overall_status: `PASS_POLICY_REFERENCE_MECHANISM_SPLIT`
policy_group: `published_policy_closed_loop`
reference_group: `reference_contact_synchronized`

## Executive Summary

- The published policy closed-loop path completes the upstream-main `flat_terrain_backlash` horizon across all eight seeds.
- The best reference-target path still fails to produce forward impulse during reference-requested single-support windows.
- The mechanism split is no longer contact parameters alone; it is closed-loop policy behavior versus open-loop target execution.
- Next work should mine policy state/action/contact timing before authorizing another teacher variant.

## Aggregate Comparison

| group | traces | complete | mean_vx | track_ratio | single_% | double_% | single_dvx_0p1s | vy_p95 | pitch_p95 | target_vel_p95 | tracking_p95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| published_policy_closed_loop | 8 | 8 | 0.0540 | 0.7294 | 44.8000 | 54.9500 | 0.0042 | 0.1883 | 0.0650 | 3.0488 | 0.1277 |
| reference_contact_synchronized | 8 | 7 | 0.0301 | 0.4073 | 19.2500 | 79.9000 | -0.0078 | 0.1347 | 0.2454 | 4.9811 | 0.1184 |
| reference_cycle_projected | 8 | 8 | -0.0114 | -0.1544 | 24.6000 | 74.9500 | 0.0216 | 0.1691 | 0.0495 | 3.7513 | 0.1611 |
| reference_raw | 8 | 7 | -0.0500 | -0.6763 | 41.6389 | 57.3667 | -0.0151 | 0.2314 | 0.0540 | 5.0742 | 0.2123 |

## Contact Sequence Comparison

| group | first_single_tick | longest_single | longest_double | alternations | left_single_% | right_single_% | ref_single_% | mismatch_% | ref_single_dvx | matched_single_dvx |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| published_policy_closed_loop | 2.1250 | 7.6250 | 29.1250 | 16.2500 | 23.1500 | 21.6500 | NA | NA | NA | NA |
| reference_contact_synchronized | 1.7500 | 8.2500 | 19.5000 | 12.8750 | 9.3988 | 9.8512 | 20.2500 | 20.1366 | -0.0051 | -0.0145 |
| reference_cycle_projected | 2.1250 | 6.0000 | 20.2500 | 24.2500 | 12.4000 | 12.2000 | 63.6000 | 72.9500 | -0.0356 | -0.0375 |
| reference_raw | 1.8750 | 10.2500 | 14.0000 | 29.5000 | 20.5722 | 21.0667 | 63.5204 | 66.9833 | -0.0390 | -0.0852 |

## Split Metrics

- policy_minus_reference_mean_vx_m_s: `0.0238`
- policy_minus_reference_single_support_pct: `25.5500`
- policy_minus_reference_single_delta_vx_m_s: `0.0119`

## Interpretation

Published policy closed-loop traces produce stable local forward motion while the best reference-target traces do not. The next branch should copy or constrain the closed-loop state-action/contact mechanism, not keep tuning open-loop target shapes.

Robot validation remains blocked.
