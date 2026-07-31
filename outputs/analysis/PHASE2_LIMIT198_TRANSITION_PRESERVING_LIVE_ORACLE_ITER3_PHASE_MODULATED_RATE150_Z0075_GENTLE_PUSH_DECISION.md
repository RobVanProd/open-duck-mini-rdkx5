# Phase 2 Rate150 z=0.0075 Gentle-Push Screen

status: `PASS_PHASE2_Z0075_GENTLE_PUSH`
generated_at: `2026-07-04T03:32:05Z`

Offline-only corrected-bridge combined terrain + gentle-push screen. No robot
test, SSH, deploy, grounded replay, runtime behavior change, or training was
performed.

## Candidate

- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
- ONNX sha256: `e2281adeedd2fa4b0d416fecee17bb960275457a81538cb3f98fe57d0e54eb18`
- parent decision: `outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_DECISION.md`

## Gate Summary

Both gates used `rough_terrain_backlash`, `home-support` reset, fitted
corrected-knee actuator bridge, CPU evaluator, 15s duration, z=0.0075 terrain,
gentle push magnitude 0.05-0.10, and seeds 0-7.

| gate | status | falls | track ratio | mean vx | max pitch vel p95 | instant vel excess | max tracking p95 | push success |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| x=0.08 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 0 | 0.3518 | 0.0281 | 1.5757 | 0.0000 | 0.1891 | 0.9704 |
| x=0.0 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 0 | NA | 0.0008 | 0.0749 | 0.0000 | 0.0422 | 0.9704 |

## Decision

The promoted rate150 parent clears combined z=0.0075 terrain plus gentle-push
robustness while preserving command conditioning and the corrected actuator
envelope.

This refines the current Phase 2 boundary:

- z=0.0075 terrain-only: `PASS`
- z=0.0075 gentle-push magnitude 0.05-0.10: `PASS`
- z=0.005 stronger push magnitude 0.10-0.15: `HOLD_PHASE2_STRONGER_PUSH_TARGET_VELOCITY`

The next offline stage should target push-recovery robustness without
increasing target velocity, or screen a smaller intermediate push step before
training. Robot validation remains blocked.
