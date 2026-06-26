# Sim Actuator Bridge Eval

overall_status: `PASS_CLOSED_LOOP_REPRODUCTION`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/source_vx_selector_trace_dagger2_mlp128_candidate/candidate.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
task: `flat_terrain`
command_x: `0.08`
command_y: `0.0`
command_yaw: `0.0`
duration_s: `10.0`
seed: `0`
eval_role: `reproduction`
jax_platform_requested: `None`

## Contract Preflight

- policy_status: `PASS_POLICY_CONTRACT_ASSUMED`
- policy_input_shape: `[1, 101]`
- policy_output_shape: `[1, 14]`
- playground_static_path: `/tmp/open_duck_playground_origin_main/playground/open_duck_mini_v2`
- playground_env_python: `/home/lsd/robots/open-duck-mini-rdkx5/../envs/open-duck-playground/bin/python`
- playground_instantiated_status: `PASS_ENV_INSTANTIATED`
- playground_action_size: `14`
- playground_observation_size: `{'privileged_state': [212], 'state': [101]}`
- playground_actuator_names: `['left_hip_yaw', 'left_hip_roll', 'left_hip_pitch', 'left_knee', 'left_ankle', 'neck_pitch', 'head_pitch', 'head_yaw', 'head_roll', 'right_hip_yaw', 'right_hip_roll', 'right_hip_pitch', 'right_knee', 'right_ankle']`
- sim_preflight_status: `HOLD_SIM_INTEGRATION_PENDING`
- sim_preflight_reason: Policy and local Playground dimensions appear compatible, but the closed-loop JAX/MJX policy eval path with actuator bridge is not wired yet.
- recommended_next_command: `python3 tools/audit_policy_sim_contract.py --policy policy/BEST_WALK_ONNX_2.onnx --playground-path ../Open_Duck_Playground`

## Closed-Loop Sim Eval

status: `PASS_CLOSED_LOOP_REPRODUCTION`
eval_role: `reproduction`
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

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | mean_local_vx | track_ratio | reward_mean |
|---|---:|---|---:|---:|---:|---:|---:|
| fitted | 500 | duration_complete | 0.0478 | 0.1536 | 0.0197 | 0.2457 | 0.4631 |

### Reward-Term Summary

| mode | term | mean | p95 | max |
|---|---|---:|---:|---:|
| fitted | `cost/action_rate` | 0.0342 | 0.0901 | 0.6996 |
| fitted | `cost/stand_still` | 0.0000 | 0.0000 | 0.0000 |
| fitted | `cost/torques` | 0.0048 | 0.0099 | 0.0449 |
| fitted | `reward/alive` | 20.0000 | 20.0000 | 20.0000 |
| fitted | `reward/imitation` | 0.8259 | 3.5176 | 4.1500 |
| fitted | `reward/tracking_ang_vel` | 0.6793 | 4.9067 | 5.9941 |
| fitted | `reward/tracking_lin_vel` | 1.6879 | 2.4693 | 2.5000 |

### Forward Shortfall Diagnostic

| mode | status | required_ratio | progress_ratio_mean | progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |
|---|---|---:|---:|---:|---:|---:|
| fitted | `PASS_DIAGNOSTIC` | 0.5000 | 0.2457 | 0.8685 | 0.3029 | 0.1553 |

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| fitted | left_hip_pitch | 1.4379 | 1.2508 | 0.0813 | 0.1249 | 3 | 0.00 |
| fitted | left_knee | 2.4413 | 2.2213 | 0.1457 | 0.1957 | 4 | 0.00 |
| fitted | left_ankle | 1.9697 | 1.8424 | 0.1193 | 0.1885 | 4 | 0.00 |
| fitted | right_hip_pitch | 1.6115 | 1.5487 | 0.1001 | 0.1254 | 3 | 0.00 |
| fitted | right_knee | 3.8533 | 3.0000 | 0.2119 | 0.2177 | 4 | 0.00 |
| fitted | right_ankle | 1.7910 | 1.6757 | 0.1063 | 0.1721 | 4 | 0.00 |

## Interpretation

- The fitted/stress actuator bridge modes completed and can be compared against real suspended evidence. Next step is offline review, not robot motion.
- No robot motion, deployment, runtime behavior change, or training was performed.
