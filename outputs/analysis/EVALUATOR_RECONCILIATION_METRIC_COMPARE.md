# Evaluator Velocity Metric Reconciliation

status: `PASS_EVALUATOR_CANONICAL`

This read-only comparison separates the BC-smoke flattened all-joint
velocity metric from the canonical strict gate's max-per-pitch-joint
velocity metric.

## Inputs

- bc_smoke_json: `outputs/analysis/source_vx_selector_trace_pitch_chain_limited_4p3_blend080_exact_onnx_fitted_bridge_bc_gate_x008_10s.json`
- canonical_json: `outputs/analysis/source_vx_selector_trace_pitch_chain_limited_4p3_blend080_exact_onnx_multiseed_fitted_backlash_summary.json`

## Summary

- BC smoke max flattened sent_vel95: `2.2237` rad/s
- canonical max pitch-joint sent_vel95: `4.2879` rad/s
- canonical max pitch tracking p95: `0.2794` rad

## BC Smoke Rows

| seed | status | samples | termination | flat_sent_vel95 | track95 | vx | ratio |
|---|---|---:|---|---:|---:|---:|---:|
| seed_000 | `PASS_ROLLOUT_COMPLETED` | 500 | `duration_complete` | 2.1444 | 0.1821 | 0.0505 | 0.6311 |
| seed_001 | `PASS_ROLLOUT_COMPLETED` | 500 | `duration_complete` | 2.2237 | 0.1837 | 0.0463 | 0.5789 |
| seed_002 | `PASS_ROLLOUT_COMPLETED` | 500 | `duration_complete` | 2.1754 | 0.1825 | 0.0522 | 0.6531 |
| seed_003 | `PASS_ROLLOUT_COMPLETED` | 500 | `duration_complete` | 2.1730 | 0.1820 | 0.0430 | 0.5380 |
| seed_004 | `PASS_ROLLOUT_COMPLETED` | 500 | `duration_complete` | 2.1444 | 0.1834 | 0.0491 | 0.6138 |
| seed_005 | `PASS_ROLLOUT_COMPLETED` | 500 | `duration_complete` | 2.1226 | 0.1818 | 0.0519 | 0.6482 |
| seed_006 | `PASS_ROLLOUT_COMPLETED` | 500 | `duration_complete` | 2.1939 | 0.1835 | 0.0444 | 0.5554 |
| seed_007 | `PASS_ROLLOUT_COMPLETED` | 500 | `duration_complete` | 2.1946 | 0.1838 | 0.0462 | 0.5774 |

## Canonical Rows

| seed | status | samples | termination | max_pitch_sent_vel95 | max_pitch_track95 | vx | ratio |
|---|---|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 4.2240 | 0.2719 | 0.0494 | 0.6171 |
| 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 4.2879 | 0.2794 | 0.0461 | 0.5759 |
| 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 4.2395 | 0.2743 | 0.0517 | 0.6464 |
| 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 4.1935 | 0.2685 | 0.0432 | 0.5394 |
| 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 4.2663 | 0.2721 | 0.0475 | 0.5933 |
| 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 4.2265 | 0.2719 | 0.0503 | 0.6290 |
| 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 4.2533 | 0.2762 | 0.0460 | 0.5755 |
| 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 4.2281 | 0.2737 | 0.0476 | 0.5954 |

## Decision

Use the canonical strict evaluator for promotion decisions. The BC
smoke metric is useful for quick replay debugging, but because it
flattens all joints and ticks it can mask a pitch-joint envelope
violation.

Gate result: `PASS_EVALUATOR_CANONICAL`
