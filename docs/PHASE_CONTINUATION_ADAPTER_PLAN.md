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

## Adapter Smoke Result

Three default-off adapter modes were implemented in
`tools/run_target_sequence_replay_smoke.py` and tested on the aggregate robust
lateral-fix phase table over seeds 0 and 2:

```text
contact_hold:
  status: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
  seed0/seed2 vx: 0.0119 / 0.0138 m/s
  seed0/seed2 contact mismatch: 2.76% / 0.00%
  seed0/seed2 holds per second: 1.33 / 0.00

contact_match:
  status: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
  seed0/seed2 vx: 0.0117 / 0.0138 m/s
  seed0/seed2 contact mismatch: 2.76% / 0.00%
  phase skips per second: 0.00 / 0.00

state_match:
  status: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
  seed0/seed2 vx: 0.0117 / 0.0138 m/s
  seed0/seed2 contact mismatch: 2.76% / 0.00%
  phase skips per second: 0.00 / 0.00
```

Artifacts:

```text
outputs/analysis/TARGET_SEQUENCE_REPLAY_SMOKE_contact_hold.md
outputs/analysis/target_sequence_replay_smoke_contact_hold.json
outputs/analysis/TARGET_SEQUENCE_REPLAY_SMOKE_contact_match.md
outputs/analysis/target_sequence_replay_smoke_contact_match.json
outputs/analysis/TARGET_SEQUENCE_REPLAY_SMOKE_state_match.md
outputs/analysis/target_sequence_replay_smoke_state_match.json
```

Interpretation:

```text
Contact/phase matching does not rescue the aggregate target table because the
contact mismatch rate is already low. The replay is not failing because phase
selection cannot find the right contact pattern; it is failing because the
low-velocity aggregate target damps into low forward progress and marginal
pitch. The current robust target table should not be promoted into PPO or BC
labels.
```

Updated next step:

```text
Do not continue adapter work on the aggregate table alone. Either generate a
longer self-consistent target trajectory directly, or build a learner/objective
that uses the short target fragment as a soft motion prior while optimizing
closed-loop forward progress and posture from the start.
```

## Sustained Target Probe Result

The existing dynamic-roll lateral-fix trace set was rescored at longer windows,
then a bounded sustained-motion primitive search was run with slightly faster
cadence and larger hip/knee amplitudes.

Existing lateral-fix traces:

```text
100-sample objective:
  status: HOLD_NO_SEED_ROBUST_TARGETS
  robust_mode_count: 0

100-sample curation:
  status: HOLD_INSUFFICIENT_CURATED_WINDOWS
  curated_seed_windows: 0

150-sample objective:
  status: HOLD_NO_SEED_ROBUST_TARGETS
  robust_mode_count: 0

150-sample curation:
  status: HOLD_INSUFFICIENT_CURATED_WINDOWS
  curated_seed_windows: 0
```

New sustained probe:

```text
search candidates: 180
seeds: 0,2
duration: 4.0 s

100-sample objective:
  status: HOLD_NO_SEED_ROBUST_TARGETS
  robust_mode_count: 0

100-sample curation:
  status: HOLD_INSUFFICIENT_CURATED_WINDOWS
  curated_seed_windows: 0

150-sample objective:
  status: HOLD_NO_SEED_ROBUST_TARGETS
  robust_mode_count: 0

150-sample curation:
  status: HOLD_INSUFFICIENT_CURATED_WINDOWS
  curated_seed_windows: 0
```

Main failure reasons:

```text
100-sample sustained probe:
  low_forward_velocity: 304
  low_base_height: 162
  single_contact_pattern_dominates: 110
  high_body_pitch: 65

150-sample sustained probe:
  low_forward_velocity: 301
  single_contact_pattern_dominates: 256
  low_base_height: 146
  high_body_pitch: 34
```

Interpretation:

```text
The primitive target-source family can produce short in-envelope motion
fragments, but it does not produce a longer self-consistent gait under the
current strict gates. The next branch should stop trying to convert these
fragments directly into labels and should instead use them as soft priors or
change the target generator structure.
```
