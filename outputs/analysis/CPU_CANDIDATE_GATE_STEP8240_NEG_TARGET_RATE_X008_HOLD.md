# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
policy: `/tmp/open_duck_actuator_bridge_pilots_negative/smoke_20260622T083747Z_cpu/2026_06_22_043831_8240.onnx`
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
| `max_pitch_tracking_p95_rad` | 0.0541 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 0.1843 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 0.0121 | 0.2500 |
| `min_base_height_m` | 0.1536 | 0.1200 |
| `min_reward_mean` | 0.5398 | 0.3000 |
| `min_forward_command_tracking_ratio` | 0.0002 | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.0800 | NA |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| vanilla | 750 | duration_complete | 0.0111 | 0.1537 | 0.0002 | 0.0030 | 0.5454 |
| fitted | 750 | duration_complete | 0.0121 | 0.1536 | 0.0002 | 0.0024 | 0.5398 |
| stress | 750 | duration_complete | 0.0030 | 0.1536 | 0.0000 | 0.0002 | 0.5448 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 0.1600 | 0.1600 | 0.0000 | 0.0154 | 0 | 0.00 |
| vanilla | left_knee | 0.1714 | 0.1714 | 0.0000 | 0.0436 | 0 | 0.00 |
| vanilla | left_ankle | 0.1061 | 0.1061 | 0.0000 | 0.0225 | 0 | 0.00 |
| vanilla | right_hip_pitch | 0.1269 | 0.1269 | 0.0000 | 0.0273 | 0 | 0.00 |
| vanilla | right_knee | 0.0936 | 0.0936 | 0.0000 | 0.0536 | 0 | 0.00 |
| vanilla | right_ankle | 0.0609 | 0.0609 | 0.0000 | 0.0121 | 0 | 0.00 |
| fitted | left_hip_pitch | 0.1664 | 0.1618 | 0.0113 | 0.0197 | 4 | 0.00 |
| fitted | left_knee | 0.1744 | 0.1676 | 0.0117 | 0.0472 | 4 | 0.00 |
| fitted | left_ankle | 0.1112 | 0.1100 | 0.0077 | 0.0239 | 3 | 0.00 |
| fitted | right_hip_pitch | 0.1277 | 0.1178 | 0.0084 | 0.0320 | 3 | 0.00 |
| fitted | right_knee | 0.0729 | 0.0659 | 0.0040 | 0.0541 | 3 | 0.00 |
| fitted | right_ankle | 0.0710 | 0.0674 | 0.0045 | 0.0134 | 3 | 0.00 |
| stress | left_hip_pitch | 0.1843 | 0.1168 | 0.0219 | 0.0201 | 9 | 0.00 |
| stress | left_knee | 0.1710 | 0.1144 | 0.0219 | 0.0438 | 9 | 0.00 |
| stress | left_ankle | 0.1287 | 0.0862 | 0.0177 | 0.0228 | 10 | 0.00 |
| stress | right_hip_pitch | 0.1382 | 0.0840 | 0.0156 | 0.0327 | 9 | 0.00 |
| stress | right_knee | 0.0646 | 0.0366 | 0.0065 | 0.0506 | 8 | 0.00 |
| stress | right_ankle | 0.0653 | 0.0399 | 0.0077 | 0.0142 | 9 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
