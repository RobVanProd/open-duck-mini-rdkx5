# Phase 2 Phase/Command Seed-4 Weighting Decision

status: `HOLD_SCALAR_SEED4_WEIGHTING_EXHAUSTED`

This is an offline sim-side analysis. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or tuning on the robot were performed.

## Context

The operator reported two hardware surfaces after the corrected-knee run:

- office-chair plastic mat: too slippery
- medium carpet: the robot stepped, but did not lift/advance the foot enough
  to walk forward

That observation matches the current rough-terrain sim blocker. The best
command-conditioned student is not failing from falls, target-rate excess, or
actuator tracking. It is failing because seed 4 lacks enough swing/advance.

## Tested Variants

Both variants used the same phase/command-modulated BC architecture and the
same command manifest:

- x=0.08 corrected action-space labels
- x=0.0 standstill labels
- context indices: `obs[6]`, `obs[99]`, `obs[100]`
- corrected fitted actuator bridge
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.002`

The only changed variable was the scalar sample weight on seed-4 moving labels.

## Results

| variant | command | seed | status | vx | track ratio | vel excess | tracking p95 | swing segments | rel-x p95 |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| seed4x25 | x=0.08 | 2 | `PASS_CANDIDATE_SIM_GATE` | 0.0352 | 0.4405 | 0.0000 | 0.1881 | 4 | 0.0048 |
| seed4x25 | x=0.08 | 4 | `HOLD_CANDIDATE_TERRAIN_SWING` | 0.0329 | 0.4108 | 0.0000 | 0.1887 | 3 | 0.0029 |
| seed4x25 | x=0.0 | 2 | `PASS_CANDIDATE_SIM_GATE` | -0.0015 | NA | 0.0000 | 0.0500 | 1 | 0.0051 |
| seed4x25 | x=0.0 | 4 | `PASS_CANDIDATE_SIM_GATE` | 0.0026 | NA | 0.0000 | 0.0471 | 0 | 0.0000 |
| seed4x40 | x=0.08 | 2 | `PASS_CANDIDATE_SIM_GATE` | 0.0394 | 0.4923 | 0.0000 | 0.1873 | 4 | 0.0136 |
| seed4x40 | x=0.08 | 4 | `HOLD_CANDIDATE_TERRAIN_SWING` | 0.0306 | 0.3829 | 0.0000 | 0.1940 | 0 | 0.0000 |

## Decision

Scalar seed-4 weighting is closed.

The x2.5 variant is a useful near miss:

- zero corrected-envelope excess
- tracking p95 below `0.20 rad`
- seed 4 has three swing segments
- x=0.0 command semantics are preserved

But it still misses the rough-terrain swing gate because seed-4 forward swing
range is `0.0029 m` against the `0.0030 m` threshold.

The x4.0 variant proves that more scalar seed-4 weighting is not the fix. It
improves seed 2 swing/track ratio but removes seed-4 swing entirely.

## Next Branch

Use a targeted command/phase/contact-conditioned correction, not another scalar
weight sweep. The next candidate should preserve:

- x=0.0 mean `|vx| <= 0.005 m/s`
- zero corrected-envelope excess
- tracking p95 under `0.20 rad`

and should specifically recover seed-4 right-foot swing/advance at x=0.08 on
rough `z=0.002`.

Reasonable next mechanisms:

- right-foot swing-phase label weighting only during seed-4 moving windows
- contact/phase-conditioned head or modulation path
- relabel only the seed-4 right-foot swing-advance ticks, not the whole seed

Do not rerun global seed weighting, scalar target-rate penalties, or plain
mixed-command feed-forward BC for this blocker.
