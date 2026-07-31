# Phase 2 Command-Gated vs Rate160 Seed-5 Stability Decision
status: `PASS_SEED5_STABILITY_PATTERN_IDENTIFIED_NOT_PROMOTABLE`

## Scope
- Offline sim/analysis only.
- No robot tests, SSH, deploy, grounded replay, runtime behavior change, or training were performed.

## Inputs
- failing source trace: `outputs/analysis/phase2_command_gated_zero0020_seed5_failure_trace/command_gated_zero0020/seed_005/trace.jsonl`
- stable hold trace: `outputs/analysis/phase2_rate160_z0075_intermediate_push_seed5_trace/phase_mod_rate160/seed_005/trace.jsonl`
- comparison: `outputs/analysis/phase2_command_gated_vs_rate160_seed5_trace_compare.json`

## Key Result
| metric | command-gated seed5 | rate160 seed5 |
|---|---:|---:|
| samples | 158 | 750 |
| mean vx | 0.1367 | 0.0282 |
| abs pitch p95 | 0.8743 | 0.1777 |
| base height min | -0.0058 | 0.1577 |
| double support pct | 88.6076 | 76.6667 |

Common-window deltas over the first 158 samples:

| metric | rate160 minus command-gated mean | abs delta p95 |
|---|---:|---:|
| vx | -0.1076 | 0.7766 |
| body pitch | -0.1267 | 0.8207 |
| base height | 0.0078 | 0.0435 |

## Interpretation
- Rate160 removes the seed-5 forward-lunge/pitchover failure through the full 15 s horizon.
- The stabilizing pattern appears by about tick 109 for body pitch and tick 145 for base height in the common window.
- The same behavior is too slow and has small instantaneous corrected-envelope excess, so the full rate160 policy is not promotable.
- The next useful source branch is targeted transfer of the seed-5 anti-lunge/stability pattern into the faster command-gated source, with strict envelope checks; broad rate160 routing or scalar PPO reward tuning is not evidence-aligned.

## Next Recommendation
Build a seed-5 anti-lunge/recovery relabel or observation-conditioned wrapper using the rate160 seed-5 stable trace as the teacher/control, then gate only seed5 plus regression-control seeds before any full-8 rerun.
