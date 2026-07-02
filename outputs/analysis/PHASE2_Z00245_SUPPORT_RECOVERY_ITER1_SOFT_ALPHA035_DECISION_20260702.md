# Phase 2 z=0.00245 Support Recovery Iter1 Soft-Alpha Decision

status: `HOLD_SOFT_ALPHA_RECOVERY_STILL_OVERDRIVES`

## Summary

Iter1 repeated the z=0.00245 seed-5 recovery DAgger precheck with softer source copying:

- source-vx blend alpha: `0.35`
- vx blend alpha: `0.35`
- BC target-rate scale: `5.0`
- BC target-rate limit: `1.5 rad/s`

The supervised fit became smoother than Iter0, but the closed-loop x=0 seed-5 gate still failed by fall/termination and target-rate saturation. The x=0 hard stop failed, so x=0.08 was not run.

## Inputs

- student: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- teacher_manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- aggregate_dataset_id: `37899aa2d6d1a86a`
- aggregate samples: `6118`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.00245`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- command checked: `x=0.0`
- seed: `5`
- duration: `2.0 s`

## Fit

- candidate: `outputs/analysis/phase2_z00245_support_recovery_dagger_iter1_soft_alpha035_contactphase_rate1p5_bc_candidate/candidate.onnx`
- fit MAE: `0.032898`
- fit p95 abs error: `0.101650`
- fit target-rate p95: `1.318220 rad/s`
- fit target-rate max: `1.735654 rad/s`

## Short Gate

| command_x | status | samples | vx m/s | base min m | pitch vel p95 | p95 excess | max excess | tracking p95 | saturation |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | -0.2423 | 0.0626 | 5.2400 | 3.2400 | 3.2400 | 0.2502 | 38.60% |

## Decision

`HOLD_SOFT_ALPHA_RECOVERY_STILL_OVERDRIVES`

Do not promote this student, do not run x=0.08/full gates, and do not use this ONNX as a parent. Simple source-alpha softening plus stronger BC target-rate regularization is insufficient on the tiny two-trace z=0.00245 recovery set.

This closes the immediate "copy z=0.0024 source onto failed z=0.00245 traces and fit BC" branch. The remaining blocker is not lack of relabel plumbing; it is that the current relabeled recovery action map expresses support recovery through closed-loop saturation. The next branch needs a structurally different recovery target or a larger on-policy curriculum that keeps the corrected envelope active during optimization, not another one-shot BC fit on the same tiny recovery set.

## Artifact Hashes

- DAgger iteration report: `3ab8e6a6a2969105d134e4138301befeff4dacb765f136f5f308695e2173a147`
- aggregate manifest: `b83b4ef1b4021f30a3e3560fab42dae45951bf2f45591ae1154ec483da985bc4`
- BC fit report: `1a7c75e8639ffe6ca30d94ce0314309c206d5d09ba3a98be970308da3c7b4b06`
- BC fit JSON: `2f888ad35762dd4ad03f9b8a745761af533bdad11806e086b455e6a86dcca28d`
- x=0.0 short gate report: `84e81f7960a3167ef072676e1a539073e55ada47185563c88014ae6cfec165c6`
- x=0.0 short gate JSON: `904fd4641f54af04297c458912d622a4e5a53ae94b7fa85894502f6abff3bde7`

No robot tests, SSH, deploy, grounded replay, PPO training, or runtime behavior changes were performed.
