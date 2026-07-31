# Phase 2 Iter3 Rate180 Gentle-Push Decision

status: `HOLD_PHASE2_RATE180_GENTLE_PUSH_TARGET_VELOCITY`
generated_at: `2026-07-03T20:09:01Z`

Offline-only robustness screen. No robot test, SSH, deploy, grounded replay,
runtime behavior change, or training was performed.

## Candidate

- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate180_20260703/candidate.onnx`
- ONNX sha256: `b658c3380d1ad3dbd8912c988a3ff0e4b019735f220cf56351e9c783f328d5b1`
- baseline no-push gates: `PASS_PHASE2_RATE180_CORRECTED_BRIDGE_GATES`

## Gentle-Push Screen

- command: `x=0.08`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0026`
- reset mode: `home-support`
- bridge: corrected-knee fitted bridge
- duration: `15s`
- seeds: `0-7`
- push interval: `1.0-1.5s`
- push magnitude: `0.05-0.1`
- push recovery window: `0.5s`

Result:

| metric | value |
|---|---:|
| runs | 8 |
| falls | 0 |
| duration complete | 8 |
| pass seeds | 6 |
| target-velocity hold seeds | 2 |
| mean track ratio | 0.4448 |
| mean vx | 0.0356 m/s |
| mean body pitch p95 | 0.1391 rad |
| base height min | 0.1522 m |
| max pitch vel p95 mean | 1.7761 rad/s |
| p95 velocity excess mean | 0.0000 rad/s |
| max velocity excess mean | 0.0366 rad/s |
| max velocity excess observed | 0.1611 rad/s |
| max tracking p95 mean | 0.1866 rad |
| mean push success | 0.9704 |

Per-seed target-velocity holds:

| seed | status | track ratio | max vel excess | push success |
|---:|---|---:|---:|---:|
| 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 0.4538 | 0.1319 | 1.0000 |
| 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 0.4349 | 0.1611 | 0.9231 |

## Decision

The rate180 candidate is a valid no-push offline candidate but is not yet
gentle-push robust at z=0.0026. The failure is narrow: all seeds stayed upright
and moved, but push perturbations produced strict max target-rate excess on two
seeds. Next training/eval should target push-time per-joint max-rate margin
without reducing the no-push gait into standstill.
