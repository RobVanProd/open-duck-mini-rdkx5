# Phase 2 Rate150 z=0.005 Gentle-Push Decision

status: `PASS_Z005_GENTLE_PUSH_PAIR`
generated_at: `2026-07-04T00:58:00Z`

Offline-only corrected-bridge z=0.005 gentle-push screen. No robot test, SSH,
deploy, grounded replay, runtime behavior change, or training was performed.

## Candidate

- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
- ONNX sha256: `e2281adeedd2fa4b0d416fecee17bb960275457a81538cb3f98fe57d0e54eb18`
- contract: `obs[1,101] -> continuous_actions[1,14]`

## Gates

Both gates used `rough_terrain_backlash`, z=0.005, `home-support` reset,
fitted corrected-knee actuator bridge, CPU evaluator, 15s duration, seeds 0-7,
gentle pushes every `1.0-1.5s`, push magnitude `0.05-0.1`, and a `0.5s`
recovery window.

| gate | status | seeds | falls | track ratio | mean vx | max pitch vel p95 | max vel excess | max tracking p95 | push success |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| x=0.08 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.3829 | 0.0306 | 1.5647 | 0.0000 | 0.1890 | 0.9704 |
| x=0.0 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | NA | 0.0005 | 0.0657 | 0.0000 | 0.0402 | 0.9704 |

## Decision

`rate150` clears the z=0.005 gentle-push pair directly. The next offline stage
can move beyond this gentle-push terrain screen instead of training a dedicated
z=0.005 gentle-push repair. Robot validation remains blocked.
