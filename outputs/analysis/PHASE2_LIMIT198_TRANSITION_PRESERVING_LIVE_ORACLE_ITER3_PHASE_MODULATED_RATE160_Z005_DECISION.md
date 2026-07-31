# Phase 2 Rate160 z=0.005 Terrain Decision

status: `HOLD_PHASE2_RATE160_Z005_TARGET_VELOCITY`
generated_at: `2026-07-03T22:09:16Z`

Offline-only corrected-bridge terrain gate. No robot test, SSH, deploy,
grounded replay, runtime behavior change, or training was performed.

## Candidate

- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_20260703/candidate.onnx`
- ONNX sha256: `870242baa5f12555f4595479d74289256a0200d9733f58c63ca161203fa5bb06`
- contract: `obs[1,101] -> continuous_actions[1,14]`

## Gate

- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.005`
- reset_mode: `home-support`
- command_x: `0.08`
- bridge: corrected-knee fitted actuator bridge
- duration: `15s`
- seeds: `0-7`
- push: disabled

| metric | value |
|---|---:|
| gate status | `HOLD_CANDIDATE_TARGET_VELOCITY` |
| runs | 8 |
| duration complete | 8 |
| falls | 0 |
| track ratio mean | 0.3729 |
| mean vx | 0.0298 m/s |
| body pitch p95 mean | 0.1494 rad |
| base height min mean | 0.1529 m |
| max pitch vel p95 | 1.6210 rad/s |
| p95 velocity excess | 0.0000 rad/s |
| max velocity excess | 0.4799 rad/s |
| max tracking p95 | 0.1837 rad |
| min swing peak lift | 0.0135 m |
| min swing segments | 16 |
| single support | 25.3333% |

## Decision

Do not promote `rate160` to the z=0.005 terrain rung. The candidate remains
stable and keeps moving on z=0.005, but all eight seeds hold on corrected
target-velocity excess. The next offline training/refinement target is terrain
support at z=0.005 that preserves the rate160 gait while removing the max
velocity excess. Do not advance to z=0.005 push, stronger terrain, or robot
validation from this result.
