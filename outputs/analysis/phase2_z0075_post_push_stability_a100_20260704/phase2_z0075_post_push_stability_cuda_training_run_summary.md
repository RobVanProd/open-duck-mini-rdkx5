# Training Run Summary

status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
generated_at: `2026-07-04T04:41:42Z`
run_dir: `/content/open_duck_training_phase2_b0g_cli/smoke_20260704T042912Z_gpu`

## Run

- platform: `gpu`
- returncode: `0`
- elapsed_s: `750.0473559039999`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `-0.012`
- non_deployable: `True`

## Latest ONNX

- path: `/content/open_duck_training_phase2_b0g_cli/smoke_20260704T042912Z_gpu/2026_07_04_044055_122880.onnx`
- step: `122880`
- sha256: `c45569a28f1af792ca193dab5405711362fc08e5bc2899b6634bf924270b63f3`
- size_bytes: `884094`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 27.856071 | 34.057766 |
| 40960 | 49.390709 | 42.381115 |
| 81920 | 42.612938 | 41.857956 |
| 122880 | 50.525616 | 40.323391 |

## ONNX Exports

| step | file | sha256 |
|---:|---|---|
| 40960 | `2026_07_04_043749_40960.onnx` | `7186ca3f08984275847ed3cd86fa55d630da821475c47f057fd7c3f50072051f` |
| 81920 | `2026_07_04_044034_81920.onnx` | `5a852ae5638235d387722af5c39b7a422ad416b624bfcf0aa907610a207410bf` |
| 122880 | `2026_07_04_044055_122880.onnx` | `c45569a28f1af792ca193dab5405711362fc08e5bc2899b6634bf924270b63f3` |

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
