# Phase Continuation Adapter Plan

This is an offline-only plan. It does not authorize PPO training, robot
validation, SSH, deploy, runtime changes, or policy changes.

## Problem

The dynamic-roll lateral-fix target source passed the strict source gate, and
one short sequence replay produced forward motion for about 60 ticks. The same
target tables are not reusable gait labels yet:

```text
one-step BC:
  HOLD_BC_REPLAY_LOW_FORWARD_MOTION / HOLD_BC_REPLAY_TERMINATED

1.2 s sequence replay:
  HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE

3.0 s sequence replay:
  HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION

3.0 s seam-corrected replay:
  HOLD_SEQUENCE_REPLAY_TERMINATED
```

The failure is no longer "no target source exists." The failure is that target
phase, contact timing, and body state do not continue cleanly once the short
window is reused.

## Working Hypothesis

The 50-tick target window contains a useful motion fragment, but fixed-time
looping assumes the simulated body and feet return to a compatible state at the
cycle boundary. They do not. Simple linear seam correction changes action
continuity but does not enforce contact or body-state continuity, and it turns
seed0 into a lunge/fall.

## Next Adapter

Add a default-off replay adapter that chooses target phase using contact/state
compatibility instead of fixed modulo time.

Candidate modes:

```text
fixed_time:
  current behavior; prefix once, then loop target window by tick modulo length

contact_hold:
  advance the target phase only when actual foot contact matches the target
  contact pattern, up to a small hold limit

contact_match:
  at each tick, choose the nearest future phase within a small lookahead whose
  target contact pattern matches the actual current contact pattern

state_match:
  choose the nearest future phase by contact pattern plus small penalties for
  base height, body pitch, and local lateral velocity mismatch
```

This should remain a replay diagnostic first, not a learner.

## Metrics

Use the same closed-loop x=0.04 replay gates:

```text
duration: 3.0 s
seeds: 0,2 initially; expand to 0-7 only after a near-pass
min mean vx: 0.02 m/s
max vy p95: 0.12 m/s
max body pitch p95: 0.25 rad
min base height: 0.10 m
max sent target velocity p95: 3.75 rad/s
no termination
```

Also report:

```text
phase holds per second
phase skips per second
contact pattern mismatch rate
dominant contact pattern
phase index histogram
```

## Stop/Go Rule

```text
PASS_PHASE_CONTINUATION_REPLAY:
  at least one adapter passes x=0.04 replay over seed0 and seed2 without
  exceeding the target velocity envelope

HOLD_PHASE_CONTINUATION_UNSTABLE:
  adapters still fail by lateral/pitch/height/termination

HOLD_PHASE_CONTINUATION_LOW_PROGRESS:
  adapters stabilize by freezing or double-support drift
```

Only `PASS_PHASE_CONTINUATION_REPLAY` permits a compact sequence-aware
imitation learner. It still does not permit robot validation.

## Non-Goals

```text
do not launch PPO from the current target tables
do not repeat one-step BC unchanged
do not tune robot runtime behavior
do not change the physical robot
do not run grounded replay
do not relax the actuator envelope to make a target pass
```
