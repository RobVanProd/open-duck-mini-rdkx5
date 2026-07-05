# Phase 2 Health-Routed Parent Recurrent Decision

status: `HOLD_RECURRENT_BC_UNSTABLE`

## Summary

A stateful recurrent BC student was trained on the health-routed full compact
live-oracle aggregate. The supervised fit/export smoke passed, but the
closed-loop compact gate failed on every seed.

This is an offline diagnostic only. The exported recurrent ONNX requires
explicit hidden-state inputs/outputs and is not deployable to the current robot
runtime.

## Inputs

- aggregate manifest:
  `outputs/analysis/phase2_health_routed_parent_live_compact_iter2/live_oracle_dagger_aggregate_manifest.json`
- dataset id: `3fbfc23526cdaaf6`
- samples: `8550`
- student:
  `outputs/analysis/phase2_health_routed_parent_live_compact_iter2_recurrent_h96_s32/candidate.onnx`
- recurrent contract:
  `obs[1,101], h_in[1,96] -> continuous_actions[1,14], h_out[1,96]`

## Fit

```text
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_LIVE_COMPACT_ITER2_RECURRENT_H96_S32.md
outputs/analysis/phase2_health_routed_parent_live_compact_iter2_recurrent_h96_s32.json
```

Fit status:

```text
PASS_RECURRENT_BC_FIT_SMOKE
```

## Gate

Canonical compact gate:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.0075
bridge: fitted corrected actuator bridge
reset: home-support, settle 10 ticks
pushes: 0.075-0.125 every 1.0-1.5 s
seeds: 0,1,2,6,7
```

Gate result:

```text
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_LIVE_COMPACT_ITER2_RECURRENT_H96_S32_GATE.md
```

Per-seed result:

| seed | status | samples | mean vx | track ratio | p95 velocity excess |
|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 92 | -0.1932 | -2.4153 | 3.2400 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 101 | -0.1653 | -2.0657 | 3.2400 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 94 | -0.1694 | -2.1178 | 3.2400 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 103 | -0.1600 | -2.0002 | 3.2400 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 96 | -0.1862 | -2.3276 | 3.2400 |

Distribution:

```text
passes: 0/5
falls: 5/5
mean samples: 97.2
mean track ratio: -2.1853
mean vx: -0.1748 m/s
p95 corrected velocity excess: 3.2400 rad/s
```

## Decision

Plain recurrent BC on the health-routed live aggregate is worse than the static
phase-modulated parent. It immediately leaves the corrected actuator envelope
and falls backward on every compact seed.

Do not continue supervised-only recurrent BC tweaks on this aggregate.

## Next

The remaining useful directions are:

1. a frame/history wrapper that preserves the static parent action scale while
   adding only bounded correction, or
2. a true online router/mixture wrapper that keeps the already-passing
   branch-specific policies intact, then a later distillation path.

Phase 2 domain-randomized training remains blocked until a single trainable or
explicitly wrapped parent clears the compact behavior-preservation gate.
