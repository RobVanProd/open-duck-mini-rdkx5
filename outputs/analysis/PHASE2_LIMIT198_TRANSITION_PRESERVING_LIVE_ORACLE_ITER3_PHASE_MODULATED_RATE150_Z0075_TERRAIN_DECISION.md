# Phase 2 Rate150 z=0.0075 Terrain Screen

status: `PASS_PHASE2_Z0075_TERRAIN_NO_PUSH`
generated_at: `2026-07-04T02:46:05Z`

Offline-only corrected-bridge terrain escalation screen. No robot test, SSH,
deploy, grounded replay, runtime behavior change, or training was performed.

## Candidate

- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
- ONNX sha256: `e2281adeedd2fa4b0d416fecee17bb960275457a81538cb3f98fe57d0e54eb18`
- parent decision: `outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_DECISION.md`

## Gate Summary

Both gates used `rough_terrain_backlash`, `home-support` reset, fitted
corrected-knee actuator bridge, CPU evaluator, 15s duration, z=0.0075 terrain,
and seeds 0-7.

| gate | status | falls | track ratio | mean vx | max pitch vel p95 | instant vel excess | max tracking p95 | single support |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| x=0.08 no-push | `PASS_CANDIDATE_SIM_GATE` | 0 | 0.3824 | 0.0306 | 1.5548 | 0.0000 | 0.1872 | 25.60 |
| x=0.0 no-push | `PASS_CANDIDATE_SIM_GATE` | 0 | NA | 0.0008 | 0.0266 | 0.0000 | 0.0366 | 0.00 |

## Checker Note

The zero-command companion originally reported `HOLD_CANDIDATE_TERRAIN_SWING`
because the optional terrain-swing checker treated missing swing metrics as a
failure even when the requested thresholds were explicitly zero. That was a
checker semantics bug for x=0.0: a standing zero-command policy should not be
required to produce swing segments.

`tools/run_candidate_seed_sweep.py` now treats missing swing metrics as zero
when the configured swing threshold is non-positive. The z=0.0075 x=0.0 screen
was rerun after that fix and passes 8/8.

## Decision

The promoted rate150 parent clears the modest terrain-only escalation to
z=0.0075 while preserving command conditioning and the corrected actuator
envelope.

This separates the current Phase 2 boundary:

- terrain-only z=0.0075: `PASS`
- z=0.005 stronger push magnitude 0.10-0.15: `HOLD_PHASE2_STRONGER_PUSH_TARGET_VELOCITY`

The next offline work should focus on push-recovery robustness without raising
target velocity, or run a paired z=0.0075 gentle-push screen to test combined
terrain-plus-gentle-push before any stronger push training.

Robot validation remains blocked.
