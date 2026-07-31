# Movement Bootstrap V8 Overshoot-Stabilized Standstill

This directory preserves the final checkpoint from `movement_bootstrap_v8`, an
offline A100 run that started from the v7 anchored checkpoint and added
forward-overshoot, pitch, and pitch-rate costs under the fitted actuator bridge.

It is not a deployable robot policy.

## Policy Hash

```text
b8528e43083e3b9ea920a2847e6a9cfb30e11f7960433565f0945eb529bc4642
```

## Source

```text
recipe: movement_bootstrap_v8
initial checkpoint: policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320/
final phase: 02_phase2_v7_lunge_damping_consolidate
checkpoint: checkpoint_2026_06_23_225832_122880/
```

## Gate Result

Offline candidate gates hold:

```text
x=0.0:  HOLD_CANDIDATE_TRACKING
x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

At `x=0.0`, the candidate survived the full duration but narrowly missed the
pitch tracking threshold:

```text
fitted samples: 750
fitted termination: duration_complete
fitted mean local vx: 0.0003 m/s
max pitch tracking p95: 0.0863 rad
threshold: 0.0800 rad
```

At `x=0.08` with the fitted bridge, V8 no longer lunged or fell, but it also
did not walk:

```text
fitted samples: 750
fitted termination: duration_complete
fitted mean local vx: 0.0015 m/s
fitted track ratio: 0.0190
max pitch-chain p95 target velocity: 0.2760 rad/s
max pitch tracking p95: 0.0871 rad
action saturation: 0%
```

Interpretation:

V8 confirms that the v7 forward lunge can be damped, but the applied damping
and progress balance overcorrected into near-standstill. The next recipe should
preserve the overshoot stabilizers while increasing command-progress pressure
or annealing overshoot/stability costs so `x=0.08` produces meaningful forward
motion without returning to the v7 lunge.

Robot validation remains blocked.
