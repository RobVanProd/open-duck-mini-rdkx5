# Phase 2 Stage-A2 Gain099 Seed-5 Terrain Boundary z=0.0030 Short Decision

status: `HOLD_Z0030_NOT_A_SUPPORT_SOURCE`

This is an offline terrain-boundary probe. It did not run robot tests, SSH,
deploy, grounded replay, training, or runtime behavior changes.

## Purpose

The z=0.005 recovery-DAGger short gate showed that the current z=0.0024 source
is too far from the failing z=0.005 support state. This probe checked whether
the current Phase A2 gain099 candidate can serve as a closer intermediate
source at `z=0.0030`.

## Inputs

- candidate: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- seed: `5`
- terrain hfield z scale: `0.0030`
- duration: `2s`
- platform: CPU closed-loop eval

## Results

| command | status | samples | mean vx | base height min | max tracking p95 | p95 vel excess | max vel excess |
|---|---|---:|---:|---:|---:|---:|---:|
| `x=0.0` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 60 | `-0.2624` | `0.0502` | `0.1951` | `0.0000` | `0.0000` |
| `x=0.08` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `-0.2731` | `0.0547` | `0.1928` | `0.0000` | `0.1823` |

The `x=0.08` probe also exceeded the corrected right-ankle max target-velocity
limit by `0.1823 rad/s`.

## Decision

Do not use `z=0.0030` as a positive support source for seed 5. It fails the
short support gate before two seconds in both command modes.

The current source boundary is now bracketed:

```text
z=0.0024: seed-5 x=0.08 passes 15s and source traces are BC-ready
z=0.0030: seed-5 x=0.0 and x=0.08 fail before 2s
z=0.0035: seed-5 x=0.08 already known to fail
z=0.0050: seed-5 x=0.0 and x=0.08 fail
```

Next source mining should use a smaller terrain ramp between `z=0.0024` and
`z=0.0030`, with `x=0.0` support survival as a required gate before a trace is
accepted as a positive source.

Robot validation remains blocked.
