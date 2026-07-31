# Phase 2 z=0.005 Terrain Failure Trace Decision

status: `HOLD_Z005_TERRAIN_FAILURE_TRACE_DIAGNOSED`

This is an offline sim/eval result only. No robot test, SSH, deploy,
grounded replay, tuning, training, or runtime behavior change was performed.

## Candidate

- candidate: `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx`
- candidate_sha256: `6ba399528c6bc7543e0a5a3a43c30b0804357a4b98e21d723cbb5188e446b2a2`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- prior z=0.005 gate: `outputs/analysis/PHASE2_Z005_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_NOPUSH_DECISION_20260701.md`
- trace gate artifact: `outputs/analysis/PHASE2_Z005_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_FAILURE_TRACE_X008.md`
- trace JSON: `outputs/analysis/phase2_z005_command_gated_bestrec70_rate1p9_targetlimited0999_failure_trace_x008.json`
- trace_json_sha256: `d4fd0f0f2674aa422fb73c3772e609fdc286e17fd4b2c1957705b8bf80b9d1ff`

## Trace Setup

- command_x: `0.08`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.005`
- bridge_mode: `fitted`
- duration: `15 s`
- seeds traced: `1, 5`
- push: disabled
- JAX platform: `cpu`

These are the two seeds that failed the full z=0.005 no-push gate.

## Seed 1: Late Forward / Lateral / Pitch Collapse

- samples: `711`
- final time: `14.20 s`
- termination: `fall_or_nan`
- mean local vx: `0.0565 m/s`
- final-window local vx mean: `0.7270 m/s`
- track ratio: `0.7064`
- base height start/end/min: `0.1565 / 0.0045 / 0.0045 m`
- body pitch min/max/end: `-0.0082 / 1.4844 / 1.4844 rad`
- base displacement x/y: `+0.4209 / +0.3816 m`
- contact occupancy: double support `74.40%`, left-only `9.00%`, right-only `16.32%`, no contact `0.28%`

Pitch-chain sent target velocity remained under the corrected envelope:

| joint | p95 rad/s | max rad/s |
|---|---:|---:|
| left_hip_pitch | 1.5341 | 1.8843 |
| left_knee | 1.8973 | 2.0310 |
| left_ankle | 1.8183 | 1.9548 |
| right_hip_pitch | 1.6944 | 2.0411 |
| right_knee | 1.9245 | 2.0817 |
| right_ankle | 1.7935 | 1.9980 |

Interpretation: seed 1 is not a no-progress failure and not an actuator-envelope
failure. It moves forward on z=0.005 terrain, accumulates large lateral drift, then
collapses late with a forward pitch/base-height failure near the end of the run.

## Seed 5: Early Reverse / Pitch-Back Support Collapse

- samples: `57`
- final time: `1.12 s`
- termination: `fall_or_nan`
- mean local vx: `-0.2711 m/s`
- final-window local vx mean: `-0.7278 m/s`
- track ratio: `-3.3886`
- base height start/end/min: `0.1499 / 0.0594 / 0.0594 m`
- body pitch min/max/end: `-1.4357 / -0.0042 / -1.3745 rad`
- base displacement x/y: `+0.1605 / +0.1408 m`
- contact occupancy: double support `82.46%`, left-only `8.77%`, right-only `0.00%`, no contact `8.77%`

Pitch-chain sent target velocity also remained under the corrected envelope:

| joint | p95 rad/s | max rad/s |
|---|---:|---:|
| left_hip_pitch | 1.5511 | 2.4975 |
| left_knee | 1.9136 | 2.0265 |
| left_ankle | 1.5700 | 2.0990 |
| right_hip_pitch | 1.2538 | 1.4769 |
| right_knee | 1.2939 | 1.4912 |
| right_ankle | 1.5501 | 1.9980 |

Interpretation: seed 5 is an early rough-terrain support/recovery failure. It
falls backward with strong reverse velocity and base-height collapse within
`1.12 s`. This is a different failure surface than seed 1.

## Decision

The z=0.005 hold is not caused by corrected-bridge target velocity excess. Both
failing traces stay inside the corrected pitch-chain envelope. The next Phase 2
blocker is terrain support and stability on rougher height fields:

- seed 1: late forward/lateral drift followed by pitch-forward and base-height collapse
- seed 5: early reverse/pitch-back support collapse

The next training branch should target z=0.005 terrain stability, lateral drift,
base-height preservation, and pitch recovery while preserving:

- z=0.0025 rough terrain pass
- z=0.0025 stronger-push pass
- x=0.0 command semantics
- corrected-envelope target velocity gate

Do not spend the next iteration on more target limiting or push recovery alone;
the target-rate and push gates are already passing at z=0.0025, and these
z=0.005 failures occur without target-rate excess.

## Warm-Start Note

The current best candidate is a composed deployable ONNX wrapper. It is not, by
itself, a raw PPO checkpoint. Any z=0.005 training branch must explicitly choose
one of these warm-start paths:

1. restore from a trainable parent checkpoint that produced the ONNX branch, or
2. use the current ONNX as a teacher/behavior prior for distillation or DAgger.

Do not claim direct PPO restore from this composed ONNX unless that conversion
path has been implemented and verified.

## CI Note

The GitHub `Validate` run for commit `c7f3053` failed before exposing any job
steps or logs. `gh run view 28542735902 --log` returned `log not found` for the
`Static Checks` job. Local artifact validation succeeded for the trace JSON.
