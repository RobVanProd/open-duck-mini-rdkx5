# Published Policy Propulsion Audit

overall_status: `PASS_POLICY_CLOSED_LOOP_FORWARD_MOTION`
seed_count: `8`
duration_complete_count: `8`
moving_seed_count_ratio_ge_0p5: `7`
weak_seed_count_ratio_lt_0p5: `1`

## Executive Summary

- The published `BEST_WALK_ONNX_2` policy was evaluated closed-loop in upstream-main `flat_terrain_backlash`.
- 8 of 8 seeds completed the requested horizon.
- 7 of 8 seeds tracked forward command with ratio >= 0.5; 1 remained weak.
- This rules out a blanket claim that upstream-main sim/morphology cannot generate forward locomotion.
- The reference-target/open-loop path remains failed, so the mismatch is in controller/reference execution, not just contact friction.

## Aggregate Metrics

| metric | mean | p50 | p95 | min | max |
|---|---:|---:|---:|---:|---:|
| mean_local_vx_m_s | 0.0640 | 0.0681 | 0.0730 | 0.0392 | 0.0731 |
| command_tracking_ratio | 0.7998 | 0.8509 | 0.9129 | 0.4900 | 0.9136 |
| body_pitch_p95_rad | 0.0646 | 0.0562 | 0.0941 | 0.0533 | 0.1013 |
| base_height_min_m | 0.1523 | 0.1517 | 0.1565 | 0.1451 | 0.1568 |
| single_support_pct | 49.4000 | 52.4000 | 54.3800 | 30.0000 | 54.8000 |
| double_support_pct | 50.3500 | 47.6000 | 63.4200 | 45.2000 | 70.0000 |
| future_vx_delta_all_0p1s | 0.0003 | -0.0003 | 0.0038 | -0.0022 | 0.0044 |
| future_vx_delta_single_support_0p1s | 0.0030 | 0.0038 | 0.0087 | -0.0030 | 0.0099 |

## Seed Summary

| seed | status | samples | termination | mean_vx | track_ratio | pitch_p95 | height_min | single_% | double_% | single_dvx_0p1s |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0714 | 0.8925 | 0.0566 | 0.1521 | 52.4000 | 47.6000 | 0.0038 |
| 1 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0619 | 0.7740 | 0.0592 | 0.1513 | 48.8000 | 51.2000 | -0.0030 |
| 2 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0731 | 0.9136 | 0.0533 | 0.1510 | 52.4000 | 47.6000 | -0.0002 |
| 3 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0572 | 0.7148 | 0.1013 | 0.1568 | 50.4000 | 48.4000 | 0.0042 |
| 4 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0392 | 0.4900 | 0.0807 | 0.1506 | 30.0000 | 70.0000 | 0.0066 |
| 5 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0682 | 0.8531 | 0.0553 | 0.1451 | 53.6000 | 45.6000 | -0.0009 |
| 6 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0679 | 0.8487 | 0.0549 | 0.1556 | 54.8000 | 45.2000 | 0.0099 |
| 7 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0729 | 0.9114 | 0.0558 | 0.1558 | 52.8000 | 47.2000 | 0.0037 |

## Reference Comparison

- reference_artifact: `outputs/analysis/reference_push_effectiveness_upstream_main_backlash_nearest.json`
- reference_status: `HOLD_REFERENCE_CONTACT_MISMATCH`
- best_variant: `reference_motion_rollout_upstream_main_backlash_nearest_contact_synchronized_projected_traces`
- best_reference_single_future_vx_delta_mean_m_s: `-0.0051`
- best_mean_local_vx_m_s: `NA`
- best_contact_mismatch_pct: `20.1366`

## Interpretation

- Contact/friction substitution did not make the reference-target path propel forward.
- The published ONNX policy does propel forward closed-loop in the same upstream-main backlash task.
- Next work should compare the published policy's closed-loop contact/CoM strategy against the failed reference-target teacher path.
- Do not resume robot motion from this result; it is an offline sim finding.
