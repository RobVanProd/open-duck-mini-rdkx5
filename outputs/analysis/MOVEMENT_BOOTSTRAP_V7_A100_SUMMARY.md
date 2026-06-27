# Movement Bootstrap V7 A100 Summary

status: `HOLD_NON_DEPLOYABLE`

This was an offline A100 continuation run. It did not SSH, deploy, touch the
robot, or change runtime behavior.

## Candidate

- recipe: `movement_bootstrap_v7`
- initial checkpoint:
  `policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/checkpoint_2026_06_23_205634_368640`
- final ONNX sha256:
  `fa1157ea81dacbf7e7fc1dd2835963017616c8d0be3b3dc19e2389db0307def8`
- preserved candidate:
  `policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/`
- robot validation: `BLOCKED`

## Gates

| gate | status | samples | termination | mean_local_vx | track_ratio | max_pitch_vel_p95 | max_tracking_p95 | body_pitch_p95 | base_height_min |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| x=0.0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0004 | NA | 0.1840 | 0.0860 | 0.0904 | 0.1537 |
| x=0.08 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 60 | `fall_or_nan` | 0.2640 | 3.2994 | 2.2663 | 0.2070 | 1.2996 | 0.0362 |

## Interpretation

V7 improved the zero-command failure into a near-pass tracking hold. It also
preserved in-envelope forward motion under the fitted bridge at `x=0.08`, but
the rollout still falls quickly.

This rules out target velocity and action saturation as the immediate cause for
the v7 nonzero-command failure:

```text
x=0.08 fitted max pitch-chain p95 target velocity: 2.2663 rad/s
fitted envelope lower bound: 2.5 rad/s
action saturation: 0%
```

The remaining offline blocker is stability/contact timing during forward motion
under the fitted actuator bridge. Do not request robot validation for this
candidate.
