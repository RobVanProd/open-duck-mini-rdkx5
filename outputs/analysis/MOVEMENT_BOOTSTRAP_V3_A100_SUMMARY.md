# Movement Bootstrap V3 A100 Summary

status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`

## Executive Summary

`movement_bootstrap_v3` completed all three A100 training phases, including the
final fitted-actuator bridge phase, but the exported candidate failed the
no-command candidate gate. It fell/terminated during a short `x=0.0` fitted
bridge eval, so it must not be deployed or tested on the robot.

The useful result is negative: the command-window progress curriculum did not
produce a safe baseline posture under the fitted actuator bridge. The next
training iteration should first recover stable `x=0.0` behavior before checking
`x=0.08` forward progress.

## Artifact

- artifact bundle sha256:
  `b9d0a05403e332b78531ceedcedbf2393159f3139d1a864bd4016bca89d9ba07`
- final candidate ONNX sha256:
  `85e2e29d1539edba991576583cad1869fec2f80e0d4fc0b7c0cd499018a2964d`
- final candidate source:
  `03_phase3_window_progress_fitted_bridge/.../2026_06_23_170932_430080.onnx`
- robot touched: `false`

## Training Phases

| phase | bridge | steps | result | final reward |
|---|---|---:|---|---:|
| phase 1 | none | 460800 | `PASS_SMOKE_RUN` | 9.0392 |
| phase 2 | mild | 368640 | `PASS_SMOKE_RUN` | 11.7001 |
| phase 3 | fitted | 430080 | `PASS_SMOKE_RUN` | 11.1587 |

## Candidate Gate

Short local CPU gate:

```text
command_x = 0.0
duration = 5.0 s requested
bridge_mode = fitted
jax_platform = cpu
samples = 79
termination = fall_or_nan
overall_status = HOLD_CANDIDATE_FALL_OR_TERMINATION
```

| metric | value | threshold |
|---|---:|---:|
| max action saturation | 0.0000% | 1.0000% |
| max pitch tracking p95 | 0.1190 rad | 0.0800 rad |
| max sent target velocity p95 | 3.2419 rad/s | 2.5000 rad/s |
| body pitch p95 | 1.1393 rad | 0.2500 rad |
| min base height | 0.0298 m | 0.1200 m |
| reward mean | 0.4029 | 0.3000 |

Pitch-chain p95 tracking in the failed x0 gate:

| joint | sent vel p95 | applied vel p95 | bridge tracking p95 | joint tracking p95 | lag |
|---|---:|---:|---:|---:|---:|
| left_hip_pitch | 2.3728 | 2.0407 | 0.1065 | 0.0925 | 4 ticks |
| left_knee | 3.2419 | 2.0140 | 0.0974 | 0.1184 | 3 ticks |
| left_ankle | 1.9780 | 1.4093 | 0.1026 | 0.0854 | 3 ticks |
| right_hip_pitch | 2.2346 | 1.6732 | 0.0685 | 0.1117 | 3 ticks |
| right_knee | 3.1838 | 1.5769 | 0.0856 | 0.1190 | 3 ticks |
| right_ankle | 2.0888 | 1.5153 | 0.0841 | 0.1009 | 4 ticks |

## Interpretation

The v3 candidate is more active than the earlier standstill candidates, but it
is not stable at zero command under the fitted actuator bridge. Because `x=0.0`
failed, `x=0.08` was not run for this candidate.

## Next Action

Train the next candidate with a two-gate curriculum:

1. First enforce stable `x=0.0` under fitted bridge.
2. Then reintroduce command-window progress for `x=0.04-0.12`.

Do not deploy this candidate. Do not run robot validation.
