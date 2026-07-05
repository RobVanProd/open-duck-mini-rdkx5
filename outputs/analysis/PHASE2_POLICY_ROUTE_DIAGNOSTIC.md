# Phase 2 Policy Route Diagnostic

status: `PASS_ORACLE_ROUTE_EXISTS`

## Executive Summary

Existing deployable candidates are complementary across the compact z=0.0075 rough+push seeds. A validation-aware mixture/router diagnostic is evidence-aligned, but this is not deployable or trainable evidence by itself.

This is an offline/read-only diagnostic. It did not train, SSH, deploy, run robot tests, change runtime behavior, or run grounded replay.

## Candidate Pass Matrix

| candidate | status | pass/total | passing seeds | max velocity excess |
|---|---|---:|---|---:|
| `policy/candidates/phase2_z0075_iter24_live_oracle_seed2_active_history_context_rate150_20260704/candidate.onnx` | `HOLD_ITER24_LIVE_ORACLE_SEED6_REGRESSION` | `4/5` | `0,1,2,7` | `0.0` |
| `policy/candidates/phase2_z0075_iter25_dual_anchor_weight4_history_context_rate150_20260704/candidate.onnx` | `HOLD_ITER25_DUAL_ANCHOR_REGRESSES_SEEDS0_7` | `3/5` | `1,2,6` | `0.0` |
| `policy/candidates/phase2_z0075_iter26_dual_anchor_weight2_history_context_rate150_20260704/candidate.onnx` | `HOLD_ITER26_DUAL_ANCHOR_WEIGHT2_BROAD_REGRESSION` | `1/5` | `6` | `0.0` |
| `policy/candidates/phase2_z0075_iter27_live_oracle_seed6_active_history_context_rate150_20260705/candidate.onnx` | `HOLD_ITER27_LIVE_ORACLE_MULTI_SEED_REGRESSION` | `2/5` | `0,1` | `0.0` |

## Oracle Seed-Level Route

- required seeds: `[0, 1, 2, 6, 7]`
- covered seeds: `[0, 1, 2, 6, 7]`
- missing seeds: `[]`
- oracle_covers_gate: `True`

| seed | routed candidate | samples | track ratio | mean vx | tracking p95 | velocity excess |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `policy/candidates/phase2_z0075_iter27_live_oracle_seed6_active_history_context_rate150_20260705/candidate.onnx` | `750` | `0.3395` | `0.0272` | `0.1848` | `0.0` |
| 1 | `policy/candidates/phase2_z0075_iter27_live_oracle_seed6_active_history_context_rate150_20260705/candidate.onnx` | `750` | `0.383` | `0.0306` | `0.1843` | `0.0` |
| 2 | `policy/candidates/phase2_z0075_iter24_live_oracle_seed2_active_history_context_rate150_20260704/candidate.onnx` | `750` | `0.3278` | `0.0262` | `None` | `0.0` |
| 6 | `policy/candidates/phase2_z0075_iter26_dual_anchor_weight2_history_context_rate150_20260704/candidate.onnx` | `750` | `0.3491` | `0.0279` | `None` | `0.0` |
| 7 | `policy/candidates/phase2_z0075_iter24_live_oracle_seed2_active_history_context_rate150_20260704/candidate.onnx` | `750` | `0.3437` | `0.0275` | `None` | `0.0` |

## Decision

- Build an offline router/mixture diagnostic that chooses among these candidates from observation/history, not seed id.
- Gate the router on the same z=0.0075 rough+push compact screen before any PPO/DR launch.
- If the router clears the compact gate, use its rollouts to define the trainable behavior-preservation target.
- If no observation-based router clears the compact gate, skip mixture routing and move to recurrent/hidden-state training.

This diagnostic does not reopen Phase 2 DR training by itself. It only says whether a router/mixture branch has an oracle upper bound worth testing.
