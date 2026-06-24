# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_TRACKING`
policy: `/content/open_duck_staged_curriculum_cli/03_phase3_consolidate_progress_no_lunge/smoke_20260623T234521Z_gpu/2026_06_23_235119_122880.onnx`
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
| `max_pitch_tracking_p95_rad` | 0.0932 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 0.2534 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 0.0493 | 0.2500 |
| `min_base_height_m` | 0.1537 | 0.1200 |
| `min_reward_mean` | 0.5359 | 0.3000 |
| `min_forward_command_tracking_ratio` | NA | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.0003 | NA |
| `max_forward_shortfall_cost_mean` | NA | NA |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| vanilla | 750 | duration_complete | 0.0493 | 0.1574 | -0.0002 | NA | 0.5359 |
| fitted | 750 | duration_complete | 0.0469 | 0.1537 | 0.0003 | NA | 0.5495 |
| stress | 750 | duration_complete | 0.0467 | 0.1537 | 0.0003 | NA | 0.5515 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| vanilla | `cost/action_rate` | 0.0028 | 0.0008 | 0.6362 |
| vanilla | `cost/stand_still` | 0.3728 | 0.4256 | 5.0264 |
| vanilla | `cost/torques` | 0.0019 | 0.0020 | 0.0492 |
| vanilla | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| vanilla | `reward/imitation` | 0.0000 | 0.0000 | 0.0000 |
| vanilla | `reward/tracking_ang_vel` | 4.6923 | 5.9949 | 6.0000 |
| vanilla | `reward/tracking_lin_vel` | 2.4794 | 2.4998 | 2.5000 |
| fitted | `cost/action_rate` | 0.0029 | 0.0008 | 0.6362 |
| fitted | `cost/stand_still` | 0.3687 | 0.3853 | 5.1999 |
| fitted | `cost/torques` | 0.0019 | 0.0020 | 0.0474 |
| fitted | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| fitted | `reward/imitation` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `reward/tracking_ang_vel` | 5.3824 | 5.9986 | 6.0000 |
| fitted | `reward/tracking_lin_vel` | 2.4656 | 2.5000 | 2.5000 |
| stress | `cost/action_rate` | 0.0028 | 0.0009 | 0.6362 |
| stress | `cost/stand_still` | 0.3130 | 0.3348 | 5.1999 |
| stress | `cost/torques` | 0.0019 | 0.0020 | 0.0474 |
| stress | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| stress | `reward/imitation` | 0.0000 | 0.0000 | 0.0000 |
| stress | `reward/tracking_ang_vel` | 5.4432 | 5.9991 | 6.0000 |
| stress | `reward/tracking_lin_vel` | 2.4472 | 2.4999 | 2.5000 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| vanilla | `NO_FORWARD_COMMAND` | 0.5000 | NA | NA | NA | NA |
| fitted | `NO_FORWARD_COMMAND` | 0.5000 | NA | NA | NA | NA |
| stress | `NO_FORWARD_COMMAND` | 0.5000 | NA | NA | NA | NA |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 0.1617 | 0.1617 | 0.0000 | 0.0208 | 0 | 0.00 |
| vanilla | left_knee | 0.1983 | 0.1983 | 0.0000 | 0.0332 | 0 | 0.00 |
| vanilla | left_ankle | 0.1920 | 0.1920 | 0.0000 | 0.0334 | 0 | 0.00 |
| vanilla | right_hip_pitch | 0.2044 | 0.2044 | 0.0000 | 0.0483 | 0 | 0.00 |
| vanilla | right_knee | 0.2087 | 0.2087 | 0.0000 | 0.0746 | 0 | 0.00 |
| vanilla | right_ankle | 0.1610 | 0.1610 | 0.0000 | 0.0443 | 0 | 0.00 |
| fitted | left_hip_pitch | 0.1600 | 0.1542 | 0.0108 | 0.0255 | 3 | 0.00 |
| fitted | left_knee | 0.1686 | 0.1633 | 0.0115 | 0.0421 | 3 | 0.00 |
| fitted | left_ankle | 0.2120 | 0.2012 | 0.0139 | 0.0417 | 3 | 0.00 |
| fitted | right_hip_pitch | 0.2020 | 0.1965 | 0.0137 | 0.0551 | 3 | 0.00 |
| fitted | right_knee | 0.2162 | 0.2079 | 0.0145 | 0.0876 | 3 | 0.00 |
| fitted | right_ankle | 0.1695 | 0.1639 | 0.0112 | 0.0504 | 4 | 0.00 |
| stress | left_hip_pitch | 0.1965 | 0.1223 | 0.0232 | 0.0269 | 9 | 0.00 |
| stress | left_knee | 0.2089 | 0.1400 | 0.0267 | 0.0476 | 9 | 0.00 |
| stress | left_ankle | 0.2315 | 0.1392 | 0.0285 | 0.0455 | 10 | 0.00 |
| stress | right_hip_pitch | 0.2285 | 0.1354 | 0.0262 | 0.0548 | 9 | 0.00 |
| stress | right_knee | 0.2534 | 0.1515 | 0.0284 | 0.0932 | 9 | 0.00 |
| stress | right_ankle | 0.1613 | 0.1069 | 0.0214 | 0.0478 | 10 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
