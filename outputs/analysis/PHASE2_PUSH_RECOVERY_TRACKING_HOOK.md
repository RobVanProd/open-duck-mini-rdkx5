# Phase 2 Push-Recovery Tracking Hook

status: `PASS_PUSH_RECOVERY_TRACKING_HOOK_PLUMBING`

## Scope

This is an offline tooling/env plumbing result. No robot tests, SSH, deploy,
grounded replay, runtime behavior changes, or policy overwrite were performed.

## Motivation

The B0C `lk097` focused seed-4 trace showed that the current rough
`z=0.002` gentle-push near-pass does not fail from a global envelope or
saturation problem. It misses the strict gate by a localized left-knee
post-push tracking margin:

```text
left_knee joint_tracking_p95: 0.2013 rad
threshold: 0.2000 rad
high-error ticks near push: 13/13 within +/-25 ticks
velocity excess: 0.0000 rad/s
action saturation: 0.0%
```

Global tracking penalties and global gain/target-rate changes have already
shown the wrong tradeoff: they reduce forward motion or move the miss without
preserving the rough-terrain gait.

## Added Default-Off Hook

The local Playground `joystick` env now exposes a default-off reward term:

```text
push_recovery_actuator_tracking
```

It penalizes sent-vs-applied actuator target mismatch only during a configurable
recovery window after push impulses. It can optionally restrict the cost to a
comma-separated set of actuator indices; for the current localized failure,
index `3` targets `left_knee`.

RDK wrapper flags:

```text
--push-recovery-actuator-tracking-scale
--push-recovery-actuator-tracking-huber-delta
--push-recovery-tracking-window-steps
--push-recovery-tracking-joint-indices
```

Playground runner flags:

```text
--push_recovery_actuator_tracking_scale
--push_recovery_actuator_tracking_huber_delta
--push_recovery_tracking_window_steps
--push_recovery_tracking_joint_indices
```

All defaults preserve existing behavior.

## Smoke Validation

A tiny CPU smoke was run from the B0C restore checkpoint with the new cost
enabled for left-knee post-push recovery:

```text
platform: cpu
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
num_timesteps: 20
ppo_num_envs: 1
push_recovery_actuator_tracking_scale: -0.02
push_recovery_actuator_tracking_huber_delta: 0.03
push_recovery_tracking_window_steps: 25
push_recovery_tracking_joint_indices: 3
push: enabled, 0.05-0.10 impulse, 1.0-1.5 s interval
status: PASS_SMOKE_RUN
returncode: 0
```

The temporary terrain XML was restored after the smoke run.

## Next Branch

The next valid policy-producing branch should start from the `lk097` near-pass
line and use this hook as a localized correction:

```text
candidate root: outputs/analysis/phase2_b0c_245_leftknee_scale097_candidate/candidate.onnx
restore checkpoint: outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760
hook: push_recovery_actuator_tracking
joint indices: 3
window: 25 ticks
```

Gate before any broader DR stage:

```text
corrected bridge
rough_terrain_backlash
terrain_hfield_z_scale: 0.002
gentle pushes: 0.05-0.10
8 seeds
x=0.08 and x=0.0 command semantics
```

Robot validation remains blocked.
