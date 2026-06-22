# Sim Actuator Bridge Eval

overall_status: `PASS_CANDIDATE_SIM_GATE`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/open_duck_mini_actuator_bridge_cpu_pilot_20260622_step8240/candidate.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.04`
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
| `max_pitch_tracking_p95_rad` | 0.0525 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 0.1840 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 0.0190 | 0.2500 |
| `min_base_height_m` | 0.1536 | 0.1200 |
| `min_reward_mean` | 0.5565 | 0.3000 |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | reward_mean |
|---|---:|---|---:|---:|---:|
| vanilla | 750 | duration_complete | 0.0190 | 0.1538 | 0.5565 |
| fitted | 750 | duration_complete | 0.0190 | 0.1536 | 0.5593 |
| stress | 750 | duration_complete | 0.0147 | 0.1536 | 0.5638 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 0.1428 | 0.1428 | 0.0000 | 0.0164 | 0 | 0.00 |
| vanilla | left_knee | 0.1830 | 0.1830 | 0.0000 | 0.0481 | 0 | 0.00 |
| vanilla | left_ankle | 0.1349 | 0.1349 | 0.0000 | 0.0202 | 0 | 0.00 |
| vanilla | right_hip_pitch | 0.0739 | 0.0739 | 0.0000 | 0.0212 | 0 | 0.00 |
| vanilla | right_knee | 0.1141 | 0.1141 | 0.0000 | 0.0522 | 0 | 0.00 |
| vanilla | right_ankle | 0.0644 | 0.0644 | 0.0000 | 0.0119 | 0 | 0.00 |
| fitted | left_hip_pitch | 0.1576 | 0.1475 | 0.0103 | 0.0176 | 3 | 0.00 |
| fitted | left_knee | 0.1840 | 0.1798 | 0.0127 | 0.0525 | 3 | 0.00 |
| fitted | left_ankle | 0.1333 | 0.1300 | 0.0091 | 0.0216 | 4 | 0.00 |
| fitted | right_hip_pitch | 0.0759 | 0.0680 | 0.0048 | 0.0235 | 3 | 0.00 |
| fitted | right_knee | 0.1147 | 0.1087 | 0.0074 | 0.0518 | 3 | 0.00 |
| fitted | right_ankle | 0.0666 | 0.0637 | 0.0045 | 0.0103 | 3 | 0.00 |
| stress | left_hip_pitch | 0.1503 | 0.0994 | 0.0187 | 0.0162 | 9 | 0.00 |
| stress | left_knee | 0.1833 | 0.1205 | 0.0231 | 0.0511 | 9 | 0.00 |
| stress | left_ankle | 0.1422 | 0.0925 | 0.0189 | 0.0178 | 10 | 0.00 |
| stress | right_hip_pitch | 0.0839 | 0.0494 | 0.0093 | 0.0212 | 9 | 0.00 |
| stress | right_knee | 0.1211 | 0.0742 | 0.0141 | 0.0518 | 9 | 0.00 |
| stress | right_ankle | 0.0671 | 0.0380 | 0.0077 | 0.0111 | 10 | 0.00 |

## Interpretation

- Candidate sim gate passed for this offline eval horizon. This does not approve robot testing; it only means the candidate cleared the configured sim-side tracking, saturation, posture, and reward checks.
- No robot motion, deployment, runtime behavior change, or training was performed.
