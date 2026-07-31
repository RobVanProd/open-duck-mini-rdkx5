# Published Policy Propulsion Audit

overall_status: `WARN_POLICY_FORWARD_MOTION_WEAK_SEEDS`
seed_count: `8`
duration_complete_count: `8`
moving_seed_count_ratio_ge_0p5: `0`
weak_seed_count_ratio_lt_0p5: `8`

## Executive Summary

- The published `BEST_WALK_ONNX_2` policy was evaluated closed-loop in upstream-main `flat_terrain_backlash`.
- 8 of 8 seeds completed the requested horizon.
- 0 of 8 seeds tracked forward command with ratio >= 0.5; 8 remained weak.
- This rules out a blanket claim that upstream-main sim/morphology cannot generate forward locomotion.
- The reference-target/open-loop path remains failed, so the mismatch is in controller/reference execution, not just contact friction.

## Aggregate Metrics

| metric | mean | p50 | p95 | min | max |
|---|---:|---:|---:|---:|---:|
| mean_local_vx_m_s | 0.0019 | 0.0030 | 0.0063 | -0.0075 | 0.0065 |
| command_tracking_ratio | 0.0468 | 0.0761 | 0.1568 | -0.1873 | 0.1626 |
| body_pitch_p95_rad | 0.0394 | 0.0339 | 0.0826 | 0.0136 | 0.1047 |
| base_height_min_m | 0.1520 | 0.1521 | 0.1557 | 0.1450 | 0.1558 |
| single_support_pct | 3.6500 | 3.2000 | 6.6000 | 1.6000 | 8.0000 |
| double_support_pct | 96.1000 | 96.8000 | 97.4600 | 91.2000 | 97.6000 |
| future_vx_delta_all_0p1s | -0.0010 | -0.0015 | 0.0025 | -0.0035 | 0.0031 |
| future_vx_delta_single_support_0p1s | -0.0155 | -0.0076 | 0.0182 | -0.0617 | 0.0232 |

## Seed Summary

| seed | status | samples | termination | mean_vx | track_ratio | pitch_p95 | height_min | single_% | double_% | single_dvx_0p1s |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0039 | 0.0968 | 0.0416 | 0.1521 | 2.4000 | 97.6000 | 0.0036 |
| 1 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0010 | 0.0240 | 0.0408 | 0.1522 | 4.0000 | 96.0000 | -0.0617 |
| 2 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0058 | 0.1460 | 0.0136 | 0.1511 | 2.8000 | 97.2000 | -0.0561 |
| 3 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | -0.0075 | -0.1873 | 0.1047 | 0.1537 | 1.6000 | 97.2000 | -0.0019 |
| 4 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0065 | 0.1626 | 0.0243 | 0.1507 | 2.8000 | 97.2000 | 0.0088 |
| 5 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0043 | 0.1082 | 0.0227 | 0.1450 | 8.0000 | 91.2000 | -0.0133 |
| 6 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | -0.0013 | -0.0313 | 0.0281 | 0.1556 | 4.0000 | 96.0000 | 0.0232 |
| 7 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0022 | 0.0554 | 0.0398 | 0.1558 | 3.6000 | 96.4000 | -0.0264 |

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
