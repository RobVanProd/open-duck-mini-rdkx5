# Sim Actuator Bridge Eval

overall_status: `PASS_CANDIDATE_SIM_GATE`
policy: `/tmp/open_duck_actuator_bridge_pilots/smoke_20260622T073127Z_cpu/2026_06_22_033206_8240.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.0`
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

status: `PASS_CANDIDATE_SIM_GATE`
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

status: `PASS_CANDIDATE_SIM_GATE`

| metric | value | threshold |
|---|---:|---:|
| `max_action_saturation_pct` | 0.0000 | 1.0000 |
| `max_pitch_tracking_p95_rad` | 0.0522 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 0.1737 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 0.0136 | 0.2500 |
| `min_base_height_m` | 0.1536 | 0.1200 |
| `min_reward_mean` | 0.5552 | 0.3000 |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | reward_mean |
|---|---:|---|---:|---:|---:|
| vanilla | 750 | duration_complete | 0.0136 | 0.1538 | 0.5552 |
| fitted | 750 | duration_complete | 0.0135 | 0.1536 | 0.5584 |
| stress | 750 | duration_complete | 0.0090 | 0.1536 | 0.5638 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 0.1497 | 0.1497 | 0.0000 | 0.0174 | 0 | 0.00 |
| vanilla | left_knee | 0.1709 | 0.1709 | 0.0000 | 0.0486 | 0 | 0.00 |
| vanilla | left_ankle | 0.1421 | 0.1421 | 0.0000 | 0.0193 | 0 | 0.00 |
| vanilla | right_hip_pitch | 0.0733 | 0.0733 | 0.0000 | 0.0191 | 0 | 0.00 |
| vanilla | right_knee | 0.1055 | 0.1055 | 0.0000 | 0.0496 | 0 | 0.00 |
| vanilla | right_ankle | 0.0698 | 0.0698 | 0.0000 | 0.0101 | 0 | 0.00 |
| fitted | left_hip_pitch | 0.1639 | 0.1529 | 0.0107 | 0.0191 | 3 | 0.00 |
| fitted | left_knee | 0.1720 | 0.1678 | 0.0119 | 0.0522 | 3 | 0.00 |
| fitted | left_ankle | 0.1402 | 0.1366 | 0.0096 | 0.0208 | 4 | 0.00 |
| fitted | right_hip_pitch | 0.0741 | 0.0697 | 0.0046 | 0.0213 | 3 | 0.00 |
| fitted | right_knee | 0.1032 | 0.0959 | 0.0068 | 0.0491 | 3 | 0.00 |
| fitted | right_ankle | 0.0721 | 0.0691 | 0.0049 | 0.0093 | 4 | 0.00 |
| stress | left_hip_pitch | 0.1581 | 0.1037 | 0.0195 | 0.0180 | 9 | 0.00 |
| stress | left_knee | 0.1737 | 0.1138 | 0.0220 | 0.0505 | 9 | 0.00 |
| stress | left_ankle | 0.1483 | 0.0973 | 0.0197 | 0.0174 | 10 | 0.00 |
| stress | right_hip_pitch | 0.0788 | 0.0475 | 0.0088 | 0.0192 | 9 | 0.00 |
| stress | right_knee | 0.1127 | 0.0687 | 0.0130 | 0.0493 | 9 | 0.00 |
| stress | right_ankle | 0.0724 | 0.0419 | 0.0084 | 0.0097 | 10 | 0.00 |

## Interpretation

- Candidate sim gate passed for this offline eval horizon. This does not approve robot testing; it only means the candidate cleared the configured sim-side tracking, saturation, posture, and reward checks.
- No robot motion, deployment, runtime behavior change, or training was performed.
