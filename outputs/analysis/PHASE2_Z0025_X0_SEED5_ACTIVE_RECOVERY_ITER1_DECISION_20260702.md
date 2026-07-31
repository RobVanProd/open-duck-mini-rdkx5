# Phase 2 z=0.0025 x=0 Seed-5 Active-Recovery Iter1 Decision

status: `HOLD_ACTIVE_RECOVERY_RELABEL_INSUFFICIENT`
generated_at: `2026-07-02T07:50:00Z`

This is an offline live-oracle relabel, BC fit, and short closed-loop gate
decision. It did not run robot tests, SSH, deploy, grounded replay, PPO
training, or runtime behavior changes.

## Inputs

- parent candidate: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`
- active-recovery aggregate: `outputs/analysis/phase2_z0025_x0_seed5_active_recovery_relabel_iter1/live_oracle_dagger_aggregate_manifest.json`
- aggregate dataset id: `f238faf44822ef9f`
- aggregate samples: `10643`
- added x=0.08 seed-5 samples: `100`
- added x=0 seed-5 samples: `43`
- x=0 relabel teacher: `source_vx_blend`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0025`

## Active Relabel Check

Unlike the zero-action iter0 repair, the x=0 seed-5 labels were materially
nonzero:

| label source | samples | mean abs action | max abs action | left hip pitch mean | right hip pitch mean |
|---|---:|---:|---:|---:|---:|
| zero-action iter0 | 43 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| active relabel iter1 | 43 | 0.1289 | 0.4493 | -0.3635 | 0.1944 |
| original student | 43 | 0.0530 | 0.1860 | 0.0085 | -0.0465 |

This was a meaningful test of an active support correction, not a duplicate of
the zero-action relabel.

## Fit

Artifact:

```text
outputs/analysis/PHASE2_Z0025_X0_SEED5_ACTIVE_RECOVERY_ITER1_CONTACTPHASE_RATE1P9_BC_FIT.md
outputs/analysis/phase2_z0025_x0_seed5_active_recovery_iter1_contactphase_rate1p9_bc_fit.json
```

Candidate export:

```text
outputs/analysis/phase2_z0025_x0_seed5_active_recovery_iter1_contactphase_rate1p9_bc_candidate/candidate.onnx
```

Hashes:

```text
candidate.onnx:    6e0535518e4a059bb7fc94393b371c3dddfaa3b85f02e09886d64335d949c859
candidate_mlp.npz: cc153ebf7e6570f2e5935abbebd38063a51bfffe1a1da80a65df0f2e25c41e3e
```

Fit metrics:

| metric | value |
|---|---:|
| MAE | `0.015846` |
| p95 abs error | `0.048198` |
| max abs error | `0.741823` |
| target-rate p95 | `1.577307 rad/s` |
| target-rate max | `2.066789 rad/s` |
| ONNX p95 error | `0.00000012` |

## Short Closed-Loop Gates

| command | status | samples | termination | mean vx | base min | max tracking p95 | max velocity excess |
|---|---|---:|---|---:|---:|---:|---:|
| x=0.0 seed 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 51 | `fall_or_nan` | -0.2824 | 0.0691 | 0.2126 | 0.2064 |
| x=0.08 seed 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 52 | `fall_or_nan` | -0.2748 | 0.0729 | 0.2163 | 3.2400 |

Compared with the zero-action iter0 repair, x=0.0 survival improved from 43 to
51 samples and reverse velocity became less severe. However, it still failed
well before the 2-second short gate. The positive-command short gate regressed
and introduced corrected-envelope velocity excess.

## Decision

```text
HOLD_ACTIVE_RECOVERY_RELABEL_INSUFFICIENT
```

Do not promote this candidate. Do not use this ONNX as a parent.

The source-VX active relabel contains a real recovery action, but a small
supervised patch on 43 unsupported reset-state samples is not enough to produce
a stable seed-5 x=0 support behavior and it damages x=0.08 behavior. The next
repair needs either:

1. more on-policy recovery coverage from unsupported/partial-contact reset
   states, with an explicit preservation gate for x=0.08, or
2. an evaluator/training reset-settlement mechanism that makes x=0.0 and x=0.08
   start from comparable supported states.

No robot, SSH, deploy, grounded replay, or runtime behavior change is
authorized by this decision.
