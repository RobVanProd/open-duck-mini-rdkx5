# Sim Actuator Bridge Eval

overall_status: `HOLD_SIM_RUNTIME_ERROR`
policy: `/home/lsd/robots/open-duck-mini-rdkx5/policy/BEST_WALK_ONNX_2.onnx`
fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
command_x: `0.08`
duration_s: `15.0`

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

status: `HOLD_SIM_RUNTIME_ERROR`
env: `None` / task `None`
obs/action dims: `None` / `None`
actuator_names: `None`
ctrl_dt: `None`
sim_dt: `None`
jax: `None` `None`
insertion_point: `None`
double_rate_limit: `None`
worker_error: `closed-loop worker exited -6 before writing JSON`
worker_returncode: `-6`

Worker output excerpt:

```text
E0621 21:51:37.905249 1176048 pjrt_stream_executor_client.cc:2091] Execution of replica 0 failed: INTERNAL: Failed to retrieve branch_index value on stream 0x4715eec0: Could not synchronize on ROCM stream: ROCM_ERROR_ILLEGAL_ADDRESS.
Failed to import warp: No module named 'warp'
Failed to import mujoco_warp: No module named 'warp'
Traceback (most recent call last):
jax.errors.JaxRuntimeError: INTERNAL: Failed to retrieve branch_index value on stream 0x4715eec0: Could not synchronize on ROCM stream: ROCM_ERROR_ILLEGAL_ADDRESS.
F0621 21:51:37.926340 1176048 rocm_context.cc:137] Check failed: ToStatus(wrap::hipCtxSetCurrent(context_), "Failed setting context") is OK (INTERNAL: Failed setting context: ROCM_ERROR_ILLEGAL_ADDRESS)
```

### Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | reward_mean |
|---|---:|---|---:|---:|---:|

### Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| NA | NA | NA | NA | NA | NA | NA | NA |

## Interpretation

- Full MuJoCo policy-loop reproduction is not complete yet.
- Closed-loop sim gate result: `HOLD_SIM_RUNTIME_ERROR`.
- No robot motion, deployment, runtime behavior change, or training was performed.
