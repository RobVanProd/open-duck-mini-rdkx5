# Phase 2 Stage-A2 Gain099 Seed-5 Terrain Boundary z=0.00255 Short Decision

status: `HOLD_Z00255_NOT_A_SUPPORT_SOURCE`

This is an offline terrain-boundary probe. It did not run robot tests, SSH,
deploy, grounded replay, training, or runtime behavior changes.

## Purpose

After `z=0.0027` failed the seed-5 short support gate, this probe checked the
midpoint between the current passing source height (`z=0.0024`) and the failed
height (`z=0.0027`).

## Inputs

- candidate: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- seed: `5`
- terrain hfield z scale: `0.00255`
- duration: `2s`
- platform: CPU closed-loop eval

## Results

| command | status | samples | mean vx | base height min | max tracking p95 | p95 vel excess | max vel excess |
|---|---|---:|---:|---:|---:|---:|---:|
| `x=0.0` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 62 | `-0.2393` | `0.0640` | `0.1921` | `0.0000` | `0.0000` |
| `x=0.08` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 58 | `-0.2618` | `0.0593` | `0.1879` | `0.0000` | `1.3401` |

The `x=0.08` probe exceeded the corrected right-ankle max target-velocity
limit by `1.3401 rad/s`.

## Decision

Do not use `z=0.00255` as a positive support source for seed 5. It fails the
short support gate before two seconds in both command modes.

The terrain source boundary is now very narrow:

```text
z=0.00240: seed-5 x=0.08 passes 15s and source traces are BC-ready
z=0.00255: seed-5 x=0.0 and x=0.08 fail before 2s
z=0.00270: seed-5 x=0.0 and x=0.08 fail before 2s
```

This suggests the current Phase A2 candidate has almost no remaining roughness
margin beyond the accepted z=0.0024 source. Further source mining should either
probe a smaller increment just above `z=0.0024` or switch to training a support
source at low terrain increments instead of treating `z=0.00255+` rollouts as
positive labels.

Robot validation remains blocked.
