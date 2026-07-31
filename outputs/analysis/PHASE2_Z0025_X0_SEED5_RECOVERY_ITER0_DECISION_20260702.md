# Phase 2 z=0.0025 x=0 Seed-5 Recovery Iter0 Decision

status: `HOLD_X0_RECOVERY_RELABEL_REGRESSED`
generated_at: `2026-07-02T07:20:00Z`

This is an offline BC fit and short closed-loop gate decision. It did not run
robot tests, SSH, deploy, grounded replay, PPO training, or runtime behavior
changes.

## Inputs

- parent candidate: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`
- recovery aggregate: `outputs/analysis/phase2_z0025_x0_seed5_recovery_dagger_iter0/live_oracle_dagger_aggregate_manifest.json`
- aggregate dataset id: `e298f7da257048d9`
- aggregate samples: `10643`
- added x=0.08 seed-5 samples: `100`
- added x=0 seed-5 samples: `43`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0025`

## Fit

Artifact:

```text
outputs/analysis/PHASE2_Z0025_X0_SEED5_RECOVERY_ITER0_CONTACTPHASE_RATE1P9_BC_FIT.md
outputs/analysis/phase2_z0025_x0_seed5_recovery_iter0_contactphase_rate1p9_bc_fit.json
```

Candidate export:

```text
outputs/analysis/phase2_z0025_x0_seed5_recovery_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx
```

Hashes:

```text
candidate.onnx:    22240402037ded563d17ee983c2222d1d399f869bc238b6eb544710aaf5a33bb
candidate_mlp.npz: efdec700da9574a307f163e030614d9e0f02c10e847e5fba18b7ae5c09ca130a
```

Fit metrics:

| metric | value |
|---|---:|
| MAE | `0.015163` |
| p95 abs error | `0.046152` |
| max abs error | `0.691525` |
| target-rate p95 | `1.585077 rad/s` |
| target-rate max | `2.048853 rad/s` |
| ONNX p95 error | `0.00000012` |

The fit/export smoke passed, but supervised fit quality is weaker than the
parent z=0.0025 boundary candidate.

## Short Closed-Loop Gates

### x=0.0 seed 5

Artifact:

```text
outputs/analysis/PHASE2_Z0025_X0_SEED5_RECOVERY_ITER0_SHORT_X000_GATE_CPU.md
outputs/analysis/phase2_z0025_x0_seed5_recovery_iter0_short_x000_gate_cpu.json
```

Result:

| metric | value |
|---|---:|
| status | `HOLD_CANDIDATE_FALL_OR_TERMINATION` |
| samples | `43` |
| termination | `fall_or_nan` |
| mean local vx | `-0.3553 m/s` |
| base height min | `0.0542 m` |
| max tracking p95 | `0.2234 rad` |
| p95 velocity excess | `0.0000` |

### x=0.08 seed 5

Artifact:

```text
outputs/analysis/PHASE2_Z0025_X0_SEED5_RECOVERY_ITER0_SHORT_X008_GATE_CPU.md
outputs/analysis/phase2_z0025_x0_seed5_recovery_iter0_short_x008_gate_cpu.json
```

Result:

| metric | value |
|---|---:|
| status | `HOLD_CANDIDATE_FALL_OR_TERMINATION` |
| samples | `53` |
| termination | `fall_or_nan` |
| mean local vx | `-0.2666 m/s` |
| track ratio | `-3.3326` |
| base height min | `0.0756 m` |
| max tracking p95 | `0.2117 rad` |
| max velocity excess | `0.5586 rad/s` |

## Decision

```text
HOLD_X0_RECOVERY_RELABEL_REGRESSED
```

The simple zero-action live-oracle recovery relabel did not repair seed-5
zero-command support and also regressed the short positive-command seed-5 gate.
Do not promote this candidate. Do not use this ONNX as a parent.

Interpretation:

- The x=0 seed-5 failure is not solved by adding the 43 pre-collapse failure
  samples with zero-action labels.
- The failure is still a support/collapse mechanism, not a p95 corrected-envelope
  excess.
- The next repair needs a stronger support source or targeted seed-5 support
  stabilizer, not another identical zero-action relabel pass.

No robot, SSH, deploy, grounded replay, or runtime behavior change is
authorized by this decision.
