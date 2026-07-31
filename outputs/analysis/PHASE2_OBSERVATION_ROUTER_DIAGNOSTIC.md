# Phase 2 Observation Router Diagnostic

status: `PASS_OBSERVATION_ROUTER_OFFLINE`

## Executive Summary

A leave-one-seed-out observation/history router can select passing candidates for all compact z=0.0075 rough+push seeds in this offline trace diagnostic. This supports building a real closed-loop router gate next.

This is offline analysis only. It did not train, SSH, deploy, run robot tests, change runtime behavior, or run grounded replay. Seed ID is not used as a feature.

## Evaluations

| prefix ticks | k | policy onehot scale | pitch guard scale | pass/total | result |
|---:|---:|---:|---:|---:|---|
| `1` | `3` | `0.0` | `0.0` | `4/5` | `HOLD` |
| `1` | `3` | `0.0` | `1.0` | `4/5` | `HOLD` |
| `1` | `3` | `1.0` | `0.0` | `4/5` | `HOLD` |
| `1` | `3` | `1.0` | `1.0` | `4/5` | `HOLD` |
| `1` | `3` | `5.0` | `0.0` | `4/5` | `HOLD` |
| `1` | `3` | `5.0` | `1.0` | `4/5` | `HOLD` |
| `5` | `3` | `0.0` | `0.0` | `4/5` | `HOLD` |
| `5` | `3` | `0.0` | `1.0` | `4/5` | `HOLD` |
| `5` | `3` | `1.0` | `0.0` | `4/5` | `HOLD` |
| `5` | `3` | `1.0` | `1.0` | `4/5` | `HOLD` |
| `5` | `3` | `5.0` | `0.0` | `4/5` | `HOLD` |
| `5` | `3` | `5.0` | `1.0` | `4/5` | `HOLD` |
| `25` | `3` | `0.0` | `0.0` | `4/5` | `HOLD` |
| `25` | `3` | `0.0` | `1.0` | `4/5` | `HOLD` |
| `25` | `3` | `1.0` | `0.0` | `4/5` | `HOLD` |
| `25` | `3` | `1.0` | `1.0` | `4/5` | `HOLD` |
| `25` | `3` | `5.0` | `0.0` | `4/5` | `HOLD` |
| `25` | `3` | `5.0` | `1.0` | `4/5` | `HOLD` |
| `50` | `3` | `0.0` | `0.0` | `4/5` | `HOLD` |
| `50` | `3` | `0.0` | `1.0` | `4/5` | `HOLD` |
| `50` | `3` | `1.0` | `0.0` | `4/5` | `HOLD` |
| `50` | `3` | `1.0` | `1.0` | `4/5` | `HOLD` |
| `50` | `3` | `5.0` | `0.0` | `4/5` | `HOLD` |
| `50` | `3` | `5.0` | `1.0` | `4/5` | `HOLD` |
| `100` | `3` | `0.0` | `0.0` | `4/5` | `HOLD` |
| `100` | `3` | `0.0` | `1.0` | `5/5` | `PASS` |
| `100` | `3` | `1.0` | `0.0` | `4/5` | `HOLD` |
| `100` | `3` | `1.0` | `1.0` | `5/5` | `PASS` |
| `100` | `3` | `5.0` | `0.0` | `4/5` | `HOLD` |
| `100` | `3` | `5.0` | `1.0` | `5/5` | `PASS` |
| `200` | `3` | `0.0` | `0.0` | `3/5` | `HOLD` |
| `200` | `3` | `0.0` | `1.0` | `2/5` | `HOLD` |
| `200` | `3` | `1.0` | `0.0` | `3/5` | `HOLD` |
| `200` | `3` | `1.0` | `1.0` | `2/5` | `HOLD` |
| `200` | `3` | `5.0` | `0.0` | `3/5` | `HOLD` |
| `200` | `3` | `5.0` | `1.0` | `2/5` | `HOLD` |

## Best Evaluation

- prefix_ticks: `100`
- k: `3`
- policy_onehot_scale: `5.0`
- pitch_guard_scale: `1.0`
- pitch_guard_limit_rad: `0.2`
- pass_count: `5` / `5`

| seed | selected policy | selected status | score | adjusted score | pitch excess | track ratio | mean vx |
|---:|---|---|---:|---:|---:|---:|---:|
| `0` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `1.0` | `0.0` | `0.3256336280421237` | `0.0260506902433699` |
| `1` | `iter25` | `PASS_CANDIDATE_SIM_GATE` | `0.7380391135430341` | `0.7236758902194371` | `0.014363223323596908` | `0.3566823099642837` | `0.028534584797142694` |
| `2` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `1.0` | `0.0` | `0.327782184196379` | `0.02622257473571032` |
| `6` | `iter25` | `PASS_CANDIDATE_SIM_GATE` | `0.7245902223395962` | `0.7024264504397564` | `0.022163771899839924` | `0.32731479393599633` | `0.026185183514879706` |
| `7` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `1.0` | `0.0` | `0.3437347055155138` | `0.02749877644124111` |

## Next

- Implement an eval-only router wrapper that chooses among candidate policies online without seed id.
- Gate the router on the canonical z=0.0075 rough+push compact screen.
- Only if the router gate passes, generate trainable behavior-preservation rollouts for Phase 2 DR.
