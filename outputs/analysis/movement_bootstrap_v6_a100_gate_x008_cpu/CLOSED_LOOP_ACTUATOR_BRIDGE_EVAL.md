# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/colab_cli/open-duck-a100-v6-staged-curriculum-20260623T194912Z/extracted/open_duck_colab_cli_staged-curriculum_20260623T194923Z/open_duck_staged_curriculum_cli/03_phase3_hold_motion_fitted_bridge/smoke_20260623T200752Z_gpu/2026_06_23_201609_307200.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.08`
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

status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
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

status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`

| metric | value | threshold |
|---|---:|---:|
| `max_action_saturation_pct` | 0.0000 | 1.0000 |
| `max_pitch_tracking_p95_rad` | 0.0679 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 0.1765 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 0.0946 | 0.2500 |
| `min_base_height_m` | 0.1537 | 0.1200 |
| `min_reward_mean` | 0.5444 | 0.3000 |
| `min_forward_command_tracking_ratio` | 0.0084 | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.0793 | NA |
| `max_forward_shortfall_cost_mean` | 0.2523 | NA |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| vanilla | 750 | duration_complete | 0.0946 | 0.1537 | 0.0009 | 0.0114 | 0.5444 |
| fitted | 750 | duration_complete | 0.0921 | 0.1537 | 0.0009 | 0.0118 | 0.5481 |
| stress | 750 | duration_complete | 0.0898 | 0.1537 | 0.0007 | 0.0084 | 0.5480 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| vanilla | `cost/action_rate` | 0.0016 | 0.0006 | 0.3698 |
| vanilla | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| vanilla | `cost/torques` | 0.0017 | 0.0019 | 0.0402 |
| vanilla | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| vanilla | `reward/imitation` | 0.2811 | 2.3065 | 2.9572 |
| vanilla | `reward/tracking_ang_vel` | 5.6104 | 5.9883 | 6.0000 |
| vanilla | `reward/tracking_lin_vel` | 1.3316 | 1.4440 | 2.4577 |
| fitted | `cost/action_rate` | 0.0015 | 0.0005 | 0.3698 |
| fitted | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `cost/torques` | 0.0016 | 0.0020 | 0.0441 |
| fitted | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| fitted | `reward/imitation` | 0.3013 | 2.3469 | 2.9477 |
| fitted | `reward/tracking_ang_vel` | 5.7715 | 5.9906 | 6.0000 |
| fitted | `reward/tracking_lin_vel` | 1.3356 | 1.3869 | 2.4556 |
| stress | `cost/action_rate` | 0.0016 | 0.0005 | 0.3698 |
| stress | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| stress | `cost/torques` | 0.0016 | 0.0018 | 0.0441 |
| stress | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| stress | `reward/imitation` | 0.3164 | 2.3220 | 2.8567 |
| stress | `reward/tracking_ang_vel` | 5.7558 | 5.9995 | 6.0000 |
| stress | `reward/tracking_lin_vel` | 1.3307 | 1.4040 | 2.4427 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| vanilla | `PASS_DIAGNOSTIC` | 0.5000 | 0.0114 | 0.0744 | 0.4919 | 0.2499 |
| fitted | `PASS_DIAGNOSTIC` | 0.5000 | 0.0118 | 0.0406 | 0.4900 | 0.2464 |
| stress | `PASS_DIAGNOSTIC` | 0.5000 | 0.0084 | 0.0505 | 0.4942 | 0.2523 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 0.1027 | 0.1027 | 0.0000 | 0.0121 | 0 | 0.00 |
| vanilla | left_knee | 0.1765 | 0.1765 | 0.0000 | 0.0431 | 0 | 0.00 |
| vanilla | left_ankle | 0.1113 | 0.1113 | 0.0000 | 0.0151 | 0 | 0.00 |
| vanilla | right_hip_pitch | 0.0992 | 0.0992 | 0.0000 | 0.0350 | 0 | 0.00 |
| vanilla | right_knee | 0.0859 | 0.0859 | 0.0000 | 0.0659 | 0 | 0.00 |
| vanilla | right_ankle | 0.0563 | 0.0563 | 0.0000 | 0.0284 | 0 | 0.00 |
| fitted | left_hip_pitch | 0.0977 | 0.0969 | 0.0066 | 0.0140 | 3 | 0.00 |
| fitted | left_knee | 0.1612 | 0.1548 | 0.0109 | 0.0475 | 4 | 0.00 |
| fitted | left_ankle | 0.1135 | 0.1096 | 0.0077 | 0.0171 | 3 | 0.00 |
| fitted | right_hip_pitch | 0.0941 | 0.0909 | 0.0064 | 0.0375 | 3 | 0.00 |
| fitted | right_knee | 0.0920 | 0.0887 | 0.0061 | 0.0679 | 3 | 0.00 |
| fitted | right_ankle | 0.0504 | 0.0462 | 0.0031 | 0.0278 | 3 | 0.00 |
| stress | left_hip_pitch | 0.0909 | 0.0544 | 0.0101 | 0.0099 | 9 | 0.00 |
| stress | left_knee | 0.1675 | 0.1038 | 0.0199 | 0.0433 | 9 | 0.00 |
| stress | left_ankle | 0.1072 | 0.0665 | 0.0132 | 0.0163 | 11 | 0.00 |
| stress | right_hip_pitch | 0.0966 | 0.0600 | 0.0116 | 0.0371 | 9 | 0.00 |
| stress | right_knee | 0.0869 | 0.0571 | 0.0107 | 0.0674 | 9 | 0.00 |
| stress | right_ankle | 0.0467 | 0.0238 | 0.0048 | 0.0275 | 11 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
