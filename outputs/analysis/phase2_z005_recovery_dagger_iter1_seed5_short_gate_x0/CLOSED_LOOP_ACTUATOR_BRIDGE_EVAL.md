# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short_student/candidate.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit_corrected_knee.json`
task: `rough_terrain_backlash`
command_x: `0.0`
command_y: `0.0`
command_yaw: `0.0`
duration_s: `2.0`
seed: `5`
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
terrain_override: `{'enabled': True, 'hfield_z_scale': 0.005, 'source_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml', 'temp_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/.codex_eval_d3bxvxou_hfield_z0.005.xml'}`
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
| `max_pitch_tracking_p95_rad` | 0.2425 | 0.2000 |
| `max_sent_target_velocity_p95_rad_s` | 0.6171 | NA |
| `max_sent_target_velocity_limit_excess_rad_s` | 0.0000 | 0.0000 |
| `max_sent_target_velocity_max_limit_excess_rad_s` | 0.0000 | 0.0000 |
| `max_abs_body_pitch_p95_rad` | 0.0517 | 0.2500 |
| `min_base_height_m` | 0.0450 | 0.1200 |
| `min_reward_mean` | 0.4264 | 0.3000 |
| `min_forward_command_tracking_ratio` | NA | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.3861 | NA |
| `max_forward_shortfall_cost_mean` | NA | NA |

Corrected per-joint velocity limits:

| joint | limit_rad_s |
|---|---:|
| `left_hip_pitch` | 2.5000 |
| `left_knee` | 3.2500 |
| `left_ankle` | 2.7500 |
| `right_hip_pitch` | 2.2500 |
| `right_knee` | 2.7500 |
| `right_ankle` | 2.0000 |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| fitted | 41 | fall_or_nan | -0.0517 | 0.0450 | -0.3861 | NA | 0.4264 |

### Foot Clearance / Support

| mode | foot | contact_pct | swing_peak_lift | swing_lift_p95 | single_support_pct | double_support_pct | support_transitions |
|---|---|---:|---:|---:|---:|---:|---:|
| fitted | `left` | 90.2439 | 0.0291 | 0.0277 | 9.7561 | 82.9268 | 9 |
| fitted | `right` | 85.3659 | 0.0413 | 0.0384 | 9.7561 | 82.9268 | 9 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| fitted | `cost/action_rate` | 0.0016 | 0.0046 | 0.0207 |
| fitted | `cost/stand_still` | 0.9417 | 4.7183 | 5.6256 |
| fitted | `cost/torques` | 0.0050 | 0.0356 | 0.0542 |
| fitted | `diagnostic/actuator_bridge_delay_ticks` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/actuator_bridge_tau_mean_s` | 0.0200 | 0.0200 | 0.0200 |
| fitted | `diagnostic/actuator_bridge_tracking_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/actuator_bridge_velocity_limit_mean_rad_s` | 5.2400 | 5.2400 | 5.2400 |
| fitted | `diagnostic/behavior_prior_cost` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/command_progress_failure` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/command_progress_ratio` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `diagnostic/command_progress_shortfall_cost` | 0.0000 | 0.0000 | 0.0000 |
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
| fitted | `reward/imitation` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `reward/tracking_ang_vel` | 1.9189 | 5.8267 | 5.9115 |
| fitted | `reward/tracking_lin_vel` | 0.3517 | 2.1511 | 2.4320 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| fitted | `NO_FORWARD_COMMAND` | 0.5000 | NA | NA | NA | NA |

### Push Recovery

| mode | events | recovered | success_rate | push_mag_mean | push_mag_max |
|---|---:|---:|---:|---:|---:|
| fitted | 0 | 0 | NA | NA | NA |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| fitted | left_hip_pitch | 0.6171 | 0.4717 | 0.0269 | 0.0343 | 3 | 0.00 |
| fitted | left_knee | 0.4404 | 0.2903 | 0.0167 | 0.2020 | 3 | 0.00 |
| fitted | left_ankle | 0.1940 | 0.1771 | 0.0114 | 0.0912 | 3 | 0.00 |
| fitted | right_hip_pitch | 0.4040 | 0.2806 | 0.0208 | 0.1645 | 3 | 0.00 |
| fitted | right_knee | 0.2907 | 0.2890 | 0.0158 | 0.2425 | 3 | 0.00 |
| fitted | right_ankle | 0.3371 | 0.2234 | 0.0179 | 0.1267 | 3 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
