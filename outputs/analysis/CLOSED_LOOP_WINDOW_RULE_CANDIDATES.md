# Closed-Loop Window Rule Candidates

status: `PASS_RULE_CONTRAST_READY`

This is an offline analysis of existing BEST_WALK full-observation traces. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Criteria

- window_samples: `10`
- stride_samples: `2`
- dt_s: `0.02`
- future_ticks: `5`
- envelope_high: `3.75`
- min_mean_vx: `0.04`
- min_tick_vx: `0.04`
- min_single_support_pct: `20.0`
- min_moving_in_envelope_pct: `40.0`
- min_moving_single_in_envelope_pct: `10.0`
- max_vy_abs_p95: `0.2`
- max_body_pitch_abs_p95: `0.2`
- min_base_height: `0.145`

## Bucket Summary

| bucket | windows | vx | single_% | move_env_% | move_single_env_% | single_dvx | stance_dx | stance_abs_dy | pitch_p95 | right_knee_p95 | action_delta_p95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| other | 5 | 0.0514 | 34.0000 | 58.0000 | 2.0000 | 0.0184 | 0.0049 | 0.0494 | 3.3525 | 3.3119 | 0.1845 |
| pass_safe_moving_single | 330 | 0.0721 | 46.7879 | 81.6061 | 34.1212 | -0.0030 | -0.0114 | 0.0476 | 3.2896 | 2.1407 | 0.1678 |
| reject_high_rate_moving | 1233 | 0.0667 | 53.0981 | 64.1281 | 30.9570 | 0.0020 | -0.0209 | 0.0492 | 4.7046 | 4.0445 | 0.2053 |
| reject_low_progress | 1214 | 0.0008 | 5.8814 | 2.6524 | 0.5272 | 0.0139 | 0.0031 | 0.0480 | 0.8400 | 0.6684 | 0.0497 |
| review_lateral | 106 | 0.0712 | 60.6604 | 83.3019 | 48.4906 | 0.0015 | -0.0109 | 0.0484 | 3.2394 | 2.2968 | 0.1800 |
| review_low_support | 16 | 0.0530 | 5.0000 | 68.7500 | 1.2500 | 0.0138 | -0.0268 | 0.0471 | 1.8727 | 1.4654 | 0.1040 |

## By Command Cell

| command_cell | other | pass_safe_moving_single | reject_high_rate_moving | reject_low_progress | review_lateral | review_low_support |
|---|---:|---:|---:|---:|---:|---:|
| straight_x004 | 1 | 5 | 22 | 936 | 1 | 3 |
| straight_x008 | 1 | 206 | 567 | 99 | 90 | 5 |
| turning_x0074_yneg0037_yawneg0074 | 3 | 119 | 644 | 179 | 15 | 8 |

## Reason Counts

- high_pitch_velocity_p95: `1375`
- low_moving_single_in_envelope: `1240`
- low_moving_in_envelope: `1222`
- low_mean_vx: `1214`
- low_single_support: `1074`
- high_lateral_velocity: `488`
- low_base_height: `2`

## Fastest Pitch Joint Counts

- right_knee: `1360`
- left_knee: `1048`
- right_hip_pitch: `247`
- left_ankle: `113`
- left_hip_pitch: `79`
- right_ankle: `57`

## Interpretation

- `pass_safe_moving_single` windows meet the short-window movement, contact, stability, and pitch-rate gates.
- `reject_high_rate_moving` windows move forward but exceed the pitch-chain target-rate envelope.
- Compare these buckets before building a selector: the desired behavior is not simply more velocity, it is velocity with single support and bounded pitch-chain rate.
- If right-knee or left-knee dominates the high-rate bucket, the next branch should explicitly manage knee target-rate during stance transfer.
