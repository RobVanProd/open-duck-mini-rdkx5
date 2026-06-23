# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/movement_bootstrap_v5_phase1_in_envelope_unstable_20260623/candidate.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.08`
duration_s: `15.0`
eval_role: `candidate`
jax_platform_requested: `cpu`

## Contract Preflight

- policy_status: `PASS_POLICY_CONTRACT_ASSUMED`
- policy_input_shape: `[1, 101]`
- policy_output_shape: `[1, 14]`
- playground_static_path: `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2`
- playground_env_python: `/home/lsd/robots/open-duck-mini-rdkx5/../envs/open-duck-playground/bin/python`
- playground_instantiated_status: `PASS_ENV_INSTANTIATED`
- playground_action_size: `14`
- playground_observation_size: `{'privileged_state': [212], 'state': [101]}`
- playground_actuator_names: `['left_hip_yaw', 'left_hip_roll', 'left_hip_pitch', 'left_knee', 'left_ankle', 'neck_pitch', 'head_pitch', 'head_yaw', 'head_roll', 'right_hip_yaw', 'right_hip_roll', 'right_hip_pitch', 'right_knee', 'right_ankle']`
- sim_preflight_status: `HOLD_SIM_INTEGRATION_PENDING`
- sim_preflight_reason: Policy and local Playground dimensions appear compatible, but the closed-loop JAX/MJX policy eval path with actuator bridge is not wired yet.
- recommended_next_command: `python3 tools/audit_policy_sim_contract.py --policy policy/BEST_WALK_ONNX_2.onnx --playground-path ../Open_Duck_Playground`

## Closed-Loop Sim Eval

status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
eval_role: `candidate`
policy_action_gain: `1.0`
env: `playground.open_duck_mini_v2.joystick.Joystick` / task `flat_terrain`
obs/action dims: `{'privileged_state': [212], 'state': [101]}` / `14`
actuator_names: `['left_hip_yaw', 'left_hip_roll', 'left_hip_pitch', 'left_knee', 'left_ankle', 'neck_pitch', 'head_pitch', 'head_yaw', 'head_roll', 'right_hip_yaw', 'right_hip_roll', 'right_hip_pitch', 'right_knee', 'right_ankle']`
ctrl_dt: `0.02`
sim_dt: `0.002`
mjx_step_loop_mode: `default`
max_motor_velocity: `5.24`
jax: `cpu` `['TFRT_CPU_0']`
insertion_point: `target_stage_direct`
double_rate_limit: `False`
worker_returncode: `0`

Worker output excerpt:

```text
Failed to import warp: No module named 'warp'
Failed to import mujoco_warp: No module named 'warp'
```

### Candidate Gate

status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`

| metric | value | threshold |
|---|---:|---:|
| `max_action_saturation_pct` | 0.0000 | 1.0000 |
| `max_pitch_tracking_p95_rad` | 0.1429 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 1.9529 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 1.1841 | 0.2500 |
| `min_base_height_m` | 0.0434 | 0.1200 |
| `min_reward_mean` | 0.4234 | 0.3000 |
| `min_forward_command_tracking_ratio` | 2.3652 | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.1092 | NA |
| `max_forward_shortfall_cost_mean` | 0.0331 | NA |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| fitted | 80 | fall_or_nan | 1.1841 | 0.0434 | 0.1892 | 2.3652 | 0.4234 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| fitted | `cost/action_rate` | 0.0315 | 0.1067 | 1.2419 |
| fitted | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `cost/torques` | 0.0042 | 0.0086 | 0.0463 |
| fitted | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| fitted | `reward/imitation` | -1.1776 | 1.2465 | 1.7986 |
| fitted | `reward/tracking_ang_vel` | 0.7849 | 4.0179 | 5.9806 |
| fitted | `reward/tracking_lin_vel` | 1.5967 | 2.4890 | 2.4997 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| fitted | `PASS_DIAGNOSTIC` | 0.5000 | 2.3652 | 10.6699 | 0.0457 | 0.0331 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| fitted | left_hip_pitch | 1.2992 | 1.3415 | 0.0853 | 0.1253 | 3 | 0.00 |
| fitted | left_knee | 0.9235 | 0.7040 | 0.0402 | 0.1052 | 3 | 0.00 |
| fitted | left_ankle | 1.1361 | 1.0456 | 0.0528 | 0.0859 | 3 | 0.00 |
| fitted | right_hip_pitch | 0.6453 | 0.7428 | 0.0236 | 0.0468 | 3 | 0.00 |
| fitted | right_knee | 1.9529 | 1.1268 | 0.0413 | 0.0841 | 3 | 0.00 |
| fitted | right_ankle | 1.3538 | 1.4963 | 0.1049 | 0.1429 | 4 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
