# Phase 2 Limit198 Transition-Preserving Iter3 Phase-Modulated Rate150 Candidate

status: `PASS_PHASE2_RATE150_Z005_SUPPORT_WITH_REGRESSIONS`

This is a lower-rate phase/command-modulated student trained from the same
live-oracle iter3 aggregate manifest as `rate160`. It was fit as a targeted
terrain-margin probe after `rate160` stayed upright at z=0.005 but held on max
target-velocity excess.

Contract:

`obs[1,101] -> continuous_actions[1,14]`

This candidate is not a grounded-test authorization. It is the current offline
Phase 2 terrain-support parent after clearing z=0.005 no-push/gentle-push
support and the z=0.0026 no-push/gentle-push regression set.

## Files

- `candidate.onnx`
  - sha256: `e2281adeedd2fa4b0d416fecee17bb960275457a81538cb3f98fe57d0e54eb18`
- `student.npz`
  - sha256: `eed75a10ddea007697eabd9494e613f190cf8cb2687ff20ae1e03a77e3649b74`

## Fit Metrics

- samples: `40500`
- action MAE: `0.008739`
- action p95 abs error: `0.028857`
- action max abs error: `0.316246`
- target-rate p95: `1.364055 rad/s`
- target-rate max: `1.569699 rad/s`
- ONNX verify max abs error: `0.00000021`

## z=0.005 No-Push Gate Pair

Both gates used `rough_terrain_backlash`, z=0.005, `home-support` reset,
corrected-knee fitted actuator bridge, CPU evaluator, 15s duration, and seeds
0-7.

| gate | status | seeds | falls | mean vx | track ratio | max vel excess | max tracking p95 |
|---|---|---:|---:|---:|---:|---:|---:|
| x=0.08 no-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.0297 | 0.3715 | 0.0000 | 0.1838 |
| x=0.0 no-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.0005 | NA | 0.0000 | 0.0345 |
| x=0.08 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.0306 | 0.3829 | 0.0000 | 0.1890 |
| x=0.0 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.0005 | NA | 0.0000 | 0.0402 |

## z=0.0026 Regression Gates

| gate | status | seeds | falls | mean vx | track ratio | max vel excess | max tracking p95 | push success |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| x=0.08 no-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.0303 | 0.3787 | 0.0000 | 0.1888 | NA |
| x=0.0 no-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.0001 | NA | 0.0000 | 0.0328 | NA |
| x=0.08 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.0304 | 0.3806 | 0.0000 | 0.1892 | 0.9704 |
| x=0.0 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.0002 | NA | 0.0000 | 0.0374 | 0.9704 |

## Source

- manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- fit report: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student_rate150/PHASE_MODULATED_BC_STUDENT.md`
- z=0.005 decision: `outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_Z005_DECISION.md`
- final decision: `outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_DECISION.md`
- z=0.005 gentle-push decision: `outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_Z005_GENTLE_PUSH_DECISION.md`
