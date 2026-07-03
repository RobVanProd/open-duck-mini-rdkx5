# Phase 2 Iter2 Right-Ankle Limit198 Rate165 Candidate Decision

status: `PASS_OFFLINE_CORRECTED_BRIDGE_CANDIDATE_READY`

## Summary

The surgical right-ankle label clamp at `1.98 rad/s` produced a deployable
ONNX candidate that clears both corrected-bridge gates:

- `x=0.08`: `8/8` pass, zero corrected p95 velocity excess, zero corrected
  max velocity excess.
- `x=0.0`: `8/8` pass, near-zero velocity, zero corrected velocity excess.

This candidate is slower than the previous rate165 baseline, but it is strict
envelope-clean and preserves nonzero single support.

No robot test, SSH, deploy, grounded replay, PPO/domain-randomization training,
or runtime behavior change was performed.

## Candidate

Promoted candidate directory:

```text
policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703
```

Files:

```text
policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/candidate.onnx
policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/candidate_mlp.npz
policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/SHA256SUMS
```

Hashes:

- ONNX:
  `eacc7c69e517b7cef32daeedeb6b110cd766e129183b071a7254f6fa0af5c1e2`
- NPZ:
  `053accd4d916c6ec0286ff1a4eadea3b285af4c8381b27689f39b10fcfbaa5ec`

## Lineage

Base live-oracle aggregate:

```text
outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_plan/live_oracle_dagger_aggregate_manifest.json
```

Right-ankle label clamp:

```text
outputs/analysis/PHASE2_ITER2_RIGHT_ANKLE_LIMIT198_TRACE_LIMIT.md
outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json
```

Student fit:

```text
outputs/analysis/PHASE2_ITER2_RIGHT_ANKLE_LIMIT198_RATE165_STUDENT.md
outputs/analysis/phase2_iter2_right_ankle_limit198_rate165_student.json
```

Fit metrics:

- samples: `28500`
- p95 action error: `0.020872`
- target-rate p95: recorded in fit artifact
- ONNX max abs error: `0.0000002086`

## x=0.08 Corrected Gate

Gate artifact:

```text
outputs/analysis/PHASE2_ITER2_RIGHT_ANKLE_LIMIT198_RATE165_STUDENT_X008_GATE.md
outputs/analysis/phase2_iter2_right_ankle_limit198_rate165_student_x008_gate.json
```

Result:

- status: `PASS_CANDIDATE_SIM_GATE`
- duration complete: `8/8`
- falls: `0/8`
- mean local vx: `0.0262 m/s`
- track ratio: `0.3269`
- single support: `25.2000%`
- double support: `74.8000%`
- max pitch-chain p95 velocity: `1.7502 rad/s`
- corrected p95 velocity excess: `0.0000 rad/s`
- corrected max velocity excess: `0.0000 rad/s`
- max tracking p95: `0.1892 rad`

## x=0.0 Corrected Gate

Gate artifact:

```text
outputs/analysis/PHASE2_ITER2_RIGHT_ANKLE_LIMIT198_RATE165_STUDENT_X0_GATE.md
outputs/analysis/phase2_iter2_right_ankle_limit198_rate165_student_x0_gate.json
```

Result:

- status: `PASS_CANDIDATE_SIM_GATE`
- duration complete: `8/8`
- falls: `0/8`
- mean local vx: `0.0001 m/s`
- single support: `0.0000%`
- double support: `100.0000%`
- max pitch-chain p95 velocity: `0.0561 rad/s`
- corrected p95 velocity excess: `0.0000 rad/s`
- corrected max velocity excess: `0.0000 rad/s`
- max tracking p95: `0.0320 rad`

## Comparison

| metric | previous rate165 baseline | iter2 limit198 |
|---|---:|---:|
| x=0.08 gate | PASS | PASS |
| x=0.08 mean vx | 0.0272 | 0.0262 |
| x=0.08 track ratio | 0.3400 | 0.3269 |
| x=0.08 single support | 22.5333% | 25.2000% |
| x=0.08 max tracking p95 | 0.1827 | 0.1892 |
| x=0.08 max velocity excess | 0.0000 | 0.0000 |
| x=0.0 gate | PASS | PASS |

## Decision

Promote this as the current offline corrected-bridge Phase 2 baseline.

The next offline step is not robot validation. Resume Phase 2 robustness from
this candidate with the corrected bridge and right-ankle max-spike guard
preserved:

1. flat/no-push weak dynamics randomization,
2. full flat physics randomization,
3. gentle pushes,
4. terrain widening.

Every stage must keep zero corrected velocity excess and preserve x=0.0
stillness.

## Scope

Offline sim/evidence only. This decision does not authorize robot validation,
SSH, deployment, grounded replay, or runtime behavior changes.
