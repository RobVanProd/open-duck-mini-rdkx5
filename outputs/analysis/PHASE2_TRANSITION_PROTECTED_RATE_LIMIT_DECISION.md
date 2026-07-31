# Phase 2 Transition-Protected Rate-Limit Decision

status: `PARTIAL_PASS_TRACKING_PLATEAU_BROKEN_HOLD_SEED4_SWING`

## Scope

Offline-only transition-aware relabeling experiment for the Phase 2
rough-terrain branch.

No robot tests, SSH, deploy, grounded replay, runtime behavior changes, or
training from scratch were performed.

## Method

The previous global pitch-chain label-rate cap erased the support transition.
This experiment protected:

```text
non-double-support samples: protected
samples within 6 ticks of a foot-contact transition: protected
rate-limited joints: pitch chain
cap: 2.25 rad/s
```

Only sustained double-support labels away from transitions were eligible for
rate limiting.

## Label Curation Result

```text
artifact: outputs/analysis/PHASE2_TRANSITION_PROTECTED_RATE_LIMIT.md
status: PASS_TRANSITION_PROTECTED_RATE_LIMIT_READY
traces: 2
samples: 500
protected samples: 488
changed ticks: 13
changed contact counts: {'11': 13}
```

The curated manifest kept the original support-transition contact mix while
bringing the trace-level diagnostic metrics inside the rough-terrain envelope:

```text
artifact: outputs/analysis/PHASE2_TRANSITION_PROTECTED_RATE_LIMIT_MANIFEST.md
seed 2 vx: 0.0397 m/s, sent_vel95 2.1964 rad/s, tracking p95 0.1703 rad
seed 4 vx: 0.0459 m/s, sent_vel95 2.0583 rad/s, tracking p95 0.1665 rad
```

## Student Fit

```text
artifact: outputs/analysis/PHASE2_TRANSITION_PROTECTED_RATE_LIMIT_BC_STUDENT.md
status: PASS_PPO_LOC_BC_FIT_SMOKE
samples: 500
p95 action error: 0.022175
supervised target-rate p95: 2.206232 rad/s
```

## Rough-Terrain Gate

```text
artifact: outputs/analysis/PHASE2_TRANSITION_PROTECTED_RATE_LIMIT_BC_STUDENT_TERRAIN_Z002_GATE_CPU.md
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: corrected fitted
command_x: 0.08
duration: 5 s
seeds: 2,4
```

Results:

```text
seed 2: PASS_CANDIDATE_SIM_GATE
  vx: 0.0291 m/s
  track ratio: 0.3641
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1876 rad
  single support: 22.8%
  min swing segments: 2
  min rel-x range p95: 0.0039 m

seed 4: HOLD_CANDIDATE_TERRAIN_SWING
  vx: 0.0255 m/s
  track ratio: 0.3184
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1914 rad
  single support: 10.8%
  min swing segments: 0
  min rel-x range p95: 0.0000 m
```

## Interpretation

This breaks the previous tracking/envelope plateau on the rough-terrain
diagnostic gate: both seeds completed, both had zero corrected-envelope excess,
and both had tracking p95 under `0.20 rad`.

It is not a deployable pass. Seed 4 still fails the hard swing/advance gate,
with too much double support and no per-foot rel-x range. The next branch should
target seed-4 swing preservation/advance specifically, not return to global
label smoothing or scalar reward PPO.

## Decision

Proceed to a seed-balanced transition-preserving correction:

```text
keep: transition-protected rate limiting
add: seed-4 swing/advance weighting or contact-phase-balanced labels
gate: rough_terrain_backlash z=0.002 seeds 2,4, same corrected bridge
stop if: tracking/envelope regresses or seed 4 remains without swing segments
```

Robot validation remains blocked.
