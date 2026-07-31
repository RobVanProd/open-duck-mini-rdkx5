# Phase 2 Rate150 z=0.005 Terrain Decision

status: `PASS_Z005_NO_PUSH_PAIR_PENDING_REGRESSION`
generated_at: `2026-07-03T22:42:00Z`

Offline-only corrected-bridge terrain-margin probe. No robot test, SSH,
deploy, grounded replay, runtime behavior change, or PPO training was
performed.

## Candidate

- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
- ONNX sha256: `e2281adeedd2fa4b0d416fecee17bb960275457a81538cb3f98fe57d0e54eb18`
- NPZ sha256: `eed75a10ddea007697eabd9494e613f190cf8cb2687ff20ae1e03a77e3649b74`
- contract: `obs[1,101] -> continuous_actions[1,14]`

## Fit

| metric | value |
|---|---:|
| samples | 40500 |
| action MAE | 0.008739 |
| action p95 abs error | 0.028857 |
| action max abs error | 0.316246 |
| target-rate p95 | 1.364055 rad/s |
| target-rate max | 1.569699 rad/s |
| ONNX verify max abs error | 0.00000021 |

## z=0.005 No-Push Gates

Both gates used `rough_terrain_backlash`, z=0.005, `home-support` reset,
fitted corrected-knee actuator bridge, CPU evaluator, 15s duration, and seeds
0-7.

| gate | status | seeds | falls | track ratio | mean vx | max pitch vel p95 | max vel excess | max tracking p95 | support |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| x=0.08 no-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.3715 | 0.0297 | 1.5402 | 0.0000 | 0.1838 | 23.47% single |
| x=0.0 no-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | NA | 0.0005 | 0.0290 | 0.0000 | 0.0345 | 100.0% double |

## Decision

`rate150` clears the z=0.005 no-push support pair that `rate160` held on. The
change appears to be a target-rate margin fix rather than a new gait: z=0.005
x=0.08 remains slow but stable and in-envelope. Do not promote yet. The next
required step is z=0.0026 regression gating, including the gentle-push screens
that `rate160` cleared.
