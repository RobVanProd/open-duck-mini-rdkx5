# Phase 2 Rate160 z=0.0075 Intermediate-Push Full-8 Decision
status: `HOLD_RATE160_Z0075_INTERMEDIATE_PUSH_TARGET_VELOCITY_LOW_PROGRESS`
## Scope
- Offline sim/eval only.
- No robot tests, SSH, deploy, grounded replay, runtime behavior change, or training were performed.

## Candidate
- policy: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_20260703/candidate.onnx`
- role tested: possible stability/source transfer candidate for the hard Phase 2 boundary.

## Gate
- task: `rough_terrain_backlash`
- command: `x=0.08`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- terrain hfield z scale: `0.0075`
- push magnitude: `0.075-0.125`
- push interval: `1.0-1.5 s`
- reset: `home-support`, settle ticks `10`
- seeds: `0-7`

## Result
| metric | value |
|---|---:|
| runs | 8 |
| duration complete | 8 |
| falls / terminations | 0 |
| mean track ratio | 0.3218 |
| mean vx m/s | 0.0257 |
| max p95 velocity excess rad/s | 0.0000 |
| max instantaneous velocity excess rad/s | 0.1379 |
| max tracking p95 rad | 0.1935 |
| mean push success rate | 0.9704 |

Status counts:

- `HOLD_CANDIDATE_TARGET_VELOCITY`: `7`
- `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`: `1`

## Per-Seed Summary
| seed | status | samples | track_ratio | max_p95_vel | p95_excess | max_excess | tracking_p95 | push_success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3587 | 1.6493 | 0.0000 | 0.0772 | 0.1869 | 0.9167 |
| 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3364 | 1.6456 | 0.0000 | 0.0772 | 0.1935 | 1.0000 |
| 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3754 | 1.6499 | 0.0000 | 0.0772 | 0.1907 | 0.9231 |
| 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.2148 | 1.5597 | 0.0000 | 0.0772 | 0.1622 | 1.0000 |
| 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3205 | 1.6429 | 0.0000 | 0.1379 | 0.1851 | 1.0000 |
| 5 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3530 | 1.6503 | 0.0000 | 0.0772 | 0.1878 | 1.0000 |
| 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.2906 | 1.6715 | 0.0000 | 0.0772 | 0.1859 | 0.9231 |
| 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3250 | 1.6414 | 0.0000 | 0.0772 | 0.1863 | 1.0000 |

## Interpretation
- The candidate is stable for all eight seeds under the hard z=0.0075 intermediate-push screen.
- It is not promotable as a strict Phase 2 source because 7/8 seeds hold on target velocity and 1/8 holds on low forward progress.
- The p95 corrected-envelope excess is zero, but instantaneous corrected-envelope excess is nonzero on every seed, with max 0.1379 rad/s.
- Seed 5 no longer lunges or falls, so this policy may contain useful stabilizing behavior, but using it directly would trade the command-gated source failure for envelope/low-progress holds.
- Do not run x=0.0 promotion gates for this candidate because x=0.08 already fails the strict source gate.

## Next Recommendation
Do not promote rate160. Use this result as evidence that seed-5 stability exists but must be transferred without the instantaneous envelope excess and low-progress regression; next source work should be router/recovery targeted, not broad scalar PPO reward tuning.
