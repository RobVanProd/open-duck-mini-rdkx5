# Phase 2 Seed5 Recurrent Diagnostic

status: `HOLD_RECURRENT_SEED5_STILL_FALLS`

## Scope

Offline-only state/history diagnostic for the corrected-bridge Phase 2
rough-terrain branch. No robot tests, SSH, deploy, grounded replay, runtime
behavior changes, or training from scratch were performed.

This ONNX is not robot-deployable because it uses an explicit hidden-state
contract:

```text
inputs:  obs[1,101], h_in[1,96]
outputs: continuous_actions[1,14], h_out[1,96]
```

## Why

Contact-phase feed-forward modulation did not recover seed 5. The next cheap
diagnostic was to test whether a small recurrent student trained on the same
latest seed-5 aggregate could alter the early seed-5 contact-state fall.

## Fit

```text
manifest:
  outputs/analysis/phase2_seed5_early_state_weighted_aggregate_manifest.json

candidate:
  outputs/analysis/phase2_seed5_early_state_recurrent_bc_student/candidate.onnx

candidate_sha256:
  8b41b7276a59b6d6ddfdf0ec295bae965673b6882ab8ccad5645cb09341a3e4d

hidden_dim:
  96

sequence_length:
  64

fit status:
  PASS_RECURRENT_BC_FIT_SMOKE
```

## Seed-5 x=0.08 Rough z=0.002 Gate

```text
artifact:
  outputs/analysis/PHASE2_SEED5_EARLY_STATE_RECURRENT_X008_SEED5_ROUGH_Z002_GATE_CPU.md

task:
  rough_terrain_backlash

terrain_hfield_z_scale:
  0.002

bridge:
  corrected fitted

seed:
  5

status:
  HOLD_CANDIDATE_FALL_OR_TERMINATION

samples:
  48

mean_vx:
  -0.3137 m/s

track_ratio:
  -3.9218

max velocity excess:
  1.5672 rad/s

max tracking p95:
  0.2205 rad
```

## Decision

Do not promote this recurrent student and do not continue recurrence-only
training on the same aggregate as the next step.

The result does not prove recurrence is useless in general; it proves that this
small recurrent fit to the current seed-5 aggregate does not fix the early
seed-5 rough-terrain failure. Combined with the contact-phase hold, the next
branch should create a recovery teacher/relabel pass that changes seed 5's
first contact transition before the negative-velocity/fall mode begins.

Robot validation remains blocked.
