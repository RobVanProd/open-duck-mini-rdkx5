# Phase 2 Health-Routed Parent Live-Correction Decision

status: `HOLD_STATIC_PHASE_MODULATED_LIVE_CORRECTION`

## Summary

The health-routed behavior still does not compress into the current static
phase-modulated BC parent, even after live-oracle relabeling on the student's
own visited states.

This is offline-only analysis. No robot test, SSH, deploy, grounded replay, or
runtime behavior change was performed.

## Inputs

- initial static parent:
  `outputs/analysis/phase2_health_routed_parent_phase_modulated/candidate.onnx`
- routed source manifest:
  `outputs/analysis/phase2_health_routed_parent_manifest.json`
- corrected actuator bridge:
  `outputs/analysis/actuator_response_fit_corrected_knee.json`
- compact gate:
  `rough_terrain_backlash`, z-scale `0.0075`, fitted bridge, home-support
  reset, settle `10`, intermediate pushes, seeds `0,1,2,6,7`

## Prior Static Parent

The first phase-modulated parent fit the routed labels and improved over the
PPO-loc parent, but still failed seed `7`:

```text
PASS: seeds 0,1,2,6
HOLD: seed 7, fall_or_nan at 300 samples, track ratio -0.5236
```

Gate result:

```text
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_PHASE_MODULATED_GATE.md
```

## Focused Seed-7 Live Correction

One bounded live-oracle correction iteration was run only on the failing seed
`7`, plus one zero-command correction trace:

```text
outputs/analysis/phase2_health_routed_parent_live_seed7_iter1/
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_LIVE_SEED7_ITER1_PHASE_MODULATED_GATE.md
```

Result:

```text
PASS: seeds 0,2,6
HOLD: seed 1, seed 7
```

Seed `7` improved from a `300` sample reverse fall to a `502` sample positive
motion fall, but seed `1` regressed into an early lunge/fall. This showed that
single-seed relabeling traded one failure surface for another.

## Full Compact Live Correction

A second live-oracle correction iteration relabeled the current student's own
visited states for all compact x=0.08 seeds and two x=0.0 seeds:

```text
outputs/analysis/phase2_health_routed_parent_live_compact_iter2/
```

Aggregate manifest:

```text
status: PASS_FILTERED_BC_MANIFEST_READY
dataset_id: 3fbfc23526cdaaf6
entries: 12
samples: 8550
```

The resulting phase-modulated parent fit smoke passed:

```text
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_LIVE_COMPACT_ITER2_PHASE_MODULATED.md
```

But the compact gate regressed:

```text
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_LIVE_COMPACT_ITER2_PHASE_MODULATED_GATE.md
```

Per-seed result:

| seed | status | samples | mean vx | track ratio | base height min |
|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 675 | 0.0567 | 0.7081 | -0.0065 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 471 | -0.0078 | -0.0977 | 0.0702 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0305 | 0.3817 | 0.1585 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0296 | 0.3695 | 0.1587 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 296 | -0.0402 | -0.5019 | 0.0695 |

Distribution:

```text
passes: 2/5
falls: 3/5
mean track ratio: 0.1719
mean vx: 0.0138 m/s
corrected velocity excess: 0.0
```

## Decision

Static phase-modulated BC is not sufficient for this routed behavior. Live
student-state relabeling is useful data, but when compressed back into the same
static parent class it either trades failures across seeds or regresses the
compact distribution.

Do not launch Phase 2 domain-randomized training from any of these static
parents.

## Next Branch

Escalate representation rather than adding more static relabel weight tweaks:

```text
1. frame-stacked feed-forward student
2. recurrent/hidden-state student if frame stacking fails
3. online parallel-prefix/router wrapper only as an eval tool, not as the final
   deployable policy
```

The next artifact should test whether a small amount of observation history can
represent the seed-7 recovery branch without regressing seeds `0` and `1`.
