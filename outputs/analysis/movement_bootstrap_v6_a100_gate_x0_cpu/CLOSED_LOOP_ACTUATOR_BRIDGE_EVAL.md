# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/colab_cli/open-duck-a100-v6-staged-curriculum-20260623T194912Z/extracted/open_duck_colab_cli_staged-curriculum_20260623T194923Z/open_duck_staged_curriculum_cli/03_phase3_hold_motion_fitted_bridge/smoke_20260623T200752Z_gpu/2026_06_23_201609_307200.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.0`
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
| `max_pitch_tracking_p95_rad` | 0.2565 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 2.9157 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 1.2562 | 0.2500 |
| `min_base_height_m` | 0.0318 | 0.1200 |
| `min_reward_mean` | 0.3930 | 0.3000 |
| `min_forward_command_tracking_ratio` | NA | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.2358 | NA |
| `max_forward_shortfall_cost_mean` | NA | NA |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| vanilla | 61 | fall_or_nan | 1.2562 | 0.0413 | 0.2358 | NA | 0.3930 |
| fitted | 78 | fall_or_nan | 1.2246 | 0.0318 | 0.1935 | NA | 0.4190 |
| stress | 93 | fall_or_nan | 1.1212 | 0.0417 | 0.1524 | NA | 0.4265 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| vanilla | `cost/action_rate` | 0.0446 | 0.1358 | 1.2866 |
| vanilla | `cost/stand_still` | 1.1300 | 4.2508 | 5.2992 |
| vanilla | `cost/torques` | 0.0049 | 0.0197 | 0.0429 |
| vanilla | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| vanilla | `reward/imitation` | 0.0000 | 0.0000 | 0.0000 |
| vanilla | `reward/tracking_ang_vel` | 0.1424 | 0.9128 | 1.0522 |
| vanilla | `reward/tracking_lin_vel` | 0.6883 | 1.5962 | 2.4601 |
| fitted | `cost/action_rate` | 0.0419 | 0.1911 | 1.2866 |
| fitted | `cost/stand_still` | 1.0082 | 3.5034 | 5.2789 |
| fitted | `cost/torques` | 0.0044 | 0.0120 | 0.0476 |
| fitted | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| fitted | `reward/imitation` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `reward/tracking_ang_vel` | 0.9169 | 5.2026 | 5.9625 |
| fitted | `reward/tracking_lin_vel` | 1.0881 | 1.9995 | 2.3557 |
| stress | `cost/action_rate` | 0.0322 | 0.1109 | 1.2866 |
| stress | `cost/stand_still` | 0.9476 | 2.7839 | 5.2789 |
| stress | `cost/torques` | 0.0037 | 0.0064 | 0.0476 |
| stress | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| stress | `reward/imitation` | 0.0000 | 0.0000 | 0.0000 |
| stress | `reward/tracking_ang_vel` | 1.1599 | 5.7029 | 5.9977 |
| stress | `reward/tracking_lin_vel` | 1.1477 | 2.2326 | 2.4899 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| vanilla | `NO_FORWARD_COMMAND` | 0.5000 | NA | NA | NA | NA |
| fitted | `NO_FORWARD_COMMAND` | 0.5000 | NA | NA | NA | NA |
| stress | `NO_FORWARD_COMMAND` | 0.5000 | NA | NA | NA | NA |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 1.9298 | 1.9298 | 0.0000 | 0.0877 | 0 | 0.00 |
| vanilla | left_knee | 1.0694 | 1.0694 | 0.0000 | 0.0765 | 0 | 0.00 |
| vanilla | left_ankle | 1.8503 | 1.8503 | 0.0000 | 0.0886 | 0 | 0.00 |
| vanilla | right_hip_pitch | 1.1046 | 1.1046 | 0.0000 | 0.0793 | 0 | 0.00 |
| vanilla | right_knee | 2.1482 | 2.1482 | 0.0000 | 0.0739 | 0 | 0.00 |
| vanilla | right_ankle | 1.7730 | 1.7730 | 0.0000 | 0.2565 | 0 | 0.00 |
| fitted | left_hip_pitch | 1.5376 | 1.0027 | 0.0488 | 0.1002 | 3 | 0.00 |
| fitted | left_knee | 1.1870 | 1.4232 | 0.0910 | 0.0871 | 4 | 0.00 |
| fitted | left_ankle | 1.4893 | 1.2046 | 0.0572 | 0.0853 | 3 | 0.00 |
| fitted | right_hip_pitch | 1.3491 | 0.9709 | 0.0431 | 0.1086 | 3 | 0.00 |
| fitted | right_knee | 2.9157 | 1.3510 | 0.0686 | 0.0915 | 3 | 0.00 |
| fitted | right_ankle | 1.5940 | 1.3737 | 0.1084 | 0.2197 | 4 | 0.00 |
| stress | left_hip_pitch | 1.6857 | 0.2706 | 0.0432 | 0.1055 | 8 | 0.00 |
| stress | left_knee | 0.9738 | 0.4865 | 0.1088 | 0.1191 | 9 | 0.00 |
| stress | left_ankle | 1.2312 | 0.4670 | 0.1051 | 0.1250 | 11 | 0.00 |
| stress | right_hip_pitch | 0.8258 | 0.3849 | 0.0841 | 0.1007 | 9 | 0.00 |
| stress | right_knee | 2.6251 | 0.3644 | 0.0593 | 0.1313 | 8 | 0.00 |
| stress | right_ankle | 1.1585 | 0.8089 | 0.1724 | 0.1838 | 12 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
