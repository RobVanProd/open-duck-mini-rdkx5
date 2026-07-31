# Training Run Summary

status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
generated_at: `2026-06-29T19:06:23Z`
run_dir: `/content/open_duck_training_phase2_z005_support_cli/smoke_20260629T184953Z_gpu`

## Run

- platform: `gpu`
- returncode: `0`
- elapsed_s: `990.27934026`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `-0.01`
- non_deployable: `True`

## Latest ONNX

- path: `/content/open_duck_training_phase2_z005_support_cli/smoke_20260629T184953Z_gpu/2026_06_29_190550_122880.onnx`
- step: `122880`
- sha256: `59f1ba30516e3019eef9c324304883ae37d69316e0a9469d136d87493ac6ce12`
- size_bytes: `884094`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 24.411722 | 25.393875 |
| 40960 | 32.146736 | 27.939310 |
| 81920 | 32.249718 | 28.580282 |
| 122880 | 36.603050 | 28.471169 |

## ONNX Exports

| step | file | sha256 |
|---:|---|---|
| 40960 | `2026_06_29_190108_40960.onnx` | `05931e5d5cf2b6230ff404f580b0d68a804d0c2c9c9aa726bd546b776e979c92` |
| 81920 | `2026_06_29_190508_81920.onnx` | `49ba524b35d470d9a03d9ed25ee039495f6a8d44489e0488a3e05a044004abcc` |
| 122880 | `2026_06_29_190550_122880.onnx` | `59f1ba30516e3019eef9c324304883ae37d69316e0a9469d136d87493ac6ce12` |

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
