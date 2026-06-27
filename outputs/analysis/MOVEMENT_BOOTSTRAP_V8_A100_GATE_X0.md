# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_TRACKING`
policy: `/content/open_duck_staged_curriculum_cli/02_phase2_v7_lunge_damping_consolidate/smoke_20260623T225217Z_gpu/2026_06_23_225832_122880.onnx`
fit_json: `/content/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.0`
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

status: `HOLD_CANDIDATE_TRACKING`
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

status: `HOLD_CANDIDATE_TRACKING`

| metric | value | threshold |
|---|---:|---:|
| `max_action_saturation_pct` | 0.0000 | 1.0000 |
| `max_pitch_tracking_p95_rad` | 0.0863 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 0.2186 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 0.0539 | 0.2500 |
| `min_base_height_m` | 0.1537 | 0.1200 |
| `min_reward_mean` | 0.5440 | 0.3000 |
| `min_forward_command_tracking_ratio` | NA | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.0006 | NA |
| `max_forward_shortfall_cost_mean` | NA | NA |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| vanilla | 750 | duration_complete | 0.0539 | 0.1559 | 0.0002 | NA | 0.5440 |
| fitted | 750 | duration_complete | 0.0505 | 0.1537 | 0.0003 | NA | 0.5515 |
| stress | 750 | duration_complete | 0.0537 | 0.1537 | 0.0006 | NA | 0.5579 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| vanilla | `cost/action_rate` | 0.0024 | 0.0007 | 0.5646 |
| vanilla | `cost/stand_still` | 0.3386 | 0.3939 | 4.9563 |
| vanilla | `cost/torques` | 0.0017 | 0.0018 | 0.0484 |
| vanilla | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| vanilla | `reward/imitation` | 0.0000 | 0.0000 | 0.0000 |
| vanilla | `reward/tracking_ang_vel` | 5.0624 | 5.9957 | 6.0000 |
| vanilla | `reward/tracking_lin_vel` | 2.4823 | 2.4997 | 2.5000 |
| fitted | `cost/action_rate` | 0.0025 | 0.0007 | 0.5646 |
| fitted | `cost/stand_still` | 0.3362 | 0.3465 | 5.0986 |
| fitted | `cost/torques` | 0.0018 | 0.0018 | 0.0471 |
| fitted | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| fitted | `reward/imitation` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `reward/tracking_ang_vel` | 5.4480 | 5.9946 | 6.0000 |
| fitted | `reward/tracking_lin_vel` | 2.4653 | 2.5000 | 2.5000 |
| stress | `cost/action_rate` | 0.0024 | 0.0008 | 0.5646 |
| stress | `cost/stand_still` | 0.2889 | 0.2983 | 5.0986 |
| stress | `cost/torques` | 0.0017 | 0.0018 | 0.0471 |
| stress | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| stress | `reward/imitation` | 0.0000 | 0.0000 | 0.0000 |
| stress | `reward/tracking_ang_vel` | 5.7326 | 5.9989 | 6.0000 |
| stress | `reward/tracking_lin_vel` | 2.4549 | 2.4998 | 2.5000 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| vanilla | `NO_FORWARD_COMMAND` | 0.5000 | NA | NA | NA | NA |
| fitted | `NO_FORWARD_COMMAND` | 0.5000 | NA | NA | NA | NA |
| stress | `NO_FORWARD_COMMAND` | 0.5000 | NA | NA | NA | NA |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 0.1359 | 0.1359 | 0.0000 | 0.0154 | 0 | 0.00 |
| vanilla | left_knee | 0.1707 | 0.1707 | 0.0000 | 0.0371 | 0 | 0.00 |
| vanilla | left_ankle | 0.1867 | 0.1867 | 0.0000 | 0.0285 | 0 | 0.00 |
| vanilla | right_hip_pitch | 0.1859 | 0.1859 | 0.0000 | 0.0446 | 0 | 0.00 |
| vanilla | right_knee | 0.1793 | 0.1793 | 0.0000 | 0.0695 | 0 | 0.00 |
| vanilla | right_ankle | 0.1458 | 0.1458 | 0.0000 | 0.0414 | 0 | 0.00 |
| fitted | left_hip_pitch | 0.1323 | 0.1274 | 0.0088 | 0.0183 | 3 | 0.00 |
| fitted | left_knee | 0.1494 | 0.1454 | 0.0102 | 0.0451 | 3 | 0.00 |
| fitted | left_ankle | 0.2109 | 0.2014 | 0.0136 | 0.0360 | 3 | 0.00 |
| fitted | right_hip_pitch | 0.1770 | 0.1738 | 0.0122 | 0.0499 | 3 | 0.00 |
| fitted | right_knee | 0.1825 | 0.1772 | 0.0122 | 0.0806 | 3 | 0.00 |
| fitted | right_ankle | 0.1485 | 0.1454 | 0.0103 | 0.0470 | 4 | 0.00 |
| stress | left_hip_pitch | 0.1643 | 0.1012 | 0.0191 | 0.0194 | 9 | 0.00 |
| stress | left_knee | 0.1928 | 0.1261 | 0.0244 | 0.0491 | 9 | 0.00 |
| stress | left_ankle | 0.2186 | 0.1345 | 0.0276 | 0.0379 | 10 | 0.00 |
| stress | right_hip_pitch | 0.2087 | 0.1277 | 0.0243 | 0.0489 | 9 | 0.00 |
| stress | right_knee | 0.2120 | 0.1328 | 0.0252 | 0.0863 | 9 | 0.00 |
| stress | right_ankle | 0.1480 | 0.0981 | 0.0198 | 0.0437 | 10 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
