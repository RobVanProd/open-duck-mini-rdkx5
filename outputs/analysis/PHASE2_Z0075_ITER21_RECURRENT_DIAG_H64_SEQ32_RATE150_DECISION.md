# Phase 2 z0.0075 Iter21 Recurrent Diagnostic H64 Seq32 Rate150 Decision

status: `HOLD_RECURRENT_DIAG_STANDSTILL`

## Context

The deployable history-context phase-modulated student preserved seeds 0, 1, 2,
and 6, but seed7 still regressed into reverse/fall. This diagnostic tested
whether explicit recurrent state, trained on the same current merged manifest,
would break that sensitive-seed plateau.

This candidate is not deployable on the current robot runtime because it exports
a stateful ONNX contract:

```text
inputs:  obs[1,101], h_in[1,64]
outputs: continuous_actions[1,14], h_out[1,64]
```

No robot tests, SSH, deploy, runtime behavior changes, grounded replay, or PPO
training were performed.

## Candidate

- path: `policy/candidates/phase2_z0075_iter21_recurrent_diag_h64_seq32_rate150_20260704/candidate.onnx`
- ONNX sha256: `3a53e4d77007d52ded2723a123ed29cae037744396089f03d18fe79f04b5d293`
- NPZ sha256: `7fbba4104c4f7f4b271ce6c418eb898a03f278941b0faf7f409d37efeaca6acc`
- source manifest: `outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_plus_seed2_merged_manifest.json`
- source manifest sha256: `3398b064c7454faae25d046c630450b4060e3dca58251d0e9c709adfb99029fa`
- screen JSON sha256: `53602e4179eaf87c6a79fa20849c777fb92d4a62c73047babd2f75d89984394f`
- training status: `PASS_RECURRENT_BC_FIT_SMOKE`
- ONNX max action error: `0.00000029`
- ONNX max hidden error: `0.00000074`

## Fit Metrics

- sequences: `98`
- samples: `53834`
- hidden dim: `64`
- sequence length: `32`
- MAE: `0.012817`
- p95 abs error: `0.040449`
- target-rate p95: `1.338052 rad/s`
- target-rate max: `9.128114 rad/s`

## Compact Screen

Corrected-bridge screen:

- command: `x=0.08`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0075`
- bridge: `fitted`
- reset: `home-support`, settle `10` ticks
- pushes: enabled, `0.075-0.125`, interval `1.0-1.5 s`
- seeds: `0,1,2,6,7`

| seed | status | samples | termination | track_ratio | mean_local_vx | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | single_support | double_support |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0106 | 0.0009 | 0.0672 | 0.1612 | 0.0772 | 0.0420 | 0.0000 | 100.0000 |
| 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0118 | 0.0009 | 0.0723 | 0.1607 | 0.0768 | 0.0430 | 0.0000 | 100.0000 |
| 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0113 | 0.0009 | 0.0684 | 0.1613 | 0.0784 | 0.0433 | 0.0000 | 100.0000 |
| 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0104 | 0.0008 | 0.0732 | 0.1611 | 0.0773 | 0.0424 | 0.0000 | 100.0000 |
| 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0106 | 0.0008 | 0.0694 | 0.1611 | 0.0754 | 0.0411 | 0.0000 | 100.0000 |

## Interpretation

The recurrent/stateful student did not recover the sensitive-seed distribution.
It completed all five rollouts but collapsed into a stable standstill:

- mean track ratio: `0.0109`
- mean local vx: `0.0009 m/s`
- single support: `0.0%`
- double support: `100.0%`
- corrected velocity excess: `0.0`

This is not a seed7-specific instability fix. It is a conservative low-action
solution learned from the same static BC manifest. Explicit hidden state alone
is therefore not sufficient when trained by static behavior cloning on the
current data.

## Decision

Do not promote this candidate and do not run x=0.0 or robot validation.

The next useful branch should be the actual live-oracle DAgger loop: roll out
the current student, query the source-VX selector on the student-visited states,
aggregate those labels, and retrain. The evidence now says the static manifest
is the bottleneck for both deployable feed-forward and diagnostic recurrent
students.
