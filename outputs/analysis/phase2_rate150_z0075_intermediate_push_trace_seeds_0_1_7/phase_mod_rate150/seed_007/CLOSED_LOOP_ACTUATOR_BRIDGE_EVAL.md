# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit_corrected_knee.json`
task: `rough_terrain_backlash`
command_x: `0.08`
command_y: `0.0`
command_yaw: `0.0`
duration_s: `15.0`
seed: `7`
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
push_config: `{'enable': True, 'interval_range_s': [1.0, 1.5], 'magnitude_range': [0.075, 0.125], 'recovery_window_s': 0.5, 'recovery_max_abs_pitch_rad': 0.8, 'recovery_min_base_height_m': 0.08}`
terrain_override: `{'enabled': True, 'hfield_z_scale': 0.0075, 'source_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml', 'temp_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/.codex_eval_zdguifa0_hfield_z0.0075.xml'}`
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
| `max_pitch_tracking_p95_rad` | 0.1872 | 0.2000 |
| `max_sent_target_velocity_p95_rad_s` | 1.5628 | NA |
| `max_sent_target_velocity_limit_excess_rad_s` | 0.0000 | 0.0000 |
| `max_sent_target_velocity_max_limit_excess_rad_s` | 0.4477 | 0.0000 |
| `max_abs_body_pitch_p95_rad` | 0.3386 | 0.2500 |
| `min_base_height_m` | 0.0201 | 0.1200 |
| `min_reward_mean` | 0.4585 | 0.3000 |
| `min_forward_command_tracking_ratio` | 0.7245 | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.0220 | NA |
| `max_forward_shortfall_cost_mean` | 0.2114 | NA |

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
| `right_hip_pitch` | 2.6977 | 2.2500 | 0.4477 |
| `right_ankle` | 2.0396 | 2.0000 | 0.0396 |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| fitted | 550 | fall_or_nan | 0.3386 | 0.0201 | 0.0580 | 0.7245 | 0.4585 |

### Foot Clearance / Support

| mode | foot | contact_pct | swing_peak_lift | swing_lift_p95 | single_support_pct | double_support_pct | support_transitions |
|---|---|---:|---:|---:|---:|---:|---:|
| fitted | `left` | 90.7273 | 0.0630 | 0.0447 | 23.4545 | 76.3636 | 89 |
| fitted | `right` | 85.4545 | 0.0601 | 0.0182 | 23.4545 | 76.3636 | 89 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| fitted | `cost/action_rate` | 0.0224 | 0.0379 | 0.5087 |
| fitted | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `cost/torques` | 0.0056 | 0.0089 | 0.0116 |
| fitted | `diagnostic/actuator_bridge_delay_ticks` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/actuator_bridge_tau_mean_s` | 0.0200 | 0.0200 | 0.0200 |
| fitted | `diagnostic/actuator_bridge_tracking_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/actuator_bridge_velocity_limit_mean_rad_s` | 5.2400 | 5.2400 | 5.2400 |
| fitted | `diagnostic/behavior_prior_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/command_progress_failure` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/command_progress_ratio` | 0.4070 | 0.7630 | 0.9494 |
| fitted | `diagnostic/command_progress_shortfall_cost` | 0.0479 | 0.0770 | 0.0850 |
| fitted | `diagnostic/forward_double_support_steps` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/forward_phase_single_support_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/forward_phase_swing_lift_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/forward_swing_imbalance` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/forward_swing_phase_advance_ticks` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/push_recovery_actuator_tracking_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/push_recovery_steps` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/soft_prior_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/soft_prior_phase` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/swing_peak_forward_advance` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/swing_peak_lift` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/target_velocity_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| fitted | `reward/imitation` | 0.6616 | 3.4554 | 4.3919 |
| fitted | `reward/tracking_ang_vel` | 0.6147 | 5.0744 | 5.9999 |
| fitted | `reward/tracking_lin_vel` | 1.6770 | 2.4954 | 2.5000 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| fitted | `PASS_DIAGNOSTIC` | 0.5000 | 0.7245 | 1.7765 | 0.2581 | 0.2114 |

### Push Recovery

| mode | events | recovered | success_rate | push_mag_mean | push_mag_max |
|---|---:|---:|---:|---:|---:|
| fitted | 7 | 7 | 1.0000 | 0.1025 | 0.1146 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| fitted | left_hip_pitch | 1.3848 | 1.3026 | 0.0872 | 0.1390 | 4 | 0.00 |
| fitted | left_knee | 1.5628 | 1.4790 | 0.1040 | 0.1872 | 4 | 0.00 |
| fitted | left_ankle | 1.4024 | 1.3192 | 0.0905 | 0.1493 | 4 | 0.00 |
| fitted | right_hip_pitch | 1.3805 | 1.2870 | 0.0864 | 0.1237 | 4 | 0.00 |
| fitted | right_knee | 1.5544 | 1.4726 | 0.1031 | 0.1691 | 4 | 0.00 |
| fitted | right_ankle | 1.4173 | 1.3309 | 0.0909 | 0.1548 | 4 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
