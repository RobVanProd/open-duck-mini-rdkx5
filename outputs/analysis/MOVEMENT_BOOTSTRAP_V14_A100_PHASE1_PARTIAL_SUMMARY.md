# Movement Bootstrap V14 A100 Phase-1 Partial Summary

status: `HOLD_PARTIAL_LOW_PROGRESS`

## Context

V14 was launched as an offline A100 phase-1-only run to test the new
motion-discovery ladder:

```text
recipe: movement_bootstrap_v14
phase: phase1_mild_bridge_motion_discovery
session: open-duck-a100-v14
requested_timesteps: 280000
phase_gate: x=0.08, fitted bridge, CPU gate
robot_touched: false
```

The run reached a partial checkpoint/export at step `102400`, then the detached
Colab process disappeared without writing the workflow exit sentinel or artifact
bundle. Partial stdout/stderr and the step-102400 ONNX were downloaded manually.

```text
partial ONNX:
outputs/analysis/movement_bootstrap_v14_a100_phase1_partial/2026_06_24_064318_102400.onnx

sha256:
fe265e85d0d2e6f8b3d4c2f4b85550adcca6fd56232778be34c1a4634f273161
```

## Training Log Notes

The pinned CUDA stack started and exported checkpoints at:

```text
step 0
step 102400
```

The step-102400 export printed a saturated sample prediction:

```text
[ 1. -1.  1.  1.  1.  1. -1.  1. -1. -1. -1.  1.  1.  1.]
```

The run did not produce a final manifest, so this is not a complete V14 phase-1
result.

## CPU Gate On Partial Checkpoint

The step-102400 ONNX was evaluated locally with the V14 phase-1 reward overrides:

```text
status: HOLD_CANDIDATE_FALL_OR_TERMINATION
samples: 120
termination: fall_or_nan
command_x: 0.08
mean local vx: 0.0014 m/s
forward_tracking_ratio: 0.0181
reward_mean: -0.1850
max_action_saturation_pct: 0.0
max_pitch_tracking_p95_rad: 0.0718
max_sent_target_velocity_p95_rad_s: 0.2466
diagnostic/command_progress_failure max: 1.0
cost/command_progress_failure max: 80.0
```

The partial checkpoint is therefore still a low-motion policy. It should not be
used as a restore anchor and should not be tested on the robot.

## Interpretation

V14's mild-bridge discovery direction did not show useful motion by step
`102400`. Because the run died early, this does not fully falsify V14, but the
available checkpoint is already failing the same short-lived low-progress gate.

Do not continue this exact partial checkpoint blindly. The next offline work
should either:

- fix the Colab workflow's missing-sentinel failure handling and rerun phase 1
  cleanly, or
- change the discovery strategy more structurally before another A100 run.

Robot validation remains blocked.
