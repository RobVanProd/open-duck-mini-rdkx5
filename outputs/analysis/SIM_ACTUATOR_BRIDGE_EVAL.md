# Sim Actuator Bridge Eval

overall_status: `HOLD_POLICY_SIM_CONTRACT_MISMATCH`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/policy/BEST_WALK_ONNX_2.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.08`
duration_s: `15.0`

## Contract Preflight

- policy_status: `PASS_POLICY_CONTRACT_ASSUMED`
- policy_input_shape: `[1, 101]`
- policy_output_shape: `[1, 14]`
- playground_status: `PASS_PLAYGROUND_CONTRACT_READ`
- playground_action_dim_inferred: `10`
- sim_preflight_status: `HOLD_POLICY_SIM_CONTRACT_MISMATCH`
- sim_preflight_reason: policy action dim is 14, but discovered playground JOINTS_ORDER_NO_HEAD has 10 actuators

## Telemetry Replay Bridge Check

status: `PASS_TELEMETRY_REPLAY_REPRODUCTION`
telemetry_jsonl: `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds.jsonl`
samples_after_startup_filter: `696`
- fitted_bridge median sim/real p95 tracking ratio: `0.981`
- fitted_bridge max p95 model error: `0.0351`

### Pitch-Chain Summary

| mode | joint | target_vel_p95 | applied_vel_p95 | sim_tracking_p95 | real_tracking_p95 | model_error_p95 | lag_ticks |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla_no_bridge | left_hip_pitch | 5.2170 | 5.2170 | 0.0000 | 0.1736 | 0.1736 | 0 |
| vanilla_no_bridge | left_knee | 3.7804 | 3.7804 | 0.0000 | 0.1793 | 0.1793 | 0 |
| vanilla_no_bridge | left_ankle | 3.7382 | 3.7382 | 0.0000 | 0.1325 | 0.1325 | 0 |
| vanilla_no_bridge | right_hip_pitch | 3.1012 | 3.1012 | 0.0000 | 0.1661 | 0.1661 | 0 |
| vanilla_no_bridge | right_knee | 4.8109 | 4.8109 | 0.0000 | 0.2062 | 0.2062 | 0 |
| vanilla_no_bridge | right_ankle | 3.5222 | 3.5222 | 0.0000 | 0.1428 | 0.1428 | 0 |
| fitted_bridge | left_hip_pitch | 5.2170 | 2.5000 | 0.1699 | 0.1736 | 0.0252 | 4 |
| fitted_bridge | left_knee | 3.7804 | 3.2329 | 0.1824 | 0.1793 | 0.0335 | 3 |
| fitted_bridge | left_ankle | 3.7382 | 2.9639 | 0.1438 | 0.1325 | 0.0193 | 3 |
| fitted_bridge | right_hip_pitch | 3.1012 | 2.7027 | 0.1632 | 0.1661 | 0.0286 | 3 |
| fitted_bridge | right_knee | 4.8109 | 3.0000 | 0.2008 | 0.2062 | 0.0351 | 4 |
| fitted_bridge | right_ankle | 3.5222 | 2.2500 | 0.1397 | 0.1428 | 0.0273 | 4 |
| stress_bridge | left_hip_pitch | 5.2170 | 1.1628 | 0.1518 | 0.1736 | 0.1266 | 8 |
| stress_bridge | left_knee | 3.7804 | 1.3353 | 0.1880 | 0.1793 | 0.1676 | 8 |
| stress_bridge | left_ankle | 3.7382 | 0.9866 | 0.1308 | 0.1325 | 0.1339 | 9 |
| stress_bridge | right_hip_pitch | 3.1012 | 0.9824 | 0.1449 | 0.1661 | 0.1459 | 8 |
| stress_bridge | right_knee | 4.8109 | 1.2910 | 0.1602 | 0.2062 | 0.1567 | 8 |
| stress_bridge | right_ankle | 3.5222 | 0.9629 | 0.1407 | 0.1428 | 0.1288 | 9 |

## Interpretation

- Full MuJoCo policy-loop reproduction is blocked by a policy/playground contract mismatch. Do not train until the exact 101-observation / 14-action training environment is located or reconstructed.
- Telemetry replay validates the actuator bridge against existing real sent-target / actual-position evidence, but it is not a replacement for closed-loop sim reproduction.
- No robot motion, deployment, runtime behavior change, or training was performed.
