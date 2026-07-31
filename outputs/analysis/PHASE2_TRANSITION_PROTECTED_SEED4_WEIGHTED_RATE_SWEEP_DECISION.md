# Phase 2 Seed-4 Weighted Rate Sweep Decision

status: `HOLD_RATE_REGULARIZATION_SWING_TRACKING_TRADEOFF`

## Scope

Offline-only diagnostic sweep after the seed-4 weighted student restored
swing/advance but reintroduced corrected-envelope and tracking excess.

No robot tests, SSH, deploy, grounded replay, runtime behavior changes, or
training from scratch were performed.

## Method

Same weighted manifest and PPO-loc BC architecture as the seed-4 weighting
test:

```text
seed_002 weight: 1.0
seed_004 weight: 3.0
hidden sizes: 512,256,128
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: corrected fitted
command_x: 0.08
duration: 5 s
seeds: 2,4
```

Only the supervised target-rate penalty was changed:

```text
rate008: target_rate_scale 0.08
rate02:  target_rate_scale 0.20
```

## Gate Results

### target_rate_scale 0.08

```text
artifact: outputs/analysis/PHASE2_TRANSITION_PROTECTED_SEED4_WEIGHTED_RATE008_BC_STUDENT_TERRAIN_Z002_GATE_CPU.md
seed 2/4 status: HOLD_CANDIDATE_TRACKING / HOLD_CANDIDATE_TRACKING
seed 2/4 track ratio: 0.4459 / 0.3588
seed 2/4 max velocity excess: 0.0822 / 0.1252 rad/s
seed 2/4 max tracking p95: 0.2024 / 0.2067 rad
seed 2/4 min swing segments: 7 / 0
```

### target_rate_scale 0.20

```text
artifact: outputs/analysis/PHASE2_TRANSITION_PROTECTED_SEED4_WEIGHTED_RATE02_BC_STUDENT_TERRAIN_Z002_GATE_CPU.md
seed 2/4 status: HOLD_CANDIDATE_TRACKING / HOLD_CANDIDATE_TRACKING
seed 2/4 track ratio: 0.3842 / 0.3107
seed 2/4 max velocity excess: 0.0314 / 0.0943 rad/s
seed 2/4 max tracking p95: 0.2083 / 0.2113 rad
seed 2/4 min swing segments: 4 / 0
```

## Interpretation

Rate regularization reduces velocity excess, but it also erodes the seed-4
swing/advance that naive weighting recovered. The sweep remains on the same
tradeoff curve:

```text
transition-protected labels: pass tracking/envelope, weak seed-4 swing
seed-4 weighting: good swing, tracking/envelope excess
seed-4 weighting + rate penalty: less excess, seed-4 swing regresses
```

This closes the simple sample-weight plus scalar rate-penalty family.

## Decision

Do not continue scalar supervised rate sweeps on the same manifest. The next
offline branch needs a more selective correction, such as:

```text
contact-phase-balanced labels
per-contact/per-joint action-space correction
explicit replacement of only the pitch-chain components that cause excess
while preserving swing-driving components
```

Robot validation remains blocked.
