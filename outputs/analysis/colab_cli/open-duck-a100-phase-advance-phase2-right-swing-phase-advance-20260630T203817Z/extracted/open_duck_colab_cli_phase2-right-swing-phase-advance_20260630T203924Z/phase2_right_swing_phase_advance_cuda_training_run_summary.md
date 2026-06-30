# Training Run Summary

status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
generated_at: `2026-06-30T20:55:29Z`
run_dir: `/content/open_duck_training_phase2_right_swing_phase_advance_cli/smoke_20260630T204251Z_gpu`

## Run

- platform: `gpu`
- returncode: `0`
- elapsed_s: `758.0028027070002`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `-0.005`
- non_deployable: `True`

## Latest ONNX

- path: `/content/open_duck_training_phase2_right_swing_phase_advance_cli/smoke_20260630T204251Z_gpu/2026_06_30_205511_122880.onnx`
- step: `122880`
- sha256: `752916e306d4ecd96d0c5c4a3be57fd1ed4099d8a973e015ef4942c7c2edfb31`
- size_bytes: `884094`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 38.670044 | 34.962597 |
| 40960 | 46.834911 | 36.571381 |
| 81920 | 47.226364 | 36.248383 |
| 122880 | 51.418755 | 35.520245 |

## ONNX Exports

| step | file | sha256 |
|---:|---|---|
| 40960 | `2026_06_30_205154_40960.onnx` | `28454c887b963c4939319bdc83a4a0032b75e8fbc336b4840738e802355b07d1` |
| 81920 | `2026_06_30_205450_81920.onnx` | `3e50c3c87dbbd6f1b94c8cb8c1118781a88b4c8ce08fd7ea4cc942d7e2ba4d3b` |
| 122880 | `2026_06_30_205511_122880.onnx` | `752916e306d4ecd96d0c5c4a3be57fd1ed4099d8a973e015ef4942c7c2edfb31` |

## Warning Lines

Actionable warning/error-like stderr lines found: `0`
Known benign/log-noise stderr lines found: `1`

| known noise category | count |
|---|---:|
| `absl_preinit` | 1 |

No actionable warning/error-like stderr lines found.

## Next Gate

Use `tools/package_candidate_policy.py` on the latest ONNX only after
the run is intended as a candidate and the required sim-gate evidence
exists. This summary does not approve robot testing.
