# Robust Actuator Fit Check

status: `CEILING_STILL_SUPPORTED`

## Summary

The actuator response fit was rerun with robust grid-search selection metrics to
test whether stale-but-finite servo read outliers were biasing the fitted
velocity ceiling downward.

Result: robust selection did **not** raise the fitted pitch-chain velocity
limits. The hard-ceiling hypothesis remains alive.

## Input

Primary telemetry:

```text
outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds.jsonl
```

Comparison telemetry:

```text
outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x0_after_wire_routing.jsonl
```

## Selection Comparison

| selection metric | delay range | tau range | velocity-limit range |
|---|---:|---:|---:|
| original RMSE | `[3, 3]` | `[0.02, 0.02]` | `[2.25, 3.75]` |
| trimmed RMSE 95 | `[3, 3]` | `[0.02, 0.02]` | `[2.50, 3.50]` |
| p95 absolute error | `[3, 3]` | `[0.02, 0.02]` | `[2.25, 3.25]` |

Per-joint velocity-limit selections:

| joint | RMSE | trimmed RMSE 95 | p95 abs error |
|---|---:|---:|---:|
| left_hip_pitch | 2.50 | 2.50 | 2.50 |
| left_knee | 3.50 | 3.50 | 3.25 |
| left_ankle | 3.00 | 3.00 | 3.25 |
| right_hip_pitch | 3.75 | 3.50 | 3.00 |
| right_knee | 3.00 | 3.50 | 2.75 |
| right_ankle | 2.25 | 2.50 | 2.25 |

## Runtime Read-Error Path

The current `rustypot_position_hwi.py` wrapper retries reads up to eight times.
If all retries fail, `get_present_positions()` and `get_present_velocities()`
return `None`; they do not intentionally hold the last good value. Dropped
`None` samples are skipped by the fit.

Successful retry-after-error samples still return finite servo data, so a
stale-but-finite value could only enter through the lower rustypot/servo layer.
The robust refit above is the practical check for whether such contamination is
dominating the parameter selection.

## Interpretation

If RMSE contamination had been strongly biasing the fit downward, robust
selection should have moved the velocity limits higher. It did not. The fitted
range remains in roughly the same `2.25-3.75 rad/s` band, with robust variants
at `2.25-3.50 rad/s`.

This supports keeping the actuator ceiling as a real constraint while still
tracking CRC/read errors as a watch item.

## Follow-Up

The next missing experiment is the command feasibility curve:

```bash
python3 tools/analyze_command_feasibility_curve.py \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --commands 0,0.02,0.04,0.06,0.08,0.10,0.12 \
  --duration 5 \
  --bridge-mode fitted \
  --jax-platform cpu \
  --run
```

On CUDA/A100, use the same tool with `--jax-platform gpu` inside the Colab
runtime. Robot validation remains blocked.
