# Movement Bootstrap V7 Checkpoint Anchor

This directory preserves the final checkpoint from `movement_bootstrap_v7`, an
offline A100 continuation run that started from the recovered v5 phase-1 moving
checkpoint.

It is not a deployable robot policy.

## Policy Hash

```text
fa1157ea81dacbf7e7fc1dd2835963017616c8d0be3b3dc19e2389db0307def8
```

## Source

```text
recipe: movement_bootstrap_v7
initial checkpoint: policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/checkpoint_2026_06_23_205634_368640/
final phase: 02_phase2_checkpoint_anchor_fitted_bridge
checkpoint: checkpoint_2026_06_23_213846_184320/
```

## Gate Result

Offline candidate gates hold:

```text
x=0.0:  HOLD_CANDIDATE_TRACKING
x=0.08: HOLD_CANDIDATE_FALL_OR_TERMINATION
```

At `x=0.0`, the candidate survived the full duration but missed the pitch
tracking threshold narrowly:

```text
fitted samples: 750
fitted termination: duration_complete
fitted mean local vx: 0.0004 m/s
max pitch tracking p95: 0.0860 rad
threshold: 0.0800 rad
```

At `x=0.08` with the fitted bridge, it preserved in-envelope forward motion but
still fell:

```text
fitted samples: 60
fitted termination: fall_or_nan
fitted mean local vx: 0.2640 m/s
fitted track ratio: 3.2994
max pitch-chain p95 target velocity: 2.2663 rad/s
max pitch tracking p95: 0.2070 rad
action saturation: 0%
```

Interpretation:

V7 improved the zero-command failure into a near-pass tracking hold, but did not
stabilize nonzero walking. The remaining blocker is forward-motion stability
under the fitted actuator bridge, not target velocity or action saturation.
