# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
policy: `/content/open_duck_staged_curriculum_cli/03_phase3_consolidate_progress_no_lunge/smoke_20260623T234521Z_gpu/2026_06_23_235119_122880.onnx`
fit_json: `/content/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.08`
duration_s: `15.0`
eval_role: `candidate`
jax_platform_requested: `gpu`

## Contract Preflight

- policy_status: `PASS_POLICY_CONTRACT_ASSUMED`
- policy_input_shape: `[1, 101]`
- policy_output_shape: `[1, 14]`
- playground_static_path: `/content/Open_Duck_Playground/playground/open_duck_mini_v2`
- playground_env_python: `/usr/bin/python3`
- playground_instantiated_status: `PASS_ENV_INSTANTIATED`
- playground_action_size: `14`
- playground_observation_size: `{'privileged_state': [212], 'state': [101]}`
- playground_actuator_names: `['left_hip_yaw', 'left_hip_roll', 'left_hip_pitch', 'left_knee', 'left_ankle', 'neck_pitch', 'head_pitch', 'head_yaw', 'head_roll', 'right_hip_yaw', 'right_hip_roll', 'right_hip_pitch', 'right_knee', 'right_ankle']`
- sim_preflight_status: `HOLD_SIM_INTEGRATION_PENDING`
- sim_preflight_reason: Policy and local Playground dimensions appear compatible, but the closed-loop JAX/MJX policy eval path with actuator bridge is not wired yet.
- recommended_next_command: `python3 tools/audit_policy_sim_contract.py --policy policy/BEST_WALK_ONNX_2.onnx --playground-path ../Open_Duck_Playground`

## Closed-Loop Sim Eval

status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
eval_role: `candidate`
policy_action_gain: `1.0`
env: `playground.open_duck_mini_v2.joystick.Joystick` / task `flat_terrain`
obs/action dims: `{'privileged_state': [212], 'state': [101]}` / `14`
actuator_names: `['left_hip_yaw', 'left_hip_roll', 'left_hip_pitch', 'left_knee', 'left_ankle', 'neck_pitch', 'head_pitch', 'head_yaw', 'head_roll', 'right_hip_yaw', 'right_hip_roll', 'right_hip_pitch', 'right_knee', 'right_ankle']`
ctrl_dt: `0.02`
sim_dt: `0.002`
mjx_step_loop_mode: `default`
max_motor_velocity: `5.24`
jax: `gpu` `['cuda:0']`
insertion_point: `target_stage_direct`
double_rate_limit: `False`
worker_returncode: `0`

Worker output excerpt:

```text
Failed to import warp: No module named 'warp'
Failed to import mujoco_warp: No module named 'warp'
```

### Candidate Gate

status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`

| metric | value | threshold |
|---|---:|---:|
| `max_action_saturation_pct` | 0.0000 | 1.0000 |
| `max_pitch_tracking_p95_rad` | 0.0921 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 0.2879 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 0.2172 | 0.2500 |
| `min_base_height_m` | 0.1479 | 0.1200 |
| `min_reward_mean` | 0.5261 | 0.3000 |
| `min_forward_command_tracking_ratio` | 0.0206 | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.0783 | NA |
| `max_forward_shortfall_cost_mean` | 0.2743 | NA |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| vanilla | 750 | duration_complete | 0.2119 | 0.1501 | 0.0018 | 0.0226 | 0.5261 |
| fitted | 750 | duration_complete | 0.2061 | 0.1503 | 0.0017 | 0.0206 | 0.5371 |
| stress | 750 | duration_complete | 0.2172 | 0.1479 | 0.0023 | 0.0288 | 0.5317 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| vanilla | `cost/action_rate` | 0.0035 | 0.0013 | 1.0220 |
| vanilla | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| vanilla | `cost/torques` | 0.0021 | 0.0022 | 0.0474 |
| vanilla | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| vanilla | `reward/imitation` | -0.2439 | 1.7794 | 2.4477 |
| vanilla | `reward/tracking_ang_vel` | 5.2283 | 5.9885 | 6.0000 |
| vanilla | `reward/tracking_lin_vel` | 1.3270 | 1.5668 | 2.4983 |
| fitted | `cost/action_rate` | 0.0039 | 0.0014 | 1.0220 |
| fitted | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `cost/torques` | 0.0021 | 0.0025 | 0.0495 |
| fitted | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| fitted | `reward/imitation` | -0.2225 | 1.8199 | 2.4813 |
| fitted | `reward/tracking_ang_vel` | 5.7488 | 5.9988 | 6.0000 |
| fitted | `reward/tracking_lin_vel` | 1.3337 | 1.4448 | 2.5000 |
| stress | `cost/action_rate` | 0.0040 | 0.0012 | 1.0220 |
| stress | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| stress | `cost/torques` | 0.0021 | 0.0023 | 0.0495 |
| stress | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| stress | `reward/imitation` | -0.2159 | 1.8954 | 2.0239 |
| stress | `reward/tracking_ang_vel` | 5.4910 | 5.9876 | 6.0000 |
| stress | `reward/tracking_lin_vel` | 1.3178 | 1.6667 | 2.5000 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| vanilla | `PASS_DIAGNOSTIC` | 0.5000 | 0.0226 | 0.1458 | 0.4956 | 0.2654 |
| fitted | `PASS_DIAGNOSTIC` | 0.5000 | 0.0206 | 0.0751 | 0.4931 | 0.2574 |
| stress | `PASS_DIAGNOSTIC` | 0.5000 | 0.0288 | 0.2077 | 0.4933 | 0.2743 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 0.1667 | 0.1667 | 0.0000 | 0.0232 | 0 | 0.00 |
| vanilla | left_knee | 0.2452 | 0.2452 | 0.0000 | 0.0687 | 0 | 0.00 |
| vanilla | left_ankle | 0.2879 | 0.2879 | 0.0000 | 0.0242 | 0 | 0.00 |
| vanilla | right_hip_pitch | 0.1132 | 0.1132 | 0.0000 | 0.0328 | 0 | 0.00 |
| vanilla | right_knee | 0.1947 | 0.1947 | 0.0000 | 0.0662 | 0 | 0.00 |
| vanilla | right_ankle | 0.2340 | 0.2340 | 0.0000 | 0.0466 | 0 | 0.00 |
| fitted | left_hip_pitch | 0.1863 | 0.1780 | 0.0123 | 0.0289 | 3 | 0.00 |
| fitted | left_knee | 0.2337 | 0.2253 | 0.0157 | 0.0806 | 4 | 0.00 |
| fitted | left_ankle | 0.2754 | 0.2596 | 0.0180 | 0.0313 | 3 | 0.00 |
| fitted | right_hip_pitch | 0.1290 | 0.1189 | 0.0082 | 0.0353 | 3 | 0.00 |
| fitted | right_knee | 0.2292 | 0.2246 | 0.0155 | 0.0826 | 3 | 0.00 |
| fitted | right_ankle | 0.2643 | 0.2601 | 0.0181 | 0.0572 | 4 | 0.00 |
| stress | left_hip_pitch | 0.1940 | 0.1101 | 0.0204 | 0.0269 | 8 | 0.00 |
| stress | left_knee | 0.2715 | 0.1642 | 0.0314 | 0.0827 | 9 | 0.00 |
| stress | left_ankle | 0.2250 | 0.1366 | 0.0268 | 0.0295 | 10 | 0.00 |
| stress | right_hip_pitch | 0.1609 | 0.0906 | 0.0168 | 0.0349 | 9 | 0.00 |
| stress | right_knee | 0.2207 | 0.1443 | 0.0275 | 0.0921 | 9 | 0.00 |
| stress | right_ankle | 0.2409 | 0.1541 | 0.0306 | 0.0463 | 10 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
