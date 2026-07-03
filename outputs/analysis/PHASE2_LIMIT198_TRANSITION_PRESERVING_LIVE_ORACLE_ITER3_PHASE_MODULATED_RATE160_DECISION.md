# Phase 2 Iter3 Phase-Modulated Rate160 Decision

status: `PASS_PHASE2_RATE160_GENTLE_PUSH_GATES`
generated_at: `2026-07-03T21:20:26Z`

Offline-only behavior-cloning fit and corrected-bridge seed gates. No robot
test, SSH, deploy, grounded replay, runtime behavior change, or PPO training was
performed.

## Candidate

- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_20260703/candidate.onnx`
- ONNX sha256: `870242baa5f12555f4595479d74289256a0200d9733f58c63ca161203fa5bb06`
- NPZ: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_20260703/student.npz`
- NPZ sha256: `c3e930600f8cd8245a4c44166a9b435462720b562295071e276f0a81587eba9d`
- source manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- contract: `obs[1,101] -> continuous_actions[1,14]`

## Fit

| metric | value |
|---|---:|
| samples | 40500 |
| action MAE | 0.008420 |
| action p95 abs error | 0.027474 |
| action max abs error | 0.318555 |
| target-rate p95 | 1.382734 rad/s |
| target-rate max | 1.648717 rad/s |
| ONNX verify max abs error | 0.00000024 |

## Corrected-Bridge Gates

All gates used `rough_terrain_backlash`, z=0.0026, `home-support` reset,
fitted corrected-knee actuator bridge, CPU evaluator, 15s duration, and seeds
0-7.

| gate | status | seeds | falls | track ratio | mean vx | max pitch vel p95 | max vel excess | max tracking p95 | support/push |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| x=0.08 no-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.392299 | 0.031384 | 1.607294 | 0.000000 | 0.185876 | 25.33% single |
| x=0.08 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | 0.380778 | 0.030462 | 1.634139 | 0.000000 | 0.187862 | 0.9704 push success |
| x=0.0 no-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | NA | 0.000237 | 0.043135 | 0.000000 | 0.033672 | 100.0% double |
| x=0.0 gentle-push | `PASS_CANDIDATE_SIM_GATE` | 8/8 | 0 | NA | 0.000300 | 0.149000 | 0.000000 | 0.036500 | 0.9704 push success |

The gentle-push gate used interval `1.0-1.5s`, magnitude `0.05-0.1`, and a
`0.5s` recovery window. It cleared the two target-velocity holds seen in the
rate180 screen without introducing falls, velocity excess, or zero-command
drift. The zero-command gentle-push symmetry check also passed 8/8 while
remaining in double support with negligible drift.

## Decision

Promote `rate160` as the current Phase 2 offline robustness candidate. The
tradeoff is slower forward speed than `rate180`, but it clears the next staged
robustness screen and preserves zero-command semantics under gentle push. The
next offline step is to continue the staged curriculum toward the next planned
weak randomization/terrain screen. Robot validation remains blocked.
