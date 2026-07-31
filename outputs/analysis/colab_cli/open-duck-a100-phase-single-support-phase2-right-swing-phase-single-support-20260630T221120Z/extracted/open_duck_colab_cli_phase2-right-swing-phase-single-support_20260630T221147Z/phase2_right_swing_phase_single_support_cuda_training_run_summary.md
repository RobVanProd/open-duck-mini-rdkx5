# Training Run Summary

status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
generated_at: `2026-06-30T22:26:48Z`
run_dir: `/content/open_duck_training_phase2_right_swing_phase_single_support_cli/smoke_20260630T221506Z_gpu`

## Run

- platform: `gpu`
- returncode: `0`
- elapsed_s: `701.7753684260001`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `-0.005`
- non_deployable: `True`

## Latest ONNX

- path: `/content/open_duck_training_phase2_right_swing_phase_single_support_cli/smoke_20260630T221506Z_gpu/2026_06_30_222630_122880.onnx`
- step: `122880`
- sha256: `cafacac915603b92171367e68a52f3857a834f19c8228a237fc508c40ccd9345`
- size_bytes: `884094`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 38.849014 | 35.500565 |
| 40960 | 47.109398 | 36.095852 |
| 81920 | 46.142708 | 36.355061 |
| 122880 | 51.538673 | 35.404919 |

## ONNX Exports

| step | file | sha256 |
|---:|---|---|
| 40960 | `2026_06_30_222327_40960.onnx` | `e5817dc7f4e3e89d55c2faf855d38c172273afbb6c4685ec430d9e395fe35a3d` |
| 81920 | `2026_06_30_222609_81920.onnx` | `a613b6a923a56a4124557297e9418497bc4aa5adadf7ff794a4cd0c085bcaccb` |
| 122880 | `2026_06_30_222630_122880.onnx` | `cafacac915603b92171367e68a52f3857a834f19c8228a237fc508c40ccd9345` |

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
