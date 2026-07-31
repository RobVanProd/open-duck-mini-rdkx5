# Phase 2 B0C LK097 Push Localization Decision

status: `HOLD_B0C_LK097_PUSH_LOCAL_LEFT_KNEE_MARGIN`

## Scope

This is an offline sim/eval localization result. No robot tests, SSH, deploy,
grounded replay, runtime behavior changes, or policy overwrite were performed.

## Candidate Under Test

```text
policy: outputs/analysis/phase2_b0c_245_leftknee_scale097_candidate/candidate.onnx
policy_sha256: 4985f1bccaa68838d006104fb380c50a2f06d8627ff8990564f178c0b0ad7f87
corrected_bridge: outputs/analysis/actuator_response_fit_corrected_knee.json
corrected_bridge_sha256: 3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
command_x: 0.08
seed: 4
duration_s: 5.0
push: enabled, 0.05-0.10 impulse, 1.0-1.5 s interval
```

## Result

The `lk097` candidate remains the strongest current near-pass for rough
`z=0.002` plus gentle pushes. The seed-4 focused trace did not fall, did not
saturate, and did not exceed the corrected velocity envelope. The gate miss is
localized to the strict pitch-chain tracking threshold:

```text
gate_status: HOLD_CANDIDATE_TRACKING
track_ratio: 0.4285
mean_vx: 0.0343 m/s
progress_x: 0.0423 m
max_pitch_tracking_p95: 0.2013 rad
threshold: 0.2000 rad
max_sent_target_velocity_p95: 1.8002 rad/s
max_velocity_limit_excess: 0.0000 rad/s
action_saturation: 0.0%
body_pitch_abs_p95: 0.1402 rad
base_height_min: 0.1506 m
termination: duration_complete
```

Offending joint:

```text
left_knee joint_tracking_p95: 0.2013 rad
left_knee sent_vel_p95: 1.6354 rad/s
left_knee bridge_tracking_p95: 0.1022 rad
left_knee lag_ticks: 4
```

## Push Correlation

The trace contains four gentle push impulses at ticks:

```text
57, 115, 173, 231
```

All left-knee high-error ticks above the trace p95 are within `+/-25` ticks of
a push impulse:

```text
left_knee_abs_error_p95: 0.2013 rad
left_knee_abs_error_max: 0.2234 rad
high_error_near_push: 13/13
high_error_not_near_push: 0/13
```

The worst ticks occur during post-push recovery windows, not because the action
or target velocity is saturating. This makes the current blocker a local
push-recovery tracking margin, not a global gait, target-rate, or envelope
failure.

## Decision

B0F should not be continued: it trained successfully on A100 but reduced
forward progress and still missed the strict tracking gate.

Do not continue scalar gain sweeps or global target-rate clipping. Those have
already shown the wrong tradeoff: they can reduce motion or shift the miss, but
they do not preserve the rough-terrain gait while adding perturbation margin.

The next valid Phase 2 correction should start from the `lk097` near-pass line
and target the localized push-recovery window:

- preserve the nominal no-push and gentle-push gait,
- add a push-state or post-push tracking-margin correction,
- focus on left-knee recovery without globally weakening command tracking,
- gate with the same corrected bridge, rough `z=0.002`, gentle-push 8-seed
  screen before any broader DR stage.

Robot validation remains blocked.
