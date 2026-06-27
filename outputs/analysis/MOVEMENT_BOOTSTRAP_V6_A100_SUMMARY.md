# Movement Bootstrap V6 A100 Summary

status: `HOLD_NON_DEPLOYABLE`

This was an offline A100 training run. It did not SSH, deploy, touch the robot, or change runtime behavior.

## Final Candidate

- recipe: `movement_bootstrap_v6`
- final ONNX sha256: `fe88c59c509c6d50932cb17902e0615aa33286fb922a47904ab11f0153a8df0b`
- robot validation: `BLOCKED`

## Gates

| gate | status | samples | termination | mean_local_vx | track_ratio | max_pitch_vel_p95 | max_tracking_p95 | body_pitch_p95 | base_height_min |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| x=0.0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 78 | `fall_or_nan` | 0.1935 | NA | 2.9157 | 0.2197 | 1.2246 | 0.0318 |
| x=0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0009 | 0.0118 | 0.1612 | 0.0679 | 0.0921 | 0.1537 |

## Phase Checkpoints

Phase 1 did not recover the v5 phase-1 moving gait:

```text
x=0.06: duration complete, mean local vx 0.0004 m/s, pitch p95 vel 0.1254 rad/s
x=0.08: duration complete, mean local vx 0.0009 m/s, pitch p95 vel 0.1077 rad/s
```

Phase 2 also stayed in standstill:

```text
x=0.06: duration complete, mean local vx 0.0005 m/s, pitch p95 vel 0.1741 rad/s
x=0.08: duration complete, mean local vx 0.0010 m/s, pitch p95 vel 0.1390 rad/s
```

## Interpretation

V6 kept target velocities inside the measured envelope, but it failed at the continuity problem: the stricter envelope from phase 1 plus stability-oriented consolidation produced standstill rather than recovering the preserved v5 phase-1 motion.

This is evidence against another generic curriculum tweak. The next offline task should implement a real teacher-policy/action-anchor loss or trust-region mechanism using the preserved v5 phase-1 policy as the reference.

Do not request robot validation for this candidate.
