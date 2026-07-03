# Phase 2 Iter3 Phase-Modulated Student Decision

status: `HOLD_PHASE_MODULATED_STUDENT_TARGET_VELOCITY`
generated_at: `2026-07-03T18:57:27Z`

Offline-only behavior-cloning fit and partial corrected-bridge screen. No robot
test, SSH, deploy, grounded replay, runtime behavior change, or PPO training was
performed.

## Fit

- manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- samples: `40500`
- model: shared-trunk phase/command-modulated feed-forward BC student
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[128, 128]`
- context hidden sizes: `[32]`
- modulation scale: `0.5`
- activation: `swish`
- steps: `12000`
- target-rate regularizer limit: `1.98 rad/s`
- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_20260703/candidate.onnx`
- ONNX sha256: `0387e8f072cb6e2558b8eeee687331c0d8cae6e548a8a3291c2ab7509f9d0801`
- NPZ sha256: `f42e7714a0abaabc1148b7bcb42d5cd6df5aed4b30538c15fb70a7f542eadf73`

Fit metrics:

| metric | value |
|---|---:|
| action MAE | 0.007389 |
| action p95 abs error | 0.023591 |
| action max abs error | 0.306087 |
| target-rate p95 | 1.375111 rad/s |
| target-rate max | 2.195462 rad/s |
| ONNX verify max abs error | 0.00000021 |

## Partial x=0.08 Gate

The canonical corrected-bridge x=0.08 screen was stopped after three consecutive
seeds held on the same target-velocity condition. All three completed the full
duration and moved, but each exceeded the strict corrected per-joint max-velocity
gate on the right ankle.

| seed | status | duration | track ratio | max pitch p95 | max tracking p95 | right ankle max | limit | excess |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.431762 | 1.765205 | 0.188874 | 2.109346 | 2.000000 | 0.109346 |
| 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.431762 | 1.765205 | 0.188874 | 2.109346 | 2.000000 | 0.109346 |
| 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.431762 | 1.765205 | 0.188874 | 2.109346 | 2.000000 | 0.109346 |

Other gate-relevant values were healthy in the partial screen:

- action saturation: `0.0%`
- p95 velocity excess: `0.0 rad/s`
- body pitch p95: `0.136022 rad`
- base height min: `0.152237 m`
- reward mean: `0.461397`
- min forward command tracking ratio: `0.431762`

## Decision

Do not promote this phase-modulated student. It demonstrates that the iter3
aggregate can be fit into a smooth deployable ONNX, but this feed-forward rung
still leaks a right-ankle peak target-rate spike outside the corrected envelope.

Next step: either tighten the student loss around per-joint max velocity
violations, use transition-aware sample weighting specifically on the right
ankle spike, or move to the next representation rung only after this cheap
feed-forward target-rate leak is addressed.
