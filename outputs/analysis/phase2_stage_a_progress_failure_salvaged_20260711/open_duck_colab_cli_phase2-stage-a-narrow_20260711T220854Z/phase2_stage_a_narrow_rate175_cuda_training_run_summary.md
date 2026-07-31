# Training Run Summary

status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
generated_at: `2026-07-11T22:26:11Z`
run_dir: `/content/open_duck_training_phase2_stage_a_narrow_cli/smoke_20260711T220911Z_gpu`

## Run

- platform: `gpu`
- returncode: `0`
- elapsed_s: `1020.114166125`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `-0.04`
- non_deployable: `True`

## Latest ONNX

- path: `/content/open_duck_training_phase2_stage_a_narrow_cli/smoke_20260711T220911Z_gpu/2026_07_11_222542_245760.onnx`
- step: `245760`
- sha256: `962f88bcbc172b8ffe137d83809431e229c26e4b2df7cfd58c76921d243960ad`
- size_bytes: `884094`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 8.680524 | 20.482655 |
| 81920 | 13.202709 | 25.405594 |
| 163840 | 15.080274 | 27.087536 |
| 245760 | 13.837126 | 25.696161 |

## ONNX Exports

| step | file | sha256 |
|---:|---|---|
| 81920 | `2026_07_11_222151_81920.onnx` | `a081ae77f76c96d455dffed8f12a033d77529fb6d9e0fe6849ae9813bd3a4f7a` |
| 163840 | `2026_07_11_222513_163840.onnx` | `ac53a70d210c857738ff99a6c911351848247651d806acdf01df6586e426df84` |
| 245760 | `2026_07_11_222542_245760.onnx` | `962f88bcbc172b8ffe137d83809431e229c26e4b2df7cfd58c76921d243960ad` |

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
