# Training Run Summary

status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
generated_at: `2026-07-02T23:08:04Z`
run_dir: `/content/open_duck_training_phase2_z0025_boundary_cli/smoke_20260702T225504Z_gpu`

## Run

- platform: `gpu`
- returncode: `0`
- elapsed_s: `780.0531860479999`
- actuator_bridge_enabled: `True`
- target_rate_scale: `-0.005`
- actuator_tracking_scale: `-0.005`
- non_deployable: `True`

## Latest ONNX

- path: `/content/open_duck_training_phase2_z0025_boundary_cli/smoke_20260702T225504Z_gpu/2026_07_02_230734_122880.onnx`
- step: `122880`
- sha256: `36f236cef8bdd709249801d0d47d7e7281b86bcce7ca5cfe59813b316fce9a01`
- size_bytes: `884094`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 30.275702 | 27.652386 |
| 40960 | 35.050522 | 29.245630 |
| 81920 | 39.130035 | 30.617146 |
| 122880 | 39.373680 | 30.526350 |

## ONNX Exports

| step | file | sha256 |
|---:|---|---|
| 40960 | `2026_07_02_230416_40960.onnx` | `05148a0c556542d898393365a31ab4ce43e84e0440c0883302e7fd3f9635c0d4` |
| 81920 | `2026_07_02_230713_81920.onnx` | `2413e72fe998fee194570dde5fcf50438cfa72b30e1f9a6492749d3ebcee8d53` |
| 122880 | `2026_07_02_230734_122880.onnx` | `36f236cef8bdd709249801d0d47d7e7281b86bcce7ca5cfe59813b316fce9a01` |

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
