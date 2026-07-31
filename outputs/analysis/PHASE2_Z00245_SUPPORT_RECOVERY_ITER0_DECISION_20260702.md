# Phase 2 z=0.00245 Support Recovery Iter0 Decision

status: `HOLD_RECOVERY_ITER0_OVERDRIVES`

## Summary

A small live-oracle DAgger recovery iteration was run from the Phase A2 gain099 candidate on the first failing z=0.00245 seed-5 support cases. The iteration successfully produced relabeled data from the corrected z=0.0024 source manifest and fit a contact/phase-modulated BC student, but the closed-loop student is not usable.

The student shifts the failure mode from immediate reverse collapse to aggressive over-driving:

- x=0.0 survives 2 seconds, but drifts forward and hits the target-rate ceiling.
- x=0.08 lunges forward, falls, and also hits the target-rate ceiling.

This is not an in-envelope support recovery.

## Inputs

- student: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- teacher_manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- teacher_dataset_id: `d8498b665c201936`
- aggregate_dataset_id: `e7d73116381edf7d`
- aggregate samples: `6118`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.00245`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- commands: `x=0.0`, `x=0.08`
- seed: `5`
- duration: `2.0 s`

## Fit

- candidate: `outputs/analysis/phase2_z00245_support_recovery_dagger_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`
- manifest: `outputs/analysis/phase2_z00245_support_recovery_dagger_iter0/live_oracle_dagger_aggregate_manifest.json`
- architecture: contact+phase modulated BC
- context indices: `[6, 97, 98, 99, 100]`
- target-rate scale: `1.5`
- scalar target-rate limit: `1.9 rad/s`
- fit MAE: `0.020502`
- fit p95 abs error: `0.058295`
- fit target-rate p95: `1.634159 rad/s`
- fit target-rate max: `2.111015 rad/s`

## Short Gates

| command_x | status | samples | vx m/s | track ratio | base min m | pitch vel p95 | p95 excess | max excess | tracking p95 | saturation |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | `HOLD_CANDIDATE_ACTION_SATURATION` | 100 | 0.0467 | NA | 0.1389 | 5.2400 | 3.2400 | 3.2400 | 0.2797 | 36.00% |
| 0.08 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 83 | 0.2369 | 2.9615 | 0.0043 | 5.2400 | 3.2147 | 3.2400 | 0.3283 | 73.49% |

## Decision

`HOLD_RECOVERY_ITER0_OVERDRIVES`

Do not promote this student, do not run full 8-seed gates, and do not use this ONNX as a parent. The z=0.0024 live-oracle labels can produce enough support action to prevent immediate x=0 collapse, but the current BC fit expresses that recovery by saturating actions and violating the corrected actuator envelope.

The next attempt, if authorized, must constrain recovery labels or the student more strongly before closed-loop use. A useful next bounded variant would reduce copied recovery aggression rather than increase data volume: lower blend/source-vx alpha, stricter target-rate regularization, or explicit clipping of relabeled recovery targets before BC.

## Artifact Hashes

- DAgger iteration report: `4c8528045cdb67441064eab7bb112cb1a723e0e85e7aa81441360655d5c6ba41`
- aggregate manifest: `1aa18701741ef1d9f5f7b92f63419c14074207b0ce919ac006504bc6030b439b`
- BC fit report: `d358bf6b4ccb54f534ab1e9f1880faecc188693ba679b36d68a3144cd25828f2`
- BC fit JSON: `df79d66fd0ac79b853194cd6907757faf872f2e8a9c554474aff613ae5a25f5d`
- x=0.0 short gate report: `5e595635c6b51bbacc89b6a58170f70b51c9f0fd79caa4c190f7cab2c996a66b`
- x=0.08 short gate report: `cfd8442af2e428c76b358211ee6608970c5a63921dce21ffd97def704d37897f`

No robot tests, SSH, deploy, grounded replay, PPO training, or runtime behavior changes were performed.
