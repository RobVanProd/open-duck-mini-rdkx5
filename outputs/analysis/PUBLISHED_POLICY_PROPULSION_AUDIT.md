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
| mean_local_vx_m_s | 0.0540 | 0.0613 | 0.0655 | 0.0102 | 0.0662 |
| command_tracking_ratio | 0.7294 | 0.8286 | 0.8856 | 0.1373 | 0.8940 |
| body_pitch_p95_rad | 0.0650 | 0.0573 | 0.0896 | 0.0528 | 0.0967 |
| base_height_min_m | 0.1523 | 0.1516 | 0.1566 | 0.1452 | 0.1570 |
| single_support_pct | 44.8000 | 50.4000 | 53.3200 | 5.6000 | 53.6000 |
| double_support_pct | 54.9500 | 49.0000 | 80.8200 | 45.6000 | 94.4000 |
| future_vx_delta_all_0p1s | 0.0001 | -0.0002 | 0.0036 | -0.0029 | 0.0042 |
| future_vx_delta_single_support_0p1s | 0.0042 | 0.0029 | 0.0129 | -0.0006 | 0.0167 |

## Seed Summary

| seed | status | samples | termination | mean_vx | track_ratio | pitch_p95 | height_min | single_% | double_% | single_dvx_0p1s |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0662 | 0.8940 | 0.0528 | 0.1520 | 51.6000 | 48.4000 | 0.0032 |
| 1 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0504 | 0.6809 | 0.0765 | 0.1511 | 44.4000 | 55.6000 | 0.0026 |
| 2 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0618 | 0.8347 | 0.0727 | 0.1510 | 48.4000 | 51.6000 | 0.0006 |
| 3 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0540 | 0.7300 | 0.0967 | 0.1570 | 49.2000 | 49.6000 | 0.0058 |
| 4 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0102 | 0.1373 | 0.0612 | 0.1506 | 5.6000 | 94.4000 | 0.0167 |
| 5 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0644 | 0.8700 | 0.0532 | 0.1452 | 53.6000 | 45.6000 | -0.0006 |
| 6 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0609 | 0.8226 | 0.0535 | 0.1556 | 52.8000 | 47.2000 | 0.0047 |
| 7 | `PASS_CLOSED_LOOP_REPRODUCTION` | 250 | `duration_complete` | 0.0640 | 0.8653 | 0.0531 | 0.1558 | 52.8000 | 47.2000 | 0.0001 |

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
