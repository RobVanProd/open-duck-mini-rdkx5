# Phase 2 Seed5 Contact-Phase Diagnostic

status: `HOLD_CONTACTPHASE_SEED5_STILL_FALLS`

## Scope

Offline-only diagnostic for the corrected-bridge Phase 2 rough-terrain branch.
No robot tests, SSH, deploy, grounded replay, runtime behavior changes, or
training from scratch were performed.

## Why

The previous early-state weighted BC correction did not recover seed 5. Seed 5
diverges at the first contact/support state in both x=0.08 and x=0.0 rough
terrain, so this test added the two foot-contact bits to the deployable
phase/command modulation context:

```text
old context: obs[6], obs[99], obs[100]
new context: obs[6], obs[97], obs[98], obs[99], obs[100]
```

The exported ONNX contract remains deployable:

```text
obs[1,101] -> continuous_actions[1,14]
```

## Fit

```text
manifest:
  outputs/analysis/phase2_seed5_early_state_weighted_aggregate_manifest.json

candidate:
  outputs/analysis/phase2_seed5_early_state_contactphase_bc_student/candidate.onnx

candidate_sha256:
  1994b04b9259a72b44e3e600f1877dc3583ffb0a5662e6b92ba7778e2478c50d

fit status:
  PASS_PHASE_MODULATED_BC_FIT_SMOKE

fit p95 action error:
  0.0192
```

## x=0.08 Rough z=0.002 Gate

```text
artifact:
  outputs/analysis/PHASE2_SEED5_EARLY_STATE_CONTACTPHASE_X008_ROUGH_Z002_8SEED_GATE_CPU.md

task:
  rough_terrain_backlash

terrain_hfield_z_scale:
  0.002

bridge:
  corrected fitted

hard swing gate:
  min_swing_segments_per_foot >= 1
  min_swing_rel_x_range_p95_m >= 0.003
  min_swing_peak_lift_m >= 0.005
```

Result:

```text
passes: seeds 1,2,4,6,7
target-velocity hold: seed 0, excess 0.0180 rad/s
low-progress hold: seed 3
fall/reverse hold: seed 5
falls: 1/8
duration_complete: 7/8
mean track ratio: -0.1107 due to seed 5 reverse/fall
max tracking p95: 0.1970 rad
mean single support: 23.13%
```

Compared with the previous early-state weighted phase/command student, contact
conditioning reduced the tracking holds and preserved several useful rough
terrain passes, but it did not solve the seed-5 command-independent fall.

## x=0.0 Seed-5 Check

```text
artifact:
  outputs/analysis/PHASE2_SEED5_EARLY_STATE_CONTACTPHASE_X0_SEED5_ROUGH_Z002_GATE_CPU.md

seed:
  5

status:
  HOLD_CANDIDATE_FALL_OR_TERMINATION

samples:
  43

mean_vx:
  -0.3528 m/s

max tracking p95:
  0.2286 rad
```

Seed 5 still falls at zero command, so the remaining blocker is not only
positive-command swing/advance. It is still an initial-state/contact recovery
failure.

## Decision

Do not promote the contact-phase student and do not repeat the same feed-forward
context tweak with minor hyperparameter changes.

This diagnostic closes the cheapest deployable contact-conditioned modulation
rung. The next useful branch needs a different correction mechanism:

- a stateful/frame-history diagnostic to test whether seed 5 needs memory,
- or a recovery teacher/relabel pass that changes seed 5's first contact
  transition before the negative-velocity/fall mode begins.

Robot validation remains blocked.
