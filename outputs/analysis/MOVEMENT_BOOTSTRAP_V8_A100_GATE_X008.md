# Sim Actuator Bridge Eval

overall_status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
policy: `/content/open_duck_staged_curriculum_cli/02_phase2_v7_lunge_damping_consolidate/smoke_20260623T225217Z_gpu/2026_06_23_225832_122880.onnx`
fit_json: `/content/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.08`
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

status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`

| metric | value | threshold |
|---|---:|---:|
| `max_action_saturation_pct` | 0.0000 | 1.0000 |
| `max_pitch_tracking_p95_rad` | 0.0871 | 0.0800 |
| `max_sent_target_velocity_p95_rad_s` | 0.2760 | 2.5000 |
| `max_abs_body_pitch_p95_rad` | 0.2062 | 0.2500 |
| `min_base_height_m` | 0.1486 | 0.1200 |
| `min_reward_mean` | 0.5292 | 0.3000 |
| `min_forward_command_tracking_ratio` | 0.0190 | 0.2500 |
| `max_abs_forward_velocity_error_m_s` | 0.0785 | NA |
| `max_forward_shortfall_cost_mean` | 0.2768 | NA |

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| vanilla | 750 | duration_complete | 0.2008 | 0.1509 | 0.0017 | 0.0208 | 0.5292 |
| fitted | 750 | duration_complete | 0.1953 | 0.1510 | 0.0015 | 0.0190 | 0.5376 |
| stress | 750 | duration_complete | 0.2062 | 0.1486 | 0.0019 | 0.0239 | 0.5351 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| vanilla | `cost/action_rate` | 0.0030 | 0.0012 | 0.9454 |
| vanilla | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| vanilla | `cost/torques` | 0.0020 | 0.0021 | 0.0470 |
| vanilla | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| vanilla | `reward/imitation` | -0.2176 | 1.8275 | 2.4614 |
| vanilla | `reward/tracking_ang_vel` | 5.3460 | 5.9733 | 5.9999 |
| vanilla | `reward/tracking_lin_vel` | 1.3357 | 1.5954 | 2.4998 |
| fitted | `cost/action_rate` | 0.0035 | 0.0011 | 0.9454 |
| fitted | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `cost/torques` | 0.0020 | 0.0024 | 0.0494 |
| fitted | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| fitted | `reward/imitation` | -0.2043 | 1.8347 | 2.5541 |
| fitted | `reward/tracking_ang_vel` | 5.7603 | 5.9996 | 6.0000 |
| fitted | `reward/tracking_lin_vel` | 1.3301 | 1.4727 | 2.4977 |
| stress | `cost/action_rate` | 0.0034 | 0.0010 | 0.9454 |
| stress | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| stress | `cost/torques` | 0.0020 | 0.0023 | 0.0494 |
| stress | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| stress | `reward/imitation` | -0.2107 | 1.9015 | 2.0917 |
| stress | `reward/tracking_ang_vel` | 5.6562 | 5.9997 | 6.0000 |
| stress | `reward/tracking_lin_vel` | 1.3167 | 1.6598 | 2.4987 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| vanilla | `PASS_DIAGNOSTIC` | 0.5000 | 0.0208 | 0.1626 | 0.4935 | 0.2646 |
| fitted | `PASS_DIAGNOSTIC` | 0.5000 | 0.0190 | 0.0908 | 0.4960 | 0.2622 |
| stress | `PASS_DIAGNOSTIC` | 0.5000 | 0.0239 | 0.2035 | 0.4961 | 0.2768 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 0.1362 | 0.1362 | 0.0000 | 0.0196 | 0 | 0.00 |
| vanilla | left_knee | 0.2238 | 0.2238 | 0.0000 | 0.0643 | 0 | 0.00 |
| vanilla | left_ankle | 0.2760 | 0.2760 | 0.0000 | 0.0215 | 0 | 0.00 |
| vanilla | right_hip_pitch | 0.1076 | 0.1076 | 0.0000 | 0.0329 | 0 | 0.00 |
| vanilla | right_knee | 0.1773 | 0.1773 | 0.0000 | 0.0664 | 0 | 0.00 |
| vanilla | right_ankle | 0.2246 | 0.2246 | 0.0000 | 0.0451 | 0 | 0.00 |
| fitted | left_hip_pitch | 0.1364 | 0.1250 | 0.0085 | 0.0217 | 3 | 0.00 |
| fitted | left_knee | 0.2058 | 0.2001 | 0.0140 | 0.0744 | 4 | 0.00 |
| fitted | left_ankle | 0.2625 | 0.2474 | 0.0169 | 0.0283 | 3 | 0.00 |
| fitted | right_hip_pitch | 0.0979 | 0.0915 | 0.0064 | 0.0351 | 3 | 0.00 |
| fitted | right_knee | 0.1928 | 0.1829 | 0.0126 | 0.0787 | 3 | 0.00 |
| fitted | right_ankle | 0.2412 | 0.2360 | 0.0163 | 0.0536 | 4 | 0.00 |
| stress | left_hip_pitch | 0.1517 | 0.0785 | 0.0145 | 0.0236 | 8 | 0.00 |
| stress | left_knee | 0.2332 | 0.1437 | 0.0272 | 0.0752 | 9 | 0.00 |
| stress | left_ankle | 0.2312 | 0.1363 | 0.0265 | 0.0268 | 10 | 0.00 |
| stress | right_hip_pitch | 0.1301 | 0.0700 | 0.0128 | 0.0337 | 9 | 0.00 |
| stress | right_knee | 0.1911 | 0.1207 | 0.0231 | 0.0871 | 9 | 0.00 |
| stress | right_ankle | 0.2226 | 0.1401 | 0.0278 | 0.0434 | 10 | 0.00 |

## Interpretation

- Candidate sim gate is holding. Do not use this policy on the robot.
- No robot motion, deployment, runtime behavior change, or training was performed.
