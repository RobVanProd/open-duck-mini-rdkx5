# Phase 2 Rate150 z=0.005 Stronger-Push Screen

status: `HOLD_PHASE2_STRONGER_PUSH_TARGET_VELOCITY`
generated_at: `2026-07-04T01:39:31Z`

Offline-only corrected-bridge robustness screen. No robot test, SSH, deploy,
grounded replay, runtime behavior change, or training was performed.

## Candidate

- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
- ONNX sha256: `e2281adeedd2fa4b0d416fecee17bb960275457a81538cb3f98fe57d0e54eb18`
- parent decision: `outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_DECISION.md`

## Screen

- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.005`
- command_x: `0.08`
- duration_s: `15`
- seeds: `0-7`
- bridge: corrected-knee fitted actuator bridge
- push interval: `1.0-1.5 s`
- push magnitude: `0.10-0.15`

## Result

| metric | value |
|---|---:|
| runs | 8 |
| duration complete | 8 |
| falls | 0 |
| passing seeds | 5 |
| target-velocity holds | 3 |
| track ratio mean | 0.3532 |
| mean local vx | 0.0283 m/s |
| body pitch p95 mean | 0.1536 rad |
| base height min | 0.1529 m |
| max pitch vel p95 | 1.5827 rad/s |
| p95 velocity excess max | 0.0000 rad/s |
| instant velocity excess max | 0.1537 rad/s |
| max tracking p95 | 0.1907 rad |
| push success mean | 0.9704 |
| single support mean | 23.65% |

Per-seed target-velocity holds: `3`, `4`, `7`.

## Decision

The promoted rate150 parent survives the stronger-push screen mechanically:
all seeds complete 15 seconds, no falls occur, push recovery remains high, and
tracking p95 stays under 0.20 rad.

It is not a clean pass for the next robustness rung because three seeds exceed
the corrected actuator envelope on instant target velocity. Treat this as a
bounded robustness hold, not a deployability approval.

Next offline work should either:

- train/refine push recovery without increasing target velocity, or
- test a modest terrain-only escalation separately to determine whether the
  current boundary is push-specific.

Robot validation remains blocked.
