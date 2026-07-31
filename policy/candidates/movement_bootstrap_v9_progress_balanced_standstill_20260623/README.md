# Movement Bootstrap V9 Progress-Balanced Standstill

This directory preserves the final checkpoint from `movement_bootstrap_v9`, an
offline A100 run that restarted from the v7 moving anchor with lighter
overshoot/pitch damping than V8 and stronger command-window progress pressure.

It is not a deployable robot policy.

## Policy Hash

```text
e281667087140800d5b06d547ea6644fdf40af7c49897e6774ea913e5fb41839
```

## Source

```text
recipe: movement_bootstrap_v9
initial checkpoint: policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320/
final phase: 03_phase3_consolidate_progress_no_lunge
checkpoint: checkpoint_2026_06_23_235119_122880/
```

## Gate Result

Offline candidate gates hold:

```text
x=0.0:  HOLD_CANDIDATE_TRACKING
x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

At `x=0.0`, the candidate survived the full duration but missed the pitch
tracking threshold:

```text
fitted samples: 750
fitted termination: duration_complete
fitted mean local vx: 0.0003 m/s
max pitch tracking p95: 0.0932 rad
threshold: 0.0800 rad
```

At `x=0.08` with the fitted bridge, the candidate stayed stable but remained
near standstill:

```text
fitted samples: 750
fitted termination: duration_complete
fitted mean local vx: 0.0017 m/s
fitted track ratio: 0.0206
max pitch-chain p95 target velocity: 0.2879 rad/s
max pitch tracking p95: 0.0921 rad
action saturation: 0%
```

Interpretation:

V9 did not recover the V7 moving gait. Reducing V8's stabilizers and increasing
command-window progress pressure was not enough to escape the stable
near-standstill basin. The next useful offline task should stop tuning the same
reward balance and instead add a stronger continuity/teacher-action mechanism,
explicit gait prior, or checkpoint-sweep diagnostics that select an earlier
moving checkpoint before consolidation destroys motion.

Robot validation remains blocked.
