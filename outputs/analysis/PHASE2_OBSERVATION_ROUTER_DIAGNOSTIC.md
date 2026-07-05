# Phase 2 Observation Router Diagnostic

status: `HOLD_ROUTER_NEAR_MISS`

## Executive Summary

The offline router improves candidate selection but does not cover all compact seeds. Inspect the missed seed before building an online wrapper.

This is offline analysis only. It did not train, SSH, deploy, run robot tests, change runtime behavior, or run grounded replay. Seed ID is not used as a feature.

## Evaluations

| prefix ticks | k | policy onehot scale | pass/total | result |
|---:|---:|---:|---:|---|
| `1` | `3` | `0.0` | `4/5` | `HOLD` |
| `1` | `3` | `1.0` | `4/5` | `HOLD` |
| `1` | `3` | `5.0` | `4/5` | `HOLD` |
| `5` | `3` | `0.0` | `4/5` | `HOLD` |
| `5` | `3` | `1.0` | `4/5` | `HOLD` |
| `5` | `3` | `5.0` | `4/5` | `HOLD` |
| `25` | `3` | `0.0` | `4/5` | `HOLD` |
| `25` | `3` | `1.0` | `4/5` | `HOLD` |
| `25` | `3` | `5.0` | `4/5` | `HOLD` |

## Best Evaluation

- prefix_ticks: `25`
- k: `3`
- policy_onehot_scale: `5.0`
- pass_count: `4` / `5`

| seed | selected policy | selected status | score | track ratio | mean vx |
|---:|---|---|---:|---:|---:|
| `0` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `0.6666666666666666` | `0.3256336280421237` | `0.0260506902433699` |
| `1` | `iter25` | `PASS_CANDIDATE_SIM_GATE` | `0.6666666666666666` | `0.3566823099642837` | `0.028534584797142694` |
| `2` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `0.6666666666666666` | `0.327782184196379` | `0.02622257473571032` |
| `6` | `iter24` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `1.0` | `-0.5659199241796159` | `-0.04527359393436927` |
| `7` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `0.3437347055155138` | `0.02749877644124111` |

## Next

- Do not launch DR from this router.
- Inspect the missed seed/policy scores and either improve router features or move to recurrent policy class.
