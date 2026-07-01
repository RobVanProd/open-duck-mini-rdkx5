# Phase 2 A2 Seed-5 z=0.005 Composite Recovery BC Smoke Decision

status: `HOLD_COMPOSITE_RECOVERY_BC_CLOSED_LOOP_UNSTABLE`

This is an offline supervised smoke and short sim gate. It did not run PPO,
SSH, deploy, run robot tests, grounded replay, or change runtime behavior.

## Fit

The phase-modulated BC student fit the tiny composite support/recovery manifest
cleanly:

| metric | value |
|---|---:|
| samples | 141 |
| MAE | `0.002018` |
| p95 abs error | `0.005435` |
| target-rate p95 | `0.7387 rad/s` |
| target-rate max | `1.8693 rad/s` |
| ONNX p95 error | `0.00000012` |
| ONNX sha256 | `c9fcbc0617628d0496df332522cf1e9d784ccbe5be51068488ce58c32bc15e94` |

## Short Gate

The fitted ONNX was evaluated on the short seed-5 support gate:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.005
command_x: 0.0
seed: 5
duration: 2s
bridge: corrected fitted
```

Result:

| metric | value |
|---|---:|
| status | `HOLD_CANDIDATE_FALL_OR_TERMINATION` |
| samples | 44 |
| mean vx | `-0.2296 m/s` |
| base height min | `0.1189 m` |
| action saturation max | `65.9091%` |
| max pitch tracking p95 | `0.3727 rad` |
| max sent target p95 | `5.2400 rad/s` |
| corrected velocity excess | `3.2400 rad/s` |

Every pitch-chain joint exceeded its corrected p95 velocity limit. The smoke
student therefore regressed to an over-envelope, high-action closed-loop policy
despite a low offline target-rate metric on the fixed manifest.

## Decision

Do not scale this composite manifest. Do not use this smoke ONNX as a candidate
or a parent policy. Do not run the full 8-seed z=0.005 gate.

This result says the tiny support/recovery dataset is too narrow and does not
define a stable closed-loop policy. The next source must include more
on-policy/live states or use a live-oracle DAgger loop with immediate short-gate
checks, rather than a one-shot fixed BC fit on 141 samples.
