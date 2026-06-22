# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/open_duck_mini_actuator_bridge_cpu_pilot_20260622_step8240/candidate.onnx`
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
| `max_pitch_tracking_p95_rad` | 0.0550 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 0.1962 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 0.0246 | 0.2500 |
| `min_base_height_m` | 0.1536 | 0.1200 |
| `min_reward_mean` | 0.5406 | 0.3000 |
| `min_forward_command_tracking_ratio` | -0.0017 | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.0801 | NA |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| vanilla | 750 | duration_complete | 0.0246 | 0.1538 | 0.0002 | 0.0020 | 0.5406 |
| fitted | 750 | duration_complete | 0.0246 | 0.1536 | -0.0000 | -0.0001 | 0.5429 |
| stress | 750 | duration_complete | 0.0202 | 0.1536 | -0.0001 | -0.0017 | 0.5471 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 0.1374 | 0.1374 | 0.0000 | 0.0155 | 0 | 0.00 |
| vanilla | left_knee | 0.1955 | 0.1955 | 0.0000 | 0.0476 | 0 | 0.00 |
| vanilla | left_ankle | 0.1293 | 0.1293 | 0.0000 | 0.0211 | 0 | 0.00 |
| vanilla | right_hip_pitch | 0.0766 | 0.0766 | 0.0000 | 0.0231 | 0 | 0.00 |
| vanilla | right_knee | 0.1250 | 0.1250 | 0.0000 | 0.0550 | 0 | 0.00 |
| vanilla | right_ankle | 0.0576 | 0.0576 | 0.0000 | 0.0137 | 0 | 0.00 |
| fitted | left_hip_pitch | 0.1494 | 0.1414 | 0.0098 | 0.0160 | 3 | 0.00 |
| fitted | left_knee | 0.1962 | 0.1916 | 0.0135 | 0.0528 | 3 | 0.00 |
| fitted | left_ankle | 0.1261 | 0.1228 | 0.0087 | 0.0225 | 4 | 0.00 |
| fitted | right_hip_pitch | 0.0794 | 0.0757 | 0.0052 | 0.0257 | 3 | 0.00 |
| fitted | right_knee | 0.1227 | 0.1195 | 0.0082 | 0.0546 | 3 | 0.00 |
| fitted | right_ankle | 0.0632 | 0.0577 | 0.0041 | 0.0114 | 4 | 0.00 |
| stress | left_hip_pitch | 0.1439 | 0.0946 | 0.0179 | 0.0145 | 9 | 0.00 |
| stress | left_knee | 0.1934 | 0.1266 | 0.0244 | 0.0517 | 9 | 0.00 |
| stress | left_ankle | 0.1355 | 0.0875 | 0.0181 | 0.0185 | 10 | 0.00 |
| stress | right_hip_pitch | 0.0887 | 0.0515 | 0.0099 | 0.0233 | 9 | 0.00 |
| stress | right_knee | 0.1317 | 0.0806 | 0.0153 | 0.0546 | 9 | 0.00 |
| stress | right_ankle | 0.0619 | 0.0339 | 0.0070 | 0.0123 | 10 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
