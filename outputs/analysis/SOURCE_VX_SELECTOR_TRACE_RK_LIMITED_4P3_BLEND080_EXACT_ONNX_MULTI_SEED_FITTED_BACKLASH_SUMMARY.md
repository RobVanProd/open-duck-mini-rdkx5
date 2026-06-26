# Right-Knee-Limited Exact Blend ONNX Multi-Seed Gate

status: `HOLD_STRICT_EVAL_TARGET_VELOCITY_GATE`

## Setup

- policy: `outputs/analysis/source_vx_selector_trace_rk_limited_4p3_blend080_exact_onnx_candidate/candidate.onnx`
- policy_sha256: `8924ba7da021f11ec531c27afde2b74ac3eff04f5c2cdee59a9db6da6a2d1abb`
- input_base: `outputs/analysis/source_vx_selector_trace_rk_limited_4p3_blend080_exact_onnx_multiseed_fitted_backlash`
- task: `flat_terrain_backlash`
- bridge_mode: `fitted`
- command_x: `0.08`
- duration_s: `10.0`

## Aggregate

- seeds: `8`
- duration_complete: `8`
- moving_track_ratio_ge_0p5: `8`
- vx_ge_0p02: `8`
- target_velocity_p95_le_2p5: `0`
- target_velocity_p95_le_3p75: `0`
- tracking_p95_le_0p08: `0`
- mean_track_ratio: `0.5992`
- mean_vx: `0.0479`
- max_sent_p95_min: `4.1979`
- max_sent_p95_max: `4.2994`
- max_tracking_p95_min: `0.2682`
- max_tracking_p95_max: `0.2773`
- worst_tracking_joint_counts: `{'left_hip_pitch': 0, 'left_knee': 0, 'left_ankle': 0, 'right_hip_pitch': 0, 'right_knee': 8, 'right_ankle': 0}`
- fastest_joint_counts: `{'left_hip_pitch': 0, 'left_knee': 0, 'left_ankle': 0, 'right_hip_pitch': 0, 'right_knee': 8, 'right_ankle': 0}`

## Per-Seed Results

| seed | status | termination | vx_mean | track_ratio | max_sent_p95 | max_tracking_p95 | worst_tracking_joint | fastest_joint | body_pitch_p95 | base_height_min |
|---:|---|---|---:|---:|---:|---:|---|---|---:|---:|
| 0 | `HOLD_CANDIDATE_TRACKING` | `duration_complete` | 0.0499 | 0.6240 | 4.2471 | 0.2682 | `right_knee` | `right_knee` | 0.0991 | 0.1520 |
| 1 | `HOLD_CANDIDATE_TRACKING` | `duration_complete` | 0.0455 | 0.5690 | 4.2333 | 0.2773 | `right_knee` | `right_knee` | 0.0984 | 0.1556 |
| 2 | `HOLD_CANDIDATE_TRACKING` | `duration_complete` | 0.0511 | 0.6392 | 4.2524 | 0.2689 | `right_knee` | `right_knee` | 0.0995 | 0.1509 |
| 3 | `HOLD_CANDIDATE_TRACKING` | `duration_complete` | 0.0443 | 0.5542 | 4.1979 | 0.2691 | `right_knee` | `right_knee` | 0.0995 | 0.1549 |
| 4 | `HOLD_CANDIDATE_TRACKING` | `duration_complete` | 0.0494 | 0.6178 | 4.2336 | 0.2698 | `right_knee` | `right_knee` | 0.0970 | 0.1506 |
| 5 | `HOLD_CANDIDATE_TRACKING` | `duration_complete` | 0.0511 | 0.6388 | 4.2242 | 0.2720 | `right_knee` | `right_knee` | 0.0973 | 0.1462 |
| 6 | `HOLD_CANDIDATE_TRACKING` | `duration_complete` | 0.0445 | 0.5561 | 4.2994 | 0.2748 | `right_knee` | `right_knee` | 0.0983 | 0.1557 |
| 7 | `HOLD_CANDIDATE_TRACKING` | `duration_complete` | 0.0476 | 0.5946 | 4.2248 | 0.2756 | `right_knee` | `right_knee` | 0.0991 | 0.1559 |

## Interpretation

- Right-knee 4.3 rad/s action-delta curation preserves 8/8 duration-complete forward replay in the strict ONNX path.
- The strict candidate gate still holds because fitted-bridge target velocity p95 remains above the 2.5 rad/s conservative gate and pitch-chain tracking remains above 0.08 rad.
- Compared with the uncurated exact blend, the right-knee spike source is reduced but not eliminated enough to produce a robot-ready candidate.
- No robot motion, SSH, deploy, runtime behavior change, or training was performed.
