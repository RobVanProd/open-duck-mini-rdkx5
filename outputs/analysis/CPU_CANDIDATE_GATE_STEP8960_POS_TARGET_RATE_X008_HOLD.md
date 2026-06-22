# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
policy: `/tmp/open_duck_actuator_bridge_cpu_pilots/smoke_20260622T071638Z_cpu/2026_06_22_031816_8960.onnx`
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
| `max_pitch_tracking_p95_rad` | 0.0608 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 0.2130 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 0.0114 | 0.2500 |
| `min_base_height_m` | 0.1537 | 0.1200 |
| `min_reward_mean` | 0.5410 | 0.3000 |
| `min_forward_command_tracking_ratio` | -0.0027 | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.0802 | NA |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| vanilla | 750 | duration_complete | -0.0114 | 0.1537 | -0.0002 | -0.0027 | 0.5410 |
| fitted | 750 | duration_complete | -0.0100 | 0.1537 | 0.0001 | 0.0008 | 0.5437 |
| stress | 750 | duration_complete | -0.0043 | 0.1537 | -0.0001 | -0.0015 | 0.5484 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 0.0917 | 0.0917 | 0.0000 | 0.0154 | 0 | 0.00 |
| vanilla | left_knee | 0.1977 | 0.1977 | 0.0000 | 0.0475 | 0 | 0.00 |
| vanilla | left_ankle | 0.1745 | 0.1745 | 0.0000 | 0.0162 | 0 | 0.00 |
| vanilla | right_hip_pitch | 0.0798 | 0.0798 | 0.0000 | 0.0152 | 0 | 0.00 |
| vanilla | right_knee | 0.2077 | 0.2077 | 0.0000 | 0.0512 | 0 | 0.00 |
| vanilla | right_ankle | 0.1026 | 0.1026 | 0.0000 | 0.0057 | 0 | 0.00 |
| fitted | left_hip_pitch | 0.0964 | 0.0942 | 0.0065 | 0.0162 | 3 | 0.00 |
| fitted | left_knee | 0.1948 | 0.1857 | 0.0129 | 0.0581 | 3 | 0.00 |
| fitted | left_ankle | 0.1811 | 0.1709 | 0.0119 | 0.0210 | 3 | 0.00 |
| fitted | right_hip_pitch | 0.0766 | 0.0746 | 0.0052 | 0.0171 | 3 | 0.00 |
| fitted | right_knee | 0.2130 | 0.2046 | 0.0143 | 0.0581 | 3 | 0.00 |
| fitted | right_ankle | 0.1048 | 0.1009 | 0.0070 | 0.0112 | 4 | 0.00 |
| stress | left_hip_pitch | 0.0792 | 0.0458 | 0.0088 | 0.0166 | 9 | 0.00 |
| stress | left_knee | 0.1839 | 0.1171 | 0.0228 | 0.0608 | 9 | 0.00 |
| stress | left_ankle | 0.1708 | 0.1069 | 0.0215 | 0.0175 | 10 | 0.00 |
| stress | right_hip_pitch | 0.0897 | 0.0563 | 0.0106 | 0.0178 | 9 | 0.00 |
| stress | right_knee | 0.1924 | 0.1215 | 0.0230 | 0.0574 | 9 | 0.00 |
| stress | right_ankle | 0.0992 | 0.0606 | 0.0122 | 0.0088 | 10 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
