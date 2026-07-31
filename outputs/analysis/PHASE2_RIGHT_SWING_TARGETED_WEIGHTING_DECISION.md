# Phase 2 Right-Swing Targeted Weighting Decision

status: `PASS_LOCAL_RIGHT_SWING_TARGETED_DIAGNOSTIC`

This is an offline sim-side analysis. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or robot tuning were performed.

## Context

The previous phase/command-modulated student preserved zero-command behavior but
held on seed-4 swing at x=0.08. Global seed-4 weighting was then closed because:

- x2.5 seed-4 weighting was a near miss but still under-advanced seed 4
- x4.0 seed-4 weighting removed seed-4 swing entirely

The operator's carpet observation was:

```text
the robot was stepping, but not lifting/advancing the foot enough to walk forward
```

That matches the rough sim metric that was failing: seed-4 forward swing range.

## Targeted Change

Instead of weighting the whole seed, only seed-4 right-foot swing ticks were
weighted:

```text
source trace: corrected seed-4 moving trace
contact code: 10
meaning: left foot stance, right foot swing
matched rows: 18 / 250
sample weight: 6.0
```

The manifest used:

- corrected x=0.08 seed-2 trace, unchanged
- corrected x=0.08 seed-4 trace with only right-swing rows weighted
- existing x=0.0 standstill trace

The model was the same phase/command-modulated BC architecture used in the
prior command-conditioning tests.

## Local Rough Gate

Task:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: corrected fitted
duration: 5 s
seeds: 2,4
```

### x=0.08

| seed | status | vx | track ratio | vel excess | tracking p95 | swing segments | rel-x p95 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 2 | `PASS_CANDIDATE_SIM_GATE` | 0.0409 | 0.5114 | 0.0000 | 0.1922 | 6 | 0.0131 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 0.0341 | 0.4269 | 0.0000 | 0.1952 | 2 | 0.0064 |

### x=0.0

| seed | status | vx | vel excess | tracking p95 |
|---:|---|---:|---:|---:|
| 2 | `PASS_CANDIDATE_SIM_GATE` | -0.0013 | 0.0000 | 0.0470 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 0.0032 | 0.0000 | 0.0422 |

## Decision

Targeted right-foot swing-phase sample weighting works on the local
rough-terrain diagnostic.

It fixes the specific failure mode that scalar seed weighting could not fix:

- seed-4 right-foot swing/advance recovered
- x=0.0 command semantics preserved
- corrected velocity envelope preserved
- tracking p95 stayed under `0.20 rad`

## Next Gate

This is not a promoted candidate yet. The next step is a wider offline gate:

```text
x=0.08 rough z=0.002, seeds 0-7
x=0.0 rough z=0.002, seeds 0-7
then canonical corrected-bridge flat/rough gates if the 8-seed diagnostic passes
```

If the eight-seed rough gate fails on another seed, do not revert to global
seed weighting. Inspect the failed seed's contact/foot phase and apply the same
targeted per-phase method.
