# Phase 2 Rate165 Live-Oracle Iter2 Decision

status: `HOLD_ITER2_MAX_VELOCITY_EXCESS`

## Summary

Live-oracle DAgger iteration 2 produced valid relabel data and a deployable
phase/contact-modulated student, but the exported student is not promotable
under the strict corrected-bridge gate.

The result is still useful: compared with the current rate165 baseline, the
iter2 student improves forward motion and single-support time. The rejection is
not a standstill regression; it is a small instantaneous corrected-envelope
violation.

No robot test, SSH, deploy, grounded replay, PPO/domain-randomization training,
or runtime behavior change was performed.

## Data Generation

- iteration artifact:
  `outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_plan/LIVE_ORACLE_DAGGER_ITERATION.md`
- aggregate manifest:
  `outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_plan/live_oracle_dagger_aggregate_manifest.json`
- status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`
- aggregate manifest status: `PASS_FILTERED_BC_MANIFEST_READY`
- kept entries: `38`
- samples: `28500`
- rejected entries: `0`

Inputs:

- previous iter1 aggregate manifest
- `8` x=0.08 student-visited traces relabeled by the live source-VX oracle
- `2` x=0.0 student-visited traces relabeled with zero-action command safety

## Student Fit

- fit artifact:
  `outputs/analysis/PHASE2_RATE165_SINGLE_SUPPORT_LIVE_ORACLE_ITER2_STUDENT.md`
- ONNX:
  `outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_student/candidate.onnx`
- ONNX sha256:
  `c476120f75ea38b16cfe2a1c0eee49adca648811e65691e374321b58372a8cd7`
- NPZ sha256:
  `020cb7737e6a92ed84dd1ab03fa8b7bc725f0c863489a5ac3cbada607d2718b7`
- samples: `28500`
- p95 action error: `0.021781`
- target-rate p95: `1.425471 rad/s`
- target-rate max: `1.893847 rad/s`
- ONNX max abs error: `0.0000002682`

## x=0.08 Corrected Gate

Gate artifact:

```text
outputs/analysis/PHASE2_RATE165_SINGLE_SUPPORT_LIVE_ORACLE_ITER2_STUDENT_X008_GATE.md
outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_student_x008_gate.json
```

Result:

- status: `HOLD_CANDIDATE_TARGET_VELOCITY`
- duration complete: `8/8`
- falls: `0/8`
- mean local vx: `0.0324 m/s`
- track ratio: `0.4047`
- single support: `27.2000%`
- double support: `72.8000%`
- max pitch-chain p95 velocity: `1.7164 rad/s`
- corrected p95 velocity excess: `0.0000 rad/s`
- corrected max velocity excess: `0.0149 rad/s`
- max tracking p95: `0.1859 rad`

Comparison with current rate165 baseline:

| metric | baseline rate165 | iter2 student |
|---|---:|---:|
| status | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_TARGET_VELOCITY` |
| mean local vx | 0.0272 | 0.0324 |
| track ratio | 0.3400 | 0.4047 |
| single support | 22.5333% | 27.2000% |
| max tracking p95 | 0.1827 | 0.1859 |
| p95 velocity excess | 0.0000 | 0.0000 |
| max velocity excess | 0.0000 | 0.0149 |

## x=0.0 Spot Gate

Gate artifact:

```text
outputs/analysis/PHASE2_RATE165_SINGLE_SUPPORT_LIVE_ORACLE_ITER2_STUDENT_X0_SPOT_GATE.md
outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_student_x0_spot_gate.json
```

Result:

- status: `PASS_CANDIDATE_SIM_GATE`
- duration complete: `2/2`
- falls: `0/2`
- mean local vx: `0.0000 m/s`
- single support: `0.0000%`
- double support: `100.0000%`
- corrected p95 velocity excess: `0.0000 rad/s`
- corrected max velocity excess: `0.0000 rad/s`
- max tracking p95: `0.0315 rad`

This confirms the first iter2 fit preserves zero-command stillness in the
spot check. It does not override the x=0.08 strict-gate hold.

## Decision

Do not promote the iter2 student.

Keep the existing corrected rate165 candidate as the offline baseline:

```text
policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/candidate.onnx
```

The next offline attempt should preserve the iter2 motion gain while restoring
zero corrected max velocity excess. Recommended options:

1. Refit from the same iter2 aggregate manifest with a tighter target-rate
   setting, then re-run the strict x=0.08 gate.
2. Add an explicit max-velocity guard to the supervised fit so p95 remains
   clean and instantaneous spikes also stay inside the corrected envelope.
3. Do not resume scalar PPO/domain randomization until a student passes the
   corrected bridge while preserving nonzero single support.

## Scope

Offline sim/evidence only. This decision does not authorize robot validation,
SSH, deployment, grounded replay, or runtime behavior changes.
