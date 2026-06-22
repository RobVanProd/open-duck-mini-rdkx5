# CUDA L4 Closed-Loop Actuator Bridge Eval

Date: 2026-06-22

Source: Google Colab L4 run reported by the operator.

## Result

```text
overall_status: PASS_CLOSED_LOOP_REPRODUCTION
JAX backend: gpu
JAX device: cuda:0
GPU: NVIDIA L4
policy: BEST_WALK_ONNX_2.onnx
command_x: 0.08
duration_s: 15.0
bridge modes: vanilla, fitted, stress
```

This confirms the closed-loop policy/eval path and target-stage actuator bridge
can run on a CUDA GPU. The local `7900 XTX` failure is therefore a ROCm/MJX
backend issue, not a policy/sim contract issue and not a blocker in the bridge
logic itself.

## Contract

The CUDA run instantiated the Open Duck Playground `Joystick(flat_terrain)` env
with the expected deployed policy contract:

```text
state observation: 101
privileged_state observation: 212
action size: 14
ctrl_dt: 0.02
sim_dt: 0.002
actuator order:
  left_hip_yaw
  left_hip_roll
  left_hip_pitch
  left_knee
  left_ankle
  neck_pitch
  head_pitch
  head_yaw
  head_roll
  right_hip_yaw
  right_hip_roll
  right_hip_pitch
  right_knee
  right_ankle
```

Bridge insertion point:

```text
target_stage_direct
double_rate_limit: False
```

## Mode Summary

| mode | samples | termination | body_pitch_p95 | base_height_min | reward_mean |
|---|---:|---|---:|---:|---:|
| vanilla | 750 | duration_complete | 0.0340 | 0.1560 | 0.5570 |
| fitted | 750 | duration_complete | 0.0674 | 0.1536 | 0.5033 |
| stress | 750 | duration_complete | 0.0680 | 0.1536 | 0.4813 |

## Pitch-Chain Summary

| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | joint_tracking_p95 | lag_ticks | action_sat_pct |
|---|---|---:|---:|---:|---:|---:|---:|
| vanilla | left_hip_pitch | 2.6781 | 2.6781 | 0.0000 | 0.0849 | 0 | 0.00 |
| vanilla | left_knee | 3.8065 | 3.8065 | 0.0000 | 0.1743 | 0 | 0.00 |
| vanilla | left_ankle | 2.6216 | 2.6216 | 0.0000 | 0.1586 | 0 | 0.00 |
| vanilla | right_hip_pitch | 3.3831 | 3.3831 | 0.0000 | 0.0880 | 0 | 0.00 |
| vanilla | right_knee | 5.2400 | 5.2400 | 0.0000 | 0.2022 | 0 | 0.00 |
| vanilla | right_ankle | 2.1754 | 2.1754 | 0.0000 | 0.1340 | 0 | 0.00 |
| fitted | left_hip_pitch | 2.5851 | 1.8342 | 0.1020 | 0.1146 | 3 | 0.00 |
| fitted | left_knee | 3.4775 | 2.7907 | 0.1657 | 0.1855 | 3 | 0.00 |
| fitted | left_ankle | 2.9783 | 2.4043 | 0.1610 | 0.2048 | 3 | 0.00 |
| fitted | right_hip_pitch | 2.4326 | 1.8747 | 0.1097 | 0.1112 | 3 | 0.00 |
| fitted | right_knee | 4.9098 | 3.0000 | 0.2293 | 0.2169 | 4 | 0.00 |
| fitted | right_ankle | 2.4356 | 1.9464 | 0.1207 | 0.1492 | 3 | 0.00 |
| stress | left_hip_pitch | 3.0056 | 0.5664 | 0.0731 | 0.0710 | 7 | 0.00 |
| stress | left_knee | 2.4982 | 1.0829 | 0.1873 | 0.1415 | 8 | 0.00 |
| stress | left_ankle | 2.8303 | 0.9545 | 0.1260 | 0.1273 | 9 | 0.00 |
| stress | right_hip_pitch | 2.1107 | 0.6143 | 0.0910 | 0.0839 | 8 | 0.00 |
| stress | right_knee | 3.7895 | 1.0807 | 0.1538 | 0.1083 | 8 | 0.00 |
| stress | right_ankle | 3.0433 | 0.9739 | 0.1334 | 0.1192 | 9 | 0.00 |

## Interpretation

The fitted actuator bridge produces closed-loop degradation in the same range as
the real suspended `x=0.08` evidence. The next engineering step is a
training-time actuator wrapper and smoothness/target-velocity objectives, not
more robot motion and not local ROCm debugging as a blocker for correctness.

The local `7900 XTX` ROCm path remains useful to fix for future local training,
but CUDA confirms the sim/eval code path itself is viable.
