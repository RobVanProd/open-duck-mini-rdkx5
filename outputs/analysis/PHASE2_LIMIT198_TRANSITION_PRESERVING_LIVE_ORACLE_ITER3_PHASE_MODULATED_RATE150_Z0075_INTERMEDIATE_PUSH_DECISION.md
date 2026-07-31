# Phase 2 Rate150 z=0.0075 Intermediate-Push Decision

status: `HOLD_PHASE2_Z0075_INTERMEDIATE_PUSH_STABILITY`

## Summary

The rate150 corrected-bridge candidate remains valid through the previously
recorded z=0.0075 gentle-push gate, but the intermediate push bracket is not
promotable.

This screen used:

- policy: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain height scale: `0.0075`
- command: `x=0.08`
- push magnitude: `0.075`-`0.125`
- push interval: `1.0`-`1.5` s
- seeds: `0-7`
- platform: CPU

## Result

| metric | value |
|---|---:|
| runs | 8 |
| duration complete | 6 |
| falls / terminations | 2 |
| mean track ratio | 0.5622 |
| mean local vx | 0.0450 m/s |
| max pitch-chain p95 sent velocity | 1.5960 rad/s |
| max p95 velocity excess | 0.0000 rad/s |
| max instantaneous velocity excess | 1.3268 rad/s |
| max tracking p95 | 0.2007 rad |
| mean push success | 0.9808 |

Per-seed outcome:

| seed | status | termination | samples | track ratio | max velocity excess |
|---:|---|---|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `fall_or_nan` | 181 | 1.5887 | 1.3268 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | `duration_complete` | 750 | 0.3864 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | `duration_complete` | 750 | 0.3784 | 0.0000 |
| 3 | `PASS_CANDIDATE_SIM_GATE` | `duration_complete` | 750 | 0.4195 | 0.0000 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | `duration_complete` | 750 | 0.3520 | 0.0000 |
| 5 | `PASS_CANDIDATE_SIM_GATE` | `duration_complete` | 750 | 0.2969 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | `duration_complete` | 750 | 0.3515 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `fall_or_nan` | 550 | 0.7245 | 0.4477 |

## Interpretation

This is a near-boundary hold. The candidate does not broadly violate the p95
corrected actuator envelope under intermediate pushes, and six seeds complete
the full horizon. The hold is stability-driven: seeds 0 and 7 terminate under
the push/terrain combination, with seed 0 also showing a large instantaneous
velocity excursion.

The current robustness boundary is therefore:

- `PASS`: z=0.0075 terrain with gentle push magnitude `0.05`-`0.10`.
- `HOLD`: z=0.0075 terrain with intermediate push magnitude `0.075`-`0.125`.
- `HOLD`: z=0.005 terrain with stronger push magnitude `0.10`-`0.15`.

No robot test, SSH, deployment, runtime behavior change, grounded replay, or
training was performed.

## Next Recommendation

Do not promote this intermediate-push result. Treat it as a measured robustness
boundary and use it to target the next offline refinement at seed-0/seed-7 push
stability without loosening the corrected actuator envelope.
