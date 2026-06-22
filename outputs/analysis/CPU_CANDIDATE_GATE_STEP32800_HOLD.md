# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
policy: `/tmp/open_duck_actuator_bridge_pilots/smoke_20260622T073238Z_cpu/2026_06_22_033329_32800.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.08`
duration_s: `2.0`
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

status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
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

status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`

| metric | value | threshold |
|---|---:|---:|
| `max_action_saturation_pct` | 89.0909 | 1.0000 |
| `max_pitch_tracking_p95_rad` | 0.2982 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 2.2964 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 1.3606 | 0.2500 |
| `min_base_height_m` | 0.0504 | 0.1200 |
| `min_reward_mean` | 0.2309 | 0.3000 |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | reward_mean |
|---|---:|---|---:|---:|---:|
| vanilla | 47 | fall_or_nan | 1.3606 | 0.0590 | 0.2309 |
| fitted | 47 | fall_or_nan | 1.3606 | 0.0504 | 0.2333 |
| stress | 55 | fall_or_nan | 0.5767 | 0.1181 | 0.2795 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 1.9629 | 1.9629 | 0.0000 | 0.2429 | 0 | 85.11 |
| vanilla | left_knee | 1.4387 | 1.4387 | 0.0000 | 0.1704 | 0 | 85.11 |
| vanilla | left_ankle | 2.2964 | 2.2964 | 0.0000 | 0.1133 | 0 | 0.00 |
| vanilla | right_hip_pitch | 1.9038 | 1.9038 | 0.0000 | 0.0615 | 0 | 82.98 |
| vanilla | right_knee | 1.4097 | 1.4097 | 0.0000 | 0.1269 | 0 | 87.23 |
| vanilla | right_ankle | 1.6415 | 1.6415 | 0.0000 | 0.2977 | 0 | 74.47 |
| fitted | left_hip_pitch | 2.1471 | 1.7964 | 0.1217 | 0.2485 | 4 | 85.11 |
| fitted | left_knee | 1.3482 | 1.6817 | 0.1092 | 0.2181 | 4 | 82.98 |
| fitted | left_ankle | 2.1456 | 1.3837 | 0.0516 | 0.1413 | 3 | 0.00 |
| fitted | right_hip_pitch | 2.0310 | 1.5624 | 0.1329 | 0.1628 | 4 | 82.98 |
| fitted | right_knee | 1.3918 | 1.7699 | 0.1244 | 0.1903 | 4 | 87.23 |
| fitted | right_ankle | 1.5134 | 1.7383 | 0.1181 | 0.2982 | 4 | 68.09 |
| stress | left_hip_pitch | 1.6490 | 1.1241 | 0.2226 | 0.2468 | 10 | 87.27 |
| stress | left_knee | 1.4093 | 1.0160 | 0.2061 | 0.2465 | 10 | 85.45 |
| stress | left_ankle | 1.6752 | 0.5444 | 0.0969 | 0.1333 | 10 | 0.00 |
| stress | right_hip_pitch | 1.8999 | 1.1743 | 0.2247 | 0.2364 | 10 | 85.45 |
| stress | right_knee | 1.2586 | 1.1023 | 0.2147 | 0.2305 | 11 | 89.09 |
| stress | right_ankle | 1.1842 | 1.0605 | 0.2179 | 0.2820 | 11 | 83.64 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
