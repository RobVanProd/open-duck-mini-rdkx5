# Phase 2 z0.0075 Iter21 Recurrent Diagnostic H64 Seq32 Rate150

Status: `HOLD_RECURRENT_DIAG_STANDSTILL`

This is a stateful recurrent behavior-cloning diagnostic trained from
`outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_plus_seed2_merged_manifest.json`.
It is not deployable on the current robot runtime because it requires hidden
state inputs and outputs:

`obs[1,101], h_in[1,64] -> continuous_actions[1,14], h_out[1,64]`

## Files

- `candidate.onnx`
- `candidate_rnn.npz`
- student report: `outputs/analysis/PHASE2_Z0075_ITER21_RECURRENT_DIAG_H64_SEQ32_RATE150_STUDENT.md`
- compact screen: `outputs/analysis/PHASE2_Z0075_ITER21_RECURRENT_DIAG_H64_SEQ32_RATE150_X008_SEED0_1_2_6_7_SCREEN.md`
- decision: `outputs/analysis/PHASE2_Z0075_ITER21_RECURRENT_DIAG_H64_SEQ32_RATE150_DECISION.md`

## Hashes

- candidate ONNX sha256: `3a53e4d77007d52ded2723a123ed29cae037744396089f03d18fe79f04b5d293`
- student NPZ sha256: `7fbba4104c4f7f4b271ce6c418eb898a03f278941b0faf7f409d37efeaca6acc`
- source manifest sha256: `3398b064c7454faae25d046c630450b4060e3dca58251d0e9c709adfb99029fa`

## Compact Screen

| seed | status | samples | track_ratio | single_support | double_support |
|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0106 | 0.0000 | 100.0000 |
| 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0118 | 0.0000 | 100.0000 |
| 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0113 | 0.0000 | 100.0000 |
| 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0104 | 0.0000 | 100.0000 |
| 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0106 | 0.0000 | 100.0000 |

## Decision

Do not promote. This diagnostic shows that explicit hidden state alone does not
solve the compact gate when trained by static BC on the current manifest. The
next branch should use live-oracle DAgger on student-visited states.
