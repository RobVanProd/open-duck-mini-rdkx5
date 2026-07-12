# Training Run Summary

status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
generated_at: `2026-07-12T00:02:01Z`
run_dir: `/content/open_duck_training_phase2_stage_a_narrow_cli/smoke_20260711T234701Z_gpu`

## Run

- platform: `gpu`
- returncode: `0`
- elapsed_s: `900.104076113`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `-0.04`
- non_deployable: `True`

## Latest ONNX

- path: `/content/open_duck_training_phase2_stage_a_narrow_cli/smoke_20260711T234701Z_gpu/2026_07_12_000115_245760.onnx`
- step: `245760`
- sha256: `4f835e675fb706736007cb1ed87f2d4c9907b400742a0c1143cfe9c0d0414e21`
- size_bytes: `884094`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 42.402145 | 39.365124 |
| 81920 | 56.692348 | 36.250233 |
| 163840 | 57.806660 | 37.775360 |
| 245760 | 56.904541 | 38.160740 |

## ONNX Exports

| step | file | sha256 |
|---:|---|---|
| 81920 | `2026_07_11_235724_81920.onnx` | `2f4ec1d364456f4e757414fc2ca64786503abf600e458b2e593ad16d9e603deb` |
| 163840 | `2026_07_12_000047_163840.onnx` | `f091e8729559cd178a871760584eec402c9b76c84c5e98e61ff2287bf69b0fa1` |
| 245760 | `2026_07_12_000115_245760.onnx` | `4f835e675fb706736007cb1ed87f2d4c9907b400742a0c1143cfe9c0d0414e21` |

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
