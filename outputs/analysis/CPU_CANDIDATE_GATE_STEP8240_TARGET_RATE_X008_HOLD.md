# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
policy: `/tmp/open_duck_actuator_bridge_pilots/smoke_20260622T073000Z_cpu/2026_06_22_033042_8240.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.08`
duration_s: `15.0`
eval_role: `candidate`

## Contract Preflight

- policy_status: `PASS_POLICY_CONTRACT_ASSUMED`
- policy_input_shape: `[1, 101]`
- policy_output_shape: `[1, 14]`
- playground_static_path: `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2`
- playground_env_python: `/home/lsd/robots/envs/open-duck-playground/bin/python`
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
env: `playground.open_duck_mini_v2.joystick.Joystick` / task `flat_terrain`
obs/action dims: `{'privileged_state': [212], 'state': [101]}` / `14`
actuator_names: `['left_hip_yaw', 'left_hip_roll', 'left_hip_pitch', 'left_knee', 'left_ankle', 'neck_pitch', 'head_pitch', 'head_yaw', 'head_roll', 'right_hip_yaw', 'right_hip_roll', 'right_hip_pitch', 'right_knee', 'right_ankle']`
ctrl_dt: `0.02`
sim_dt: `0.002`
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

status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`

| metric | value | threshold |
|---|---:|---:|
| `max_action_saturation_pct` | 0.0000 | 1.0000 |
| `max_pitch_tracking_p95_rad` | 0.0508 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 0.2140 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 0.0093 | 0.2500 |
| `min_base_height_m` | 0.1537 | 0.1200 |
| `min_reward_mean` | 0.5412 | 0.3000 |
| `min_forward_command_tracking_ratio` | -0.0039 | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.0803 | NA |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| vanilla | 750 | duration_complete | 0.0078 | 0.1538 | 0.0003 | 0.0042 | 0.5412 |
| fitted | 750 | duration_complete | 0.0093 | 0.1537 | 0.0001 | 0.0007 | 0.5440 |
| stress | 750 | duration_complete | 0.0008 | 0.1537 | -0.0003 | -0.0039 | 0.5429 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 0.1603 | 0.1603 | 0.0000 | 0.0142 | 0 | 0.00 |
| vanilla | left_knee | 0.1629 | 0.1629 | 0.0000 | 0.0457 | 0 | 0.00 |
| vanilla | left_ankle | 0.1924 | 0.1924 | 0.0000 | 0.0250 | 0 | 0.00 |
| vanilla | right_hip_pitch | 0.0801 | 0.0801 | 0.0000 | 0.0234 | 0 | 0.00 |
| vanilla | right_knee | 0.1093 | 0.1093 | 0.0000 | 0.0492 | 0 | 0.00 |
| vanilla | right_ankle | 0.1125 | 0.1125 | 0.0000 | 0.0133 | 0 | 0.00 |
| fitted | left_hip_pitch | 0.1716 | 0.1637 | 0.0115 | 0.0193 | 4 | 0.00 |
| fitted | left_knee | 0.1652 | 0.1604 | 0.0111 | 0.0478 | 4 | 0.00 |
| fitted | left_ankle | 0.1914 | 0.1885 | 0.0132 | 0.0290 | 4 | 0.00 |
| fitted | right_hip_pitch | 0.0848 | 0.0808 | 0.0056 | 0.0270 | 3 | 0.00 |
| fitted | right_knee | 0.1049 | 0.1010 | 0.0070 | 0.0481 | 3 | 0.00 |
| fitted | right_ankle | 0.1202 | 0.1157 | 0.0081 | 0.0138 | 4 | 0.00 |
| stress | left_hip_pitch | 0.1686 | 0.1073 | 0.0206 | 0.0191 | 9 | 0.00 |
| stress | left_knee | 0.1661 | 0.1082 | 0.0206 | 0.0468 | 9 | 0.00 |
| stress | left_ankle | 0.2140 | 0.1399 | 0.0284 | 0.0258 | 10 | 0.00 |
| stress | right_hip_pitch | 0.0997 | 0.0614 | 0.0115 | 0.0230 | 9 | 0.00 |
| stress | right_knee | 0.1186 | 0.0784 | 0.0149 | 0.0508 | 9 | 0.00 |
| stress | right_ankle | 0.1215 | 0.0749 | 0.0151 | 0.0143 | 10 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
