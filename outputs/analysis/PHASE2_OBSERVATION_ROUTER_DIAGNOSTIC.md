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
| `50` | `3` | `0.0` | `4/5` | `HOLD` |
| `50` | `3` | `1.0` | `4/5` | `HOLD` |
| `50` | `3` | `5.0` | `4/5` | `HOLD` |
| `100` | `3` | `0.0` | `4/5` | `HOLD` |
| `100` | `3` | `1.0` | `4/5` | `HOLD` |
| `100` | `3` | `5.0` | `4/5` | `HOLD` |
| `200` | `3` | `0.0` | `3/5` | `HOLD` |
| `200` | `3` | `1.0` | `3/5` | `HOLD` |
| `200` | `3` | `5.0` | `3/5` | `HOLD` |

## Best Evaluation

- prefix_ticks: `100`
- k: `3`
- policy_onehot_scale: `5.0`
- pass_count: `4` / `5`

| seed | selected policy | selected status | score | track ratio | mean vx |
|---:|---|---|---:|---:|---:|
| `0` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `0.3256336280421237` | `0.0260506902433699` |
| `1` | `iter25` | `PASS_CANDIDATE_SIM_GATE` | `0.7380391135430341` | `0.3566823099642837` | `0.028534584797142694` |
| `2` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `0.327782184196379` | `0.02622257473571032` |
| `6` | `iter27` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.7268402531931905` | `0.9697169494164626` | `0.07757735595331701` |
| `7` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `0.3437347055155138` | `0.02749877644124111` |

## Missed Seed Details

These rows show why the offline router is not promotable as a deployable online wrapper yet. Scores are computed without seed ID.

### Seed `6`

| policy | selected score | pass | status | track ratio |
|---|---:|---|---|---:|
| `iter24` | `0.7188176838069882` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `-0.5659199241796159` |
| `iter25` | `0.7245902223395962` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.32731479393599633` |
| `iter26` | `0.0` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.3491434641809368` |
| `iter27` | `0.7268402531931905` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.9697169494164626` |

## Next

- Do not launch DR from this router.
- Inspect the missed seed/policy scores and either improve router features or move to recurrent policy class.
