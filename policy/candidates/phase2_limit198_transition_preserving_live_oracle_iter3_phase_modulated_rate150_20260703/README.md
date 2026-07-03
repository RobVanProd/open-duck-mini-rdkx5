# Phase 2 Limit198 Transition-Preserving Iter3 Phase-Modulated Rate150 Candidate

status: `PASS_Z005_NO_PUSH_PAIR_PENDING_REGRESSION`

This is a lower-rate phase/command-modulated student trained from the same
live-oracle iter3 aggregate manifest as `rate160`. It was fit as a targeted
terrain-margin probe after `rate160` stayed upright at z=0.005 but held on max
target-velocity excess.

Contract:

`obs[1,101] -> continuous_actions[1,14]`

This candidate is not a grounded-test authorization. It still requires the
z=0.0026 regression gates before any Phase 2 promotion.

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

## Source

- manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- fit report: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student_rate150/PHASE_MODULATED_BC_STUDENT.md`
- decision: `outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_Z005_DECISION.md`
