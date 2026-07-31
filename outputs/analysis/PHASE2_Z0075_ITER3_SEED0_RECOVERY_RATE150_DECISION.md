# Phase 2 z=0.0075 Live-Oracle Iter3 Seed-0 Recovery Rate150 Decision

status: `HOLD_ITER3_DAGGER_DATA_DID_NOT_TRANSFER`

This is an offline-only decision record. No robot tests, SSH, deploy,
grounded replay, runtime behavior changes, or PPO training were performed.

## Candidate

- candidate: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_rate150_20260704/candidate.onnx`
- candidate_sha256: `c809fe2e784371f2a8c4c3f39507a6ed3efd02b1bea33e1aaf56401537f93151`
- student_npz: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_rate150_20260704/student.npz`
- student_npz_sha256: `d07c036211b0e213c638660c95aa531d8b4270dafac4885e590c462910a52e17`
- training_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_aggregate_manifest.json`
- dataset_id: `ddbeda5b717074b6`
- samples: `51175`

## Fit

- status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- MAE: `0.009558`
- p95 abs error: `0.028781`
- max abs error: `0.403406`
- target-rate p95: `1.369416 rad/s`
- target-rate p99: `1.729787 rad/s`
- target-rate max: `4.487093 rad/s`
- ONNX p95 error: `0.00000012`
- ONNX max error: `0.00000024`

## Compact Screen

Configuration:

- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0075`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- bridge_mode: `fitted`
- reset_mode: `home-support`
- push interval: `1.0-1.5 s`
- push magnitude: `0.075-0.125`
- duration: `15.0 s`
- platform: `cpu`

### x=0.08

Result: `HOLD`

| seed | status | samples | mean vx | track ratio | body pitch p95 | base height min | max pitch vel p95 | p95 vel excess | max vel excess | max tracking p95 | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 126 | 0.1657 | 2.0714 | 1.0009 | 0.0037 | 1.8411 | 0.0000 | 0.0000 | 0.2017 | 0.0000 |
| 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0341 | 0.4257 | 0.2034 | 0.1532 | 1.7502 | 0.0000 | 0.0962 | 0.1852 | 0.9000 |

### x=0.0

Result: `PASS`

| seed | status | samples | mean vx | body pitch p95 | base height min | max pitch vel p95 | p95/max vel excess | max tracking p95 | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0010 | 0.0691 | 0.1533 | 0.0271 | 0.0000 / 0.0000 | 0.0421 | 0.9167 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0007 | 0.0539 | 0.1533 | 0.0275 | 0.0000 / 0.0000 | 0.0399 | 0.9231 |

## Interpretation

The iter3 live-oracle recovery data did not transfer into a better deployable
phase-modulated student.

The candidate preserves zero-command semantics under pushed rough-terrain
conditions, but it does not improve the x=0.08 boundary that matters for Phase
2 promotion:

- seed 0 still falls early from a high-forward surge/pitchover pattern;
- seed 7 completes, but regresses from the iter2 pass into a small max
  corrected-envelope excess;
- the failure remains stability/push recovery plus transfer, not broad
  command-conditioning collapse.

Do not promote this candidate. The next branch should not keep adding frozen
DAgger samples to the same phase-modulated feed-forward student unless it also
changes the transfer mechanism that converts seed-0 recovery data into policy
behavior. Candidate next directions are a tighter gate-aware sample weighting
audit around the seed-0 pre-fall window, explicit push-phase/context features,
or the next representation rung from the live-oracle spec.
