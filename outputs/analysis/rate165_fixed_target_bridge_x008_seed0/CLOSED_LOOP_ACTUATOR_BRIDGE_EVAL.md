# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_TARGET_VELOCITY`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/candidate.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/fixed_target_p30_actuator_fit_20260712.json`
task: `rough_terrain_backlash`
command_x: `0.08`
command_y: `0.0`
command_yaw: `0.0`
duration_s: `15.0`
seed: `0`
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

status: `HOLD_CANDIDATE_TARGET_VELOCITY`
eval_role: `candidate`
policy_action_gain: `1.0`
policy_io: `{'obs_input_name': 'obs', 'action_output_name': 'continuous_actions', 'state_input_names': [], 'state_output_names': [], 'state_input_shapes': {}, 'stateful': False}`
env: `playground.open_duck_mini_v2.joystick.Joystick` / task `rough_terrain_backlash`
obs/action dims: `{'privileged_state': [212], 'state': [101]}` / `14`
actuator_names: `['left_hip_yaw', 'left_hip_roll', 'left_hip_pitch', 'left_knee', 'left_ankle', 'neck_pitch', 'head_pitch', 'head_yaw', 'head_roll', 'right_hip_yaw', 'right_hip_roll', 'right_hip_pitch', 'right_knee', 'right_ankle']`
ctrl_dt: `0.02`
sim_dt: `0.002`
mjx_step_loop_mode: `default`
max_motor_velocity: `5.24`
jax: `cpu` `['TFRT_CPU_0']`
insertion_point: `target_stage_direct`
double_rate_limit: `False`
push_config: `{'enable': False, 'interval_range_s': [5.0, 10.0], 'magnitude_range': [0.1, 1.0], 'recovery_window_s': 0.5, 'recovery_max_abs_pitch_rad': 0.8, 'recovery_min_base_height_m': 0.08}`
terrain_override: `{'enabled': True, 'hfield_z_scale': 0.0026, 'source_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml', 'temp_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/.codex_eval_yob72k78_hfield_z0.0026.xml'}`
worker_returncode: `0`

Worker output excerpt:

```text
Failed to import warp: No module named 'warp'
Failed to import mujoco_warp: No module named 'warp'
```

### Candidate Gate

status: `HOLD_CANDIDATE_TARGET_VELOCITY`

| metric | value | threshold |
|---|---:|---:|
| `max_action_saturation_pct` | 0.0000 | 1.0000 |
| `max_pitch_tracking_p95_rad` | 0.1986 | 0.2000 |
| `max_sent_target_velocity_p95_rad_s` | 1.7132 | NA |
| `max_sent_target_velocity_limit_excess_rad_s` | 0.6904 | 0.0000 |
| `max_sent_target_velocity_max_limit_excess_rad_s` | 0.9934 | 0.0000 |
| `max_abs_body_pitch_p95_rad` | 0.1380 | 0.2500 |
| `min_base_height_m` | 0.1523 | 0.1200 |
| `min_reward_mean` | 0.4574 | 0.3000 |
| `min_forward_command_tracking_ratio` | 0.3213 | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.0543 | NA |
| `max_forward_shortfall_cost_mean` | 0.1653 | NA |

Corrected per-joint velocity limits:

| joint | limit_rad_s |
|---|---:|
| `left_hip_pitch` | 1.5000 |
| `left_knee` | 1.5000 |
| `left_ankle` | 1.7500 |
| `right_hip_pitch` | 1.2500 |
| `right_knee` | 1.0000 |
| `right_ankle` | 1.2500 |

Per-joint p95 target-velocity violations:

| joint | p95_rad_s | limit_rad_s | excess_rad_s |
|---|---:|---:|---:|
| `left_knee` | 1.7132 | 1.5000 | 0.2132 |
| `right_hip_pitch` | 1.4877 | 1.2500 | 0.2377 |
| `right_knee` | 1.6904 | 1.0000 | 0.6904 |
| `right_ankle` | 1.5022 | 1.2500 | 0.2522 |

Per-joint max target-velocity violations:

| joint | max_rad_s | limit_rad_s | excess_rad_s |
|---|---:|---:|---:|
| `left_hip_pitch` | 1.8188 | 1.5000 | 0.3188 |
| `left_knee` | 2.0989 | 1.5000 | 0.5989 |
| `right_hip_pitch` | 1.8777 | 1.2500 | 0.6277 |
| `right_knee` | 1.9934 | 1.0000 | 0.9934 |
| `right_ankle` | 1.9465 | 1.2500 | 0.6965 |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| fitted | 750 | duration_complete | 0.1380 | 0.1523 | 0.0257 | 0.3213 | 0.4574 |

### Foot Clearance / Support

| mode | foot | contact_pct | swing_peak_lift | swing_lift_p95 | single_support_pct | double_support_pct | support_transitions |
|---|---|---:|---:|---:|---:|---:|---:|
| fitted | `left` | 88.2667 | 0.0157 | 0.0134 | 20.0000 | 80.0000 | 118 |
| fitted | `right` | 91.7333 | 0.0150 | 0.0132 | 20.0000 | 80.0000 | 118 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| fitted | `cost/action_rate` | 0.0227 | 0.0404 | 0.5067 |
| fitted | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `cost/torques` | 0.0055 | 0.0090 | 0.0108 |
| fitted | `diagnostic/actuator_bridge_delay_ticks` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/actuator_bridge_tau_mean_s` | 0.0200 | 0.0200 | 0.0200 |
| fitted | `diagnostic/actuator_bridge_tracking_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/actuator_bridge_velocity_limit_mean_rad_s` | 5.2400 | 5.2400 | 5.2400 |
| fitted | `diagnostic/behavior_prior_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/command_progress_failure` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/command_progress_ratio` | 0.3189 | 0.4861 | 0.6577 |
| fitted | `diagnostic/command_progress_shortfall_cost` | 0.0801 | 0.1082 | 0.1218 |
| fitted | `diagnostic/forward_double_support_steps` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/forward_phase_single_support_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/forward_phase_swing_lift_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/forward_swing_imbalance` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/forward_swing_phase_advance_ticks` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/joint_target_tracking_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/push_recovery_actuator_tracking_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/push_recovery_steps` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/soft_prior_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/soft_prior_phase` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/swing_peak_forward_advance` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/swing_peak_lift` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/target_velocity_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| fitted | `reward/imitation` | 0.6430 | 3.3814 | 4.2073 |
| fitted | `reward/tracking_ang_vel` | 0.5281 | 5.0044 | 5.9996 |
| fitted | `reward/tracking_lin_vel` | 1.7268 | 2.4918 | 2.5000 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| fitted | `PASS_DIAGNOSTIC` | 0.5000 | 0.3213 | 1.0252 | 0.2783 | 0.1653 |

### Push Recovery

| mode | events | recovered | success_rate | push_mag_mean | push_mag_max |
|---|---:|---:|---:|---:|---:|
| fitted | 0 | 0 | NA | NA | NA |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| fitted | left_hip_pitch | 1.3848 | 1.4467 | 0.0777 | 0.1307 | 3 | 0.00 |
| fitted | left_knee | 1.7132 | 1.5000 | 0.1003 | 0.1986 | 3 | 0.00 |
| fitted | left_ankle | 1.3252 | 1.3163 | 0.0798 | 0.1405 | 3 | 0.00 |
| fitted | right_hip_pitch | 1.4877 | 1.2500 | 0.0865 | 0.1270 | 3 | 0.00 |
| fitted | right_knee | 1.6904 | 1.0000 | 0.1108 | 0.1658 | 3 | 0.00 |
| fitted | right_ankle | 1.5022 | 1.2500 | 0.0899 | 0.1488 | 3 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
