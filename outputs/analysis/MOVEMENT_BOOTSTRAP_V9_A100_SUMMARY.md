# Movement Bootstrap V9 A100 Summary

status: `HOLD_NON_DEPLOYABLE`

This was an offline A100 staged-curriculum run. It did not SSH, deploy, touch
the robot, or change runtime behavior.

## Candidate

- recipe: `movement_bootstrap_v9`
- initial checkpoint:
  `policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320`
- final ONNX sha256:
  `e281667087140800d5b06d547ea6644fdf40af7c49897e6774ea913e5fb41839`
- preserved candidate:
  `policy/candidates/movement_bootstrap_v9_progress_balanced_standstill_20260623/`
- robot validation: `BLOCKED`

## Gates

| gate | status | samples | termination | mean_local_vx | track_ratio | max_pitch_vel_p95 | max_tracking_p95 | body_pitch_p95 | base_height_min |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| x=0.0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0003 | NA | 0.2534 | 0.0932 | 0.0493 | 0.1537 |
| x=0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0017 | 0.0206 | 0.2879 | 0.0921 | 0.2172 | 0.1479 |

## Interpretation

V9 confirms the V8 failure mode is not just a single over-strong damping
setting. Starting again from the V7 moving anchor, reducing overshoot/pitch
costs, and increasing command-window progress pressure still converged to a
stable near-standstill solution.

Compared with V8:

```text
V8 x=0.08 fitted track ratio: 0.0190
V9 x=0.08 fitted track ratio: 0.0206
```

This is not meaningful forward-progress recovery. The robot remains blocked
from validation.

## Next Offline Target

The next useful experiment should not be another small reward-weight tweak in
the same family. Better options:

- preserve/evaluate earlier phase checkpoints from V9 and V7 before final
  consolidation
- add an explicit teacher-action or trust-region regularizer against the V7 or
  recovered V5 moving policy
- distill only the motion structure while penalizing overshoot/pitch separately
- build a checkpoint-selection gate that chooses the best moving checkpoint,
  not always the final stabilized checkpoint

Robot validation remains blocked.
