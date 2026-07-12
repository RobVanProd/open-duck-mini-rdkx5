# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_rate165_phase_local_compact_student/candidate.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit_corrected_knee.json`
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

status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
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
terrain_override: `{'enabled': True, 'hfield_z_scale': 0.0026, 'source_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml', 'temp_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/.codex_eval_f7yzk1rw_hfield_z0.0026.xml'}`
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
| `max_action_saturation_pct` | 87.5000 | 1.0000 |
| `max_pitch_tracking_p95_rad` | 0.1830 | 0.2000 |
| `max_sent_target_velocity_p95_rad_s` | 1.9439 | NA |
| `max_sent_target_velocity_limit_excess_rad_s` | 0.0000 | 0.0000 |
| `max_sent_target_velocity_max_limit_excess_rad_s` | 2.8131 | 0.0000 |
| `max_abs_body_pitch_p95_rad` | 0.0193 | 0.2500 |
| `min_base_height_m` | 0.0830 | 0.1200 |
| `min_reward_mean` | 0.3939 | 0.3000 |
| `min_forward_command_tracking_ratio` | -2.7630 | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.3010 | NA |
| `max_forward_shortfall_cost_mean` | 28.8559 | NA |

Corrected per-joint velocity limits:

| joint | limit_rad_s |
|---|---:|
| `left_hip_pitch` | 2.5000 |
| `left_knee` | 3.2500 |
| `left_ankle` | 2.7500 |
| `right_hip_pitch` | 2.2500 |
| `right_knee` | 2.7500 |
| `right_ankle` | 2.0000 |

Per-joint max target-velocity violations:

| joint | max_rad_s | limit_rad_s | excess_rad_s |
|---|---:|---:|---:|
| `left_hip_pitch` | 3.4841 | 2.5000 | 0.9841 |
| `left_knee` | 5.2400 | 3.2500 | 1.9900 |
| `left_ankle` | 3.2906 | 2.7500 | 0.5406 |
| `right_hip_pitch` | 2.7419 | 2.2500 | 0.4919 |
| `right_ankle` | 4.8131 | 2.0000 | 2.8131 |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| fitted | 72 | fall_or_nan | 0.0193 | 0.0830 | -0.2210 | -2.7630 | 0.3939 |

### Foot Clearance / Support

| mode | foot | contact_pct | swing_peak_lift | swing_lift_p95 | single_support_pct | double_support_pct | support_transitions |
|---|---|---:|---:|---:|---:|---:|---:|
| fitted | `left` | 87.5000 | 0.0381 | 0.0373 | 11.1111 | 86.1111 | 11 |
| fitted | `right` | 95.8333 | 0.0321 | 0.0317 | 11.1111 | 86.1111 | 11 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| fitted | `cost/action_rate` | 0.0662 | 0.2175 | 1.0619 |
| fitted | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `cost/torques` | 0.0063 | 0.0147 | 0.0179 |
| fitted | `diagnostic/actuator_bridge_delay_ticks` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/actuator_bridge_tau_mean_s` | 0.0200 | 0.0200 | 0.0200 |
| fitted | `diagnostic/actuator_bridge_tracking_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/actuator_bridge_velocity_limit_mean_rad_s` | 5.2400 | 5.2400 | 5.2400 |
| fitted | `diagnostic/behavior_prior_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/command_progress_failure` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/command_progress_ratio` | -0.4630 | 0.5069 | 0.6221 |
| fitted | `diagnostic/command_progress_shortfall_cost` | 1.3417 | 7.1394 | 11.3097 |
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
| fitted | `reward/imitation` | -2.3517 | 1.9500 | 2.5694 |
| fitted | `reward/tracking_ang_vel` | 1.7436 | 5.7881 | 5.9780 |
| fitted | `reward/tracking_lin_vel` | 0.3743 | 2.2651 | 2.4824 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| fitted | `PASS_DIAGNOSTIC` | 0.5000 | -2.7630 | 0.8612 | 3.3065 | 28.8559 |

### Push Recovery

| mode | events | recovered | success_rate | push_mag_mean | push_mag_max |
|---|---:|---:|---:|---:|---:|
| fitted | 0 | 0 | NA | NA | NA |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| fitted | left_hip_pitch | 1.2091 | 1.5917 | 0.1028 | 0.1517 | 4 | 83.33 |
| fitted | left_knee | 1.9439 | 1.7124 | 0.0893 | 0.1830 | 4 | 4.17 |
| fitted | left_ankle | 0.8639 | 1.1408 | 0.0870 | 0.1137 | 4 | 87.50 |
| fitted | right_hip_pitch | 1.2803 | 1.3014 | 0.0778 | 0.1270 | 4 | 86.11 |
| fitted | right_knee | 1.1604 | 1.0230 | 0.0516 | 0.0569 | 3 | 33.33 |
| fitted | right_ankle | 0.4443 | 1.9534 | 0.1056 | 0.1368 | 4 | 87.50 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
