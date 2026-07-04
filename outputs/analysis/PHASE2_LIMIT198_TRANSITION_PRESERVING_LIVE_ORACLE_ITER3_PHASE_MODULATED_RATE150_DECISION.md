# Phase 2 Iter3 Phase-Modulated Rate150 Decision

status: `PASS_PHASE2_RATE150_Z005_SUPPORT_WITH_REGRESSIONS`
generated_at: `2026-07-03T23:48:00Z`

Offline-only corrected-bridge support and regression gates. No robot test, SSH,
deploy, grounded replay, runtime behavior change, or PPO training was
performed.

## Candidate

- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
- ONNX sha256: `e2281adeedd2fa4b0d416fecee17bb960275457a81538cb3f98fe57d0e54eb18`
- NPZ: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/student.npz`
- NPZ sha256: `eed75a10ddea007697eabd9494e613f190cf8cb2687ff20ae1e03a77e3649b74`
- contract: `obs[1,101] -> continuous_actions[1,14]`

## Gate Summary

All gates used `rough_terrain_backlash`, `home-support` reset, fitted
corrected-knee actuator bridge, CPU evaluator, 15s duration, and seeds 0-7.

| gate | status | z | push | falls | track ratio | mean vx | max pitch vel p95 | max vel excess | max tracking p95 | push success |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| x=0.08 no-push | `PASS_CANDIDATE_SIM_GATE` | 0.0050 | false | 0 | 0.3715 | 0.0297 | 1.5402 | 0.0000 | 0.1838 | NA |
| x=0.0 no-push | `PASS_CANDIDATE_SIM_GATE` | 0.0050 | false | 0 | NA | 0.0005 | 0.0290 | 0.0000 | 0.0345 | NA |
| x=0.08 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 0.0050 | true | 0 | 0.3829 | 0.0306 | 1.5647 | 0.0000 | 0.1890 | 0.9704 |
| x=0.0 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 0.0050 | true | 0 | NA | 0.0005 | 0.0657 | 0.0000 | 0.0402 | 0.9704 |
| x=0.08 no-push regression | `PASS_CANDIDATE_SIM_GATE` | 0.0026 | false | 0 | 0.3787 | 0.0303 | 1.5517 | 0.0000 | 0.1888 | NA |
| x=0.0 no-push regression | `PASS_CANDIDATE_SIM_GATE` | 0.0026 | false | 0 | NA | 0.0001 | 0.0357 | 0.0000 | 0.0328 | NA |
| x=0.08 gentle-push regression | `PASS_CANDIDATE_SIM_GATE` | 0.0026 | true | 0 | 0.3806 | 0.0304 | 1.5513 | 0.0000 | 0.1892 | 0.9704 |
| x=0.0 gentle-push regression | `PASS_CANDIDATE_SIM_GATE` | 0.0026 | true | 0 | NA | 0.0002 | 0.1094 | 0.0000 | 0.0374 | 0.9704 |

## Decision

Promote `rate150` as the current offline Phase 2 terrain-support candidate.
It resolves the `rate160` z=0.005 max target-velocity hold while preserving
the z=0.0026 no-push and gentle-push regression gates. It also clears the
z=0.005 gentle-push pair directly. The tradeoff is slower forward speed than
the original Phase 1 candidate, but it stays in the corrected actuator envelope
across the current support/regression set.

Robot validation remains blocked. The next offline stage should decide whether
to increase terrain/push difficulty or broaden domain randomization from this
`rate150` parent.
