# Exact Blend ONNX Multi-Seed Fitted Backlash Summary

status: `HOLD_EXACT_BLEND_ONNX_RIGHT_KNEE_RATE_TRACKING`

This is an offline standard closed-loop ONNX evaluation. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Setup

- policy_onnx: `outputs/analysis/source_vx_selector_trace_blend080_exact_onnx_candidate/candidate.onnx`
- policy_sha256: `23954caf77823c59524675c55e2e5ed6796877b52b4fea9bc7fa40f61e66bba4`
- contract: `obs[1,101] -> continuous_actions[1,14]`
- task: `flat_terrain_backlash`
- command_x: `0.08`
- duration_s: `10`
- bridge_mode: `fitted`
- seeds: `0,1,2,3,4,5,6,7`

## Aggregate Result

- duration_complete_count: `8 / 8`
- moving_seed_count_ratio_ge_0p5: `8 / 8`
- moving_seed_count_vx_ge_0p02: `8 / 8`
- mean_track_ratio: `0.5768`
- mean_local_vx_m_s: `0.0461`
- track_ratio_range: `0.5050-0.6288`
- max_pitch_chain_sent_target_p95_range_rad_s: `4.7355-5.1118`
- max_pitch_chain_tracking_p95_range_rad: `0.2679-0.2800`
- envelope_safe_seed_count_3p75: `0 / 8`
- standard_gate_safe_seed_count_2p5: `0 / 8`
- tracking_safe_seed_count_0p08: `0 / 8`
- dominant_failure_joint: `right_knee`

## Per-Seed Rows

| seed | term | vx | ratio | pitch95 | height_min | max_sent_p95 | worst_sent_joint | max_track_p95 | worst_track_joint |
|---:|---|---:|---:|---:|---:|---:|---|---:|---|
| 0 | duration_complete | 0.0490 | 0.6123 | 0.0991 | 0.1520 | 4.9005 | `right_knee` | 0.2679 | `right_knee` |
| 1 | duration_complete | 0.0457 | 0.5711 | 0.0989 | 0.1556 | 4.9503 | `right_knee` | 0.2771 | `right_knee` |
| 2 | duration_complete | 0.0484 | 0.6044 | 0.1003 | 0.1509 | 5.0372 | `right_knee` | 0.2767 | `right_knee` |
| 3 | duration_complete | 0.0404 | 0.5050 | 0.0973 | 0.1549 | 5.1118 | `right_knee` | 0.2756 | `right_knee` |
| 4 | duration_complete | 0.0461 | 0.5759 | 0.0970 | 0.1506 | 4.8427 | `right_knee` | 0.2744 | `right_knee` |
| 5 | duration_complete | 0.0503 | 0.6288 | 0.0963 | 0.1462 | 4.7355 | `right_knee` | 0.2718 | `right_knee` |
| 6 | duration_complete | 0.0433 | 0.5410 | 0.0967 | 0.1557 | 5.0060 | `right_knee` | 0.2761 | `right_knee` |
| 7 | duration_complete | 0.0461 | 0.5757 | 0.0966 | 0.1559 | 4.9467 | `right_knee` | 0.2800 | `right_knee` |

## Interpretation

- Exact ONNX export preserves the source-switch-free blend behavior at the action level: the export verifies against the Python blend to roughly `1e-7` and all eight standard-eval seeds complete 10 seconds.
- It is still not a promotion candidate. Every seed exceeds the fitted pitch-chain target-rate envelope, and the worst joint is consistently `right_knee`.
- This result is stronger than the DAgger-2 MLP for forward progress, but it confirms that the current blend baseline itself has a hidden max-joint pitch-chain rate/tracking problem in the stricter evaluator.
- Do not run this policy on the robot. The next offline branch needs to preserve the blend closed-loop motion while specifically reducing the right-knee pitch-chain target-rate and tracking peak.
