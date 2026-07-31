# Phase 2 Transition-Protected Seed-4 Weighting Decision

status: `HOLD_SEED_WEIGHTING_REINTRODUCES_TRACKING_EXCESS`

## Scope

Offline-only diagnostic follow-up to the transition-protected relabeling
partial pass. No robot tests, SSH, deploy, grounded replay, runtime behavior
changes, or training from scratch were performed.

## Method

The previous transition-protected BC student cleared tracking/envelope on both
rough-terrain seeds but held on seed 4 swing. This test applied a simple
per-entry sample weight:

```text
seed_002 weight: 1.0
seed_004 weight: 3.0
```

The goal was to test whether seed 4 was merely underweighted.

## Results

```text
artifact: outputs/analysis/PHASE2_TRANSITION_PROTECTED_SEED4_WEIGHTED_BC_STUDENT_TERRAIN_Z002_GATE_CPU.md
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: corrected fitted
command_x: 0.08
duration: 5 s
seeds: 2,4
```

Per-seed gate:

```text
seed 2: HOLD_CANDIDATE_TRACKING
  vx: 0.0409 m/s
  track ratio: 0.5112
  max velocity excess: 0.2465 rad/s
  max tracking p95: 0.2202 rad
  single support: 29.2%
  min swing segments: 7

seed 4: HOLD_CANDIDATE_TRACKING
  vx: 0.0335 m/s
  track ratio: 0.4184
  max velocity excess: 0.2935 rad/s
  max tracking p95: 0.2222 rad
  single support: 21.2%
  min swing segments: 6
```

## Interpretation

Simple seed-4 weighting improves swing/advance on both seeds, but it
reintroduces the corrected-envelope and tracking failure that the
transition-protected relabeling had just fixed.

This means seed 4 was not merely underweighted. The remaining branch needs a
more selective correction: preserve the extra swing/advance while keeping the
transition-protected rate envelope.

## Decision

Do not continue naive seed weighting. The next offline branch should use
contact-phase-balanced labels or an explicit action-space correction that:

```text
keeps: seed-weighted swing/advance gains
rejects: pitch-chain labels that reintroduce tracking p95 > 0.20 or velocity excess > 0
gate: same rough_terrain_backlash z=0.002 seeds 2,4
```

Robot validation remains blocked.
