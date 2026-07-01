# Foot-Placement MPC z=0.005 Source Probe Decision

status: `HOLD_FOOT_PLACEMENT_MPC_Z005_SOURCE_NOT_ROBUST`

This is an offline source-generation decision. It did not train, SSH, deploy,
run robot tests, grounded replay, or change runtime behavior.

## Purpose

The Phase 2 z=0.005 source-rebuild gate requires a source that survives the
known hard terrain/support state before another live-oracle DAgger iteration.
The foot-placement MPC teacher was tested as a bounded source candidate because
it explicitly controls stance side, lateral placement, swing-foot reach, and
propulsion timing.

## Tooling Change

`tools/probe_foot_placement_mpc_teacher.py` now supports:

```text
--terrain-hfield-z-scale
```

This is a default-off eval-only hook that uses the same scaled-hfield XML path
mechanism as the closed-loop policy evaluator. Existing probe behavior is
unchanged when the flag is omitted.

Smoke result:

- report: `outputs/analysis/FOOT_PLACEMENT_MPC_Z005_TERRAIN_HOOK_SMOKE.md`
- status: `PASS_FOOT_PLACEMENT_MPC_PROBE_RAN`
- scaled hfield z: `0.005`

## Bounded Probe

- report: `outputs/analysis/FOOT_PLACEMENT_MPC_Z005_SOURCE_PROBE.md`
- score: `outputs/analysis/FOOT_PLACEMENT_MPC_Z005_SOURCE_PROBE_SCORE.md`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.005`
- command: `x=0.08`
- seeds: `0,5`
- duration: `2.0s`
- candidate count: `16`

## Result

The probe ran, but no robust source candidates were found:

| metric | value |
|---|---:|
| robust modes | 0 / 16 |
| seed 0 failures | all candidates low velocity / low displacement / double-support dominated |
| seed 5 failures | all candidates missing a valid scoring window due early fall |
| best aggregate duration complete | 1 / 2 |
| best aggregate mean vx | about `-0.177 m/s` |
| best seed-5 samples before fall | about `43` |
| best seed-5 base height min | about `0.055 m` |

The foot-placement MPC teacher, in this bounded configuration, does not provide
a z=0.005 source suitable for distillation.

## Decision

Do not build a BC manifest from these traces. Do not run live-oracle DAgger
iteration 1 from this source. Do not promote any generated source trace.

This result narrows the source-rebuild problem: the missing source must solve
seed-5 support stability before swing/propulsion can matter. A simple
foot-placement/stance-push controller with rate-limited targets still falls on
seed 5 and barely moves on seed 0.

## Next

The next offline source attempt should target seed-5 support survival first,
with a shorter diagnostic gate before full 8-seed source gating:

```text
rough_terrain_backlash, z=0.005, x=0.08, seed 5
duration_complete >= 2s
base_height_min >= 0.12 m
body_pitch_abs_p95 <= 0.25 rad
no corrected-envelope excess
```

Only after seed 5 survives should the source be expanded to the full 8-seed
z=0.005 source gate.
